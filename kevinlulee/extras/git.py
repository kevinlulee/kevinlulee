from __future__ import annotations
import kevinlulee as kx

import os
import re
import json
import subprocess
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

    BranchType = Literal["feature", "bug", "hotfix", "refactor", "docs", "test"]


class GitCommandError(Exception):
    pass


class Status:
    def __init__(self, repo: GitRepo):
        self.repo = repo
        self._load()

    def _load(self):
        self.modified: list[str] = []
        self.created: list[str] = []
        self.deleted: list[str] = []

        for line in self.repo.run("status", "--porcelain", lines=True):
            if len(line) < 3:
                continue
            code, path = line[:2], line[3:]
            if "?" in code or "A" in code:
                self.created.append(path)
            if "M" in code:
                self.modified.append(path)
            if "D" in code:
                self.deleted.append(path)

    @property
    def files(self) -> list[str]:
        return self.modified + self.created + self.deleted

    @property
    def staged(self) -> list[str]:
        return self.repo.run("diff", "--cached", "--name-only", lines=True)

    @property
    def is_clean(self) -> bool:
        return not self.files

    @property
    def has_staged(self) -> bool:
        return bool(self.staged)


class Commit:
    def __init__(self, repo: GitRepo, ref: str):
        self.repo = repo
        self.ref = ref

    @cached_property
    def sha(self) -> str:
        return self.repo.run("rev-parse", "--verify", self.ref)

    @cached_property
    def short_sha(self) -> str:
        return self.sha[:7]

    @cached_property
    def message(self) -> str:
        return self.repo.run("log", "-1", "--pretty=%B", self.ref)

    @cached_property
    def author(self) -> str:
        return self.repo.run("log", "-1", "--pretty=%an", self.ref)

    @cached_property
    def timestamp(self) -> int:
        return int(self.repo.run("log", "-1", "--format=%ct", self.ref))

    @cached_property
    def files(self) -> list[str]:
        lines = self.repo.run("show", "--name-only", "--pretty=format:", self.ref, lines=True)
        return [f for f in lines if f]

    def show(self, file: str | None = None) -> str:
        if file:
            rel = self.repo.relative_path(file)
            return self.repo.run("show", f"{self.ref}:{rel}")
        return self.repo.run("show", self.ref)

    def parent(self) -> Commit:
        return Commit(self.repo, f"{self.ref}~1")

    def restore(self, file: str) -> str:
        return self.repo.run("checkout", self.ref, "--", file)


class GitRepo:
    def __init__(self, directory: str):
        self.cwd = os.path.expanduser(directory)

    def run(self, *args, lines=False, check=True) -> str | list[str]:
        cmd = ["git"] + [a for a in args if a is not None]
        result = subprocess.run(
            cmd,
            cwd=self.cwd,
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            raise GitCommandError(result.stderr.strip())

        output = result.stdout.strip()
        if lines:
            return [ln.strip() for ln in output.splitlines() if ln.strip()]
        return output

    def run_ok(self, *args) -> bool:
        try:
            self.run(*args)
            return True
        except GitCommandError:
            return False

    # --- properties ---

    @property
    def branch(self) -> str:
        return self.run("branch", "--show-current")

    @property
    def branches(self) -> list[str]:
        return self.run("branch", lines=True)

    @property
    def remotes(self) -> list[str]:
        return self.run("remote", "-v", lines=True)

    @property
    def remote_url(self) -> str:
        return self.run("remote", "get-url", "origin")

    @property
    def head(self) -> Commit:
        return Commit(self, "HEAD")

    @property
    def status(self) -> Status:
        return Status(self)

    @property
    def is_repo(self) -> bool:
        return os.path.isdir(os.path.join(self.cwd, ".git"))

    # --- basic operations ---

    def init(self) -> str:
        return self.run("init")

    def add(self, *files: str) -> str:
        targets = files or (".",)
        return self.run("add", *targets)

    def commit(self, message: str = "auto-commit") -> Commit | None:
        if self.status.is_clean:
            return None
        output = self.run("commit", "-m", message)
        sha = re.search(r"\[[\w-]+ ([a-f0-9]+)\]", output)
        return Commit(self, sha.group(1)) if sha else None

    def push(self, remote: str = "origin", branch: str | None = None) -> str:
        branch = branch or self.branch
        needs_upstream = not self.run_ok(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
        )
        if needs_upstream:
            return self.run("push", "-u", remote, branch)
        return self.run("push", remote, branch)

    def pull(self, remote: str = "origin", branch: str | None = None) -> str:
        branch = branch or self.branch
        return self.run("pull", remote, branch)

    def fetch(self, remote: str = "origin") -> str:
        return self.run("fetch", remote)

    # --- branches ---

    def checkout(self, branch: str) -> str:
        return self.run("checkout", branch)

    def create_branch(self, name: str) -> str:
        return self.run("switch", "-c", name)

    def delete_branch(self, name: str, force: bool = False) -> str:
        flag = "-D" if force else "-d"
        return self.run("branch", flag, name)

    # --- history ---

    def log(self, n: int = 10) -> list[str]:
        return self.run("log", f"-{n}", "--oneline", lines=True)

    def diff(self, *files: str, staged: bool = False) -> str:
        args = ["diff"]
        if staged:
            args.append("--cached")
        if files:
            args.extend(files)
        return self.run(*args)

    def reset(self, ref: str = "HEAD~1", mode: str = "mixed") -> str:
        return self.run("reset", f"--{mode}", ref)

    # --- paths ---

    def relative_path(self, path: str) -> str:
        path = os.path.expanduser(path)
        if os.path.isabs(path):
            return os.path.relpath(path, self.cwd)
        return path

    def absolute_path(self, path: str) -> str:
        return os.path.join(self.cwd, path)


class GitHubRepo:
    def __init__(self, repo: GitRepo, token: str):
        self._repo = repo
        self._token = token
        self._gh = None
        self._remote = None

    @property
    def gh(self):
        if self._gh is None:
            from github import Github
            self._gh = Github(self._token)
        return self._gh

    @property
    def owner(self) -> str:
        return self._repo.run("config", "user.name")

    @property
    def name(self) -> str:
        return os.path.basename(self._repo.cwd)

    @property
    def remote(self):
        if self._remote is None:
            self._remote = self.gh.get_user().get_repo(self.name)
        return self._remote

    def create_remote(self, private: bool = False):
        user = self.gh.get_user()
        try:
            return user.get_repo(self.name)
        except Exception:
            return user.create_repo(self.name, private=private)

    def create_issue(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ):
        assignees = assignees or [self.owner]
        return self.remote.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees,
        )

    def create_pull_request(
        self,
        head: str,
        base: str,
        title: str,
        body: str | None = None,
    ):
        return self.remote.create_pull(
            title=title,
            body=body or "",
            head=head,
            base=base,
        )

    def get_issue(self, number: int):
        return self.remote.get_issue(number)


class GitWorkflow:
    def __init__(self, repo: GitRepo, github: GitHubRepo | None = None):
        self.repo = repo
        self.github = github
        self.meta = BranchMeta(repo)

    def typed_branch(self, branch_type: BranchType, name: str, base: str | None = None) -> str:
        base = base or self.repo.branch
        branch_name = f"{branch_type}/{name}"
        self.repo.create_branch(branch_name)
        self.meta.set(branch_name, "base", base)
        return branch_name

    def get_base(self, branch: str | None = None) -> str | None:
        branch = branch or self.repo.branch
        return self.meta.get(branch, "base")

    def squash_merge(self, target: str | None = None, message: str | None = None) -> str:
        current = self.repo.branch
        target = target or self.get_base(current)
        if not target:
            raise ValueError("no target branch specified or found")
        
        self.repo.checkout(target)
        self.repo.run("merge", "--squash", current)
        msg = message or f"squash merge {current} into {target}"
        self.repo.commit(msg)
        return f"merged {current} into {target}"

    def typed_branch(self, branch_type: BranchType, name: str) -> str:
        branch_name = f"{branch_type}/{name}"
        return self.repo.create_branch(branch_name)

    def feature(self, name: str) -> str:
        return self.typed_branch("feature", name)

    def bugfix(self, name: str) -> str:
        return self.typed_branch("bug", name)

    def hotfix(self, name: str) -> str:
        return self.typed_branch("hotfix", name)

    def get_typed_branches(self, branch_type: BranchType) -> list[str]:
        prefix = f"{branch_type}/"
        return [b for b in self.repo.branches if prefix in b]

    # --- merge workflows ---

    def squash_commits(self, n: int, message: str | None = None) -> str:
        self.repo.reset(f"HEAD~{n}", mode="soft")
        msg = message or self.repo.head.message
        self.repo.run("commit", "-m", msg)
        return f"squashed {n} commits"

    # --- pr workflows ---

    def pr_for_issue(self, issue_number: int, base: str = "dev") -> str:
        if not self.github:
            raise ValueError("github not configured")

        head = self.repo.branch
        if head == base:
            raise ValueError(f"cannot PR from {head} to itself")

        self.repo.push()

        issue = self.github.get_issue(issue_number)
        title = f"{issue.title} (#{issue.number})"
        body = f"Fixes #{issue.number}"

        pr = self.github.create_pull_request(head, base, title, body)
        return pr.html_url

    # --- init workflows ---

    def init_project(self, private: bool = False) -> str:
        if not self.repo.is_repo:
            self.repo.init()

        gitignore = self.repo.absolute_path(".gitignore")
        if not os.path.exists(gitignore):
            kx.cp('~/dotfiles/templates/.gitignore', self.repo.cwd)

        self.repo.add()
        self.repo.commit("initial commit")

        if self.github:
            remote = self.github.create_remote(private=private)
            self.repo.run("remote", "add", "origin", remote.ssh_url)
            self.repo.push()

        return "project initialized"


class GitArchaeology:
    def __init__(self, repo: GitRepo):
        self.repo = repo

    def find_file(
        self,
        filename: str,
        content_pattern: str | None = None,
        limit: int = 100,
    ) -> Commit | None:
        args = ["log", "--all", "--full-history", "--format=%H", f"-{limit}", "--", f"**/{filename}"]
        commits = self.repo.run(*args, lines=True)

        for sha in commits:
            commit = Commit(self.repo, sha)
            matching = [f for f in commit.files if filename in f]
            if not matching:
                continue

            if content_pattern is None:
                return commit

            content = commit.show(matching[0])
            if content and re.search(content_pattern, content):
                return commit

        return None

    def restore_file(self, filename: str, content_pattern: str | None = None) -> str | None:
        commit = self.find_file(filename, content_pattern)
        if commit:
            matching = [f for f in commit.files if filename in f]
            if matching:
                return commit.restore(matching[0])
        return None

    def get_branch_origin(self, branch: str | None = None) -> str | None:
        branch = branch or self.repo.branch
        lines = self.repo.run("reflog", "show", branch, lines=True, check=False)
        if not lines:
            return None
        match = re.search(r"Created from (.+)$", lines[-1])
        return match.group(1) if match else None
import json

class BranchMeta:
    def __init__(self, repo: GitRepo):
        self.repo = repo
        self.path = os.path.join(repo.cwd, ".git", "branch-meta.json")

    def _load(self) -> dict:
        if os.path.exists(self.path):
            return json.load(open(self.path))
        return {}

    def _save(self, data: dict):
        json.dump(data, open(self.path, "w"), indent=2)

    def set(self, branch: str, key: str, value):
        data = self._load()
        data.setdefault(branch, {})[key] = value
        self._save(data)

    def get(self, branch: str, key: str, default=None):
        return self._load().get(branch, {}).get(key, default)

    def delete(self, branch: str):
        data = self._load()
        data.pop(branch, None)
        self._save(data)

    def prune(self):
        data = self._load()
        branches = set(self.repo.branches)
        pruned = {k: v for k, v in data.items() if k in branches}
        self._save(pruned)


if __name__ == "__main__":
    repo = GitRepo('~/projects/hammymathclass')
    # import kevinlulee as kx
    # github = GitHubRepo(repo, token)
    # g = GitWorkflow(repo)
    print(repo.branch)
    # g.meta.set(g.repo.branch, 'dev')
    # kx.pretty_print(kx.readfile(g.meta.path))


