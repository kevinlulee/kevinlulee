import os
import json
import re
import textwrap

from kevinlulee.string_utils import split
from .bash import bash
from .ao import filtered
from dotenv import load_dotenv
import os
DEFAULT_REMOTE_NAME = 'origin'
def trim_lines(s):
    return [line.strip() for line in s.splitlines()]


class HistoryData:
    def get_history(self):
        cmd = [
            "log",
            "--numstat",
            "--date=iso",
            "--pretty=format:%H|%an|%ad|%s",
        ]
        result = self.log_cmd(*cmd)

        commits = []
        commit = None

        for line in result:
            commit_match = re.search(r"^(\w+)\|(.*?)\|(.*?)\|(.*)$", line)
            if commit_match:
                if commit:
                    commits.append(commit)
                commit = {
                    "hash": commit_match.group(1),
                    "author": commit_match.group(2),
                    "date": commit_match.group(3),
                    "message": commit_match.group(4),
                    "files": [],
                }
            elif commit and line.strip():
                numstat_match = re.match(r"^(\d+|-)\s+(\d+|-)\s+(.+)$", line)
                if numstat_match:
                    insertions = numstat_match.group(1)
                    deletions = numstat_match.group(2)
                    filename = numstat_match.group(3)

                    deletions = 0 if deletions == "-" else int(deletions)
                    insertions = 0 if insertions == "-" else int(insertions)

                    file_entry = {
                        "filename": filename,
                        "deletions": deletions,
                        "insertions": insertions,
                    }

                    commit["files"].append(file_entry)

        if commit:
            commits.append(commit)

        return commits


class StatusData:
    def get_files(self, filter="*"):
        s = self.cmd("status")
        changes = []

        # Untracked files
        untracked_match = re.search(
            r"Untracked files:\n.*?\n((?:\s{4}.+\n)+)", s
        )
        if untracked_match:
            untracked = [
                line.strip() for line in untracked_match.group(1).splitlines()
            ]
            changes.extend(
                {
                    "status": "created",
                    "file": os.path.abspath(os.path.join(self.cwd, f)),
                }
                for f in untracked
            )

        # Modified, deleted, renamed
        matches = re.findall(
            r"^\s*(modified|deleted|renamed):\s+(.+)", s, re.MULTILINE
        )
        changes.extend(
            {
                "status": status,
                "file": os.path.abspath(os.path.join(self.cwd, f.strip())),
            }
            for status, f in matches
        )

        if filter == "*":
            return changes

        return [c for c in changes if c["status"] == filter]


class GitProperties:
    def get_commit_info(
        self,
        commit,
        hash=False,
        short_hash=False,
        author=True,
        author_date=True,
        committer=True,
        committer_date=True,
        subject=True,
        body=False,
        parent_hashes=False,
        refs=False,
        changed_files=False,
    ):
        """
        Dynamically retrieve commit information based on specified parameters.

        Args:
            repo: The repository object with cmd method
            commit: The commit identifier
            hash: Whether to get the full commit hash
            short_hash: Whether to get the abbreviated commit hash
            author: Whether to get author name and email
            author_date: Whether to get author date
            committer: Whether to get committer name and email
            committer_date: Whether to get committer date
            subject: Whether to get commit subject/title
            body: Whether to get commit message body
            parent_hashes: Whether to get parent commit hashes
            refs: Whether to get associated references (tags, branches)
            changed_files: Whether to get the list of changed files

        Returns:
            A dictionary containing the requested commit information
        """
        # Define mappings for git format specifiers
        format_specs = {
            "hash": "%H",  # Full hash
            "short_hash": "%h",  # Short hash
            "author": "%an <%ae>",  # Author name and email
            "author_date": "%ai",  # Author date (ISO format)
            "committer": "%cn <%ce>",  # Committer name and email
            "committer_date": "%ci",  # Committer date (ISO format)
            "subject": "%s",  # Subject/title
            "body": "%b",  # Message body
            "parent_hashes": "%P",  # Parent hashes
            "refs": "%D",  # Refs (tags, branches)
        }

        # Build format string based on requested parameters
        format_parts = []
        params = {
            "hash": hash,
            "short_hash": short_hash,
            "author": author,
            "author_date": author_date,
            "committer": committer,
            "committer_date": committer_date,
            "subject": subject,
            "body": body,
            "parent_hashes": parent_hashes,
            "refs": refs,
        }

        for key, value in params.items():
            if value:
                format_parts.append(f"{key.upper()}:{format_specs[key]}%n")

        # If no valid parameters specified, return empty dict
        if not format_parts:
            return {}

        # Create format string
        format_string = "".join(format_parts)

        # Get commit information with a single command
        commit_output = self.cmd(
            "show", "-s", f"--format={format_string}", commit
        )

        # Add files changed if requested
        if changed_files:
            files_changed = self.cmd("show", "--name-only", "--format=", commit)

        # Parse the output into a dictionary
        result = {}
        current_key = None
        current_value = []

        for line in commit_output.splitlines():
            # Check if this line starts a new section
            is_header = False
            for key in params:
                if params[key] and line.startswith(f"{key.upper()}:"):
                    if current_key:
                        result[current_key] = (
                            "\n".join(current_value) if current_value else ""
                        )
                        current_value = []
                    current_key = key.lower()
                    current_value = [
                        line.split(":", 1)[1] if ":" in line else ""
                    ]
                    is_header = True
                    break

            if not is_header and current_key:
                current_value.append(line)

        # Add the last key
        if current_key and current_value:
            result[current_key] = "\n".join(current_value)

        # Add changed files if requested
        if changed_files:
            result["changed_files"] = files_changed

        return result

    def get_file_commits(self, target_file):
        return self.log_cmd("log", "--all", "--format=%H", "--", target_file)

    def get_historical_files(self, pattern=None):
        return list(set(self.log_cmd(
            "log", "--all", "--pretty=format:", "--name-only", pattern = pattern
        )))

    def log_cmd(self, *args, pattern = None):
        
        if 'log' not in args:
            args = ['log'] + list(args)
        all_files = self.cmd(*args).split('\n')
        matching_files = filtered(all_files, pattern)
        return matching_files


class GitRepo(HistoryData, StatusData, GitProperties):

    @property
    def address(self):
        url = self.url
        if url:
            return '/'.join(split(url, '/')[-2:])
    def is_git_directory(self):
        return os.path.isdir(os.path.join(self.cwd, ".git"))

    def diff(self, *files):
        return self.cmd("diff", *files)

    def on_error(self, err: str):
        if self.strict:
            raise Exception(err)
        self.errors.append(err)
        return err

    def cmd(self, *args, debug = False):
        return bash(
            "git",
            *args,
            cwd=self.cwd,
            debug=debug or self.debug,
            silent=True,
            on_error=self.on_error,
        )

    def __init__(self, cwd):
        self.cwd = os.path.expanduser(cwd)
        self.debug = False
        self.errors = []
        self.commands = GitCommands(self)
        self.strict = False

    def init(self):
        return self.cmd("init")

    @property
    def path(self):
        return self.cwd
    @property
    def name(self):
        return os.path.basename(self.cwd)

    def add(self, *args):
        return self.cmd("add", *args)

    def push(self, remote = DEFAULT_REMOTE_NAME, branch = None):
        return self.cmd("push", remote, branch)

    def commit(self, message):
        return self.cmd("commit", "-m", message)

    def create_branch(self, branch_name):
        return self.cmd("branch", '-M', branch_name)

    def checkout(self, branch_name):
        return self.cmd("checkout", branch_name)

    @property
    def branch(self):
        return self.cmd("branch", "--show-current")

    @property
    def symbolic_full_name(self):
        a = self.cmd(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
        )
        if "fatal" in a:
            return
        return a

    @property
    def remote(self):
        m = self.symbolic_full_name
        if m:
            return m.split("/")[0]

    @property
    def status(self):
        return self.cmd("status")

    @property
    def branches(self):
        output = self.cmd("branch").replace("*", "")
        return trim_lines(output)

    @property
    def remotes(self):
        output = self.cmd("remote")
        return trim_lines(output)

    @property
    def url(self):
        output = self.cmd("remote", "get-url", DEFAULT_REMOTE_NAME)
        return output

    def create_remote(self, name, url):
        self.cmd("remote", "add", name, url)

    @property
    def username(self):
        return self.cmd("config", "user.name")

    def is_clean(self):
        return self.cmd('status', '--porcelain') == ''
        return "nothing to commit, working tree clean" in self.status

    def has_remote_repository(self):
        r = "repository not found|permission denied"
        return not re.search(r, self.cmd("ls-remote", self.url), flags=re.I)


class GitCommands:

    def cmd(self, *args, **kwargs):
        return self.repo.cmd(*args, **kwargs)

    def set_remote(self, name = 'origin', apikey = None):
        if apikey == True:
            load_dotenv()
            NAME = self.repo.address.split('/')[0].upper()
            key = NAME + "_GITHUB_API_KEY"
            apikey = os.getenv(key)
            assert apikey != None, f"no implicit apikey for {key}"

        prefix = apikey or 'git'

        address = f'https://{prefix}@github.com/{self.repo.address}.git'
        args = [
            'remote', 'set-url', name, address
        ]
        return self.cmd(*args, debug = False)

    def show(self, commit, file = None):
        el = f'{commit}:{file}' if file else commit
        args = ['show', el]
        return self.repo.cmd(*args)
        
    def __init__(self, repo: GitRepo):
        self.repo = repo

    def implicitly_create_remote(self):
        if "origin" in self.repo.remotes:
            return
        repo = os.path.basename(re.sub("/$", "", self.repo.cwd))
        username = self.repo.username
        print(username)
        return self.repo.cmd(
            "remote", "add", "origin", f"git@github.com:{username}/{repo}.git"
        )

    def push_to_origin(self):
        remote = "origin"

        remotes = self.repo.remotes
        if remote not in remotes:
            self.implicitly_create_remote()

        # print(self.repo.username)
        # set_git_auth_token_if_author(self.repo)
        print(self.repo.cmd("push"))
        # return self.repo.cmd('push')

    def commit_all(self, m="autocommit"):
        repo = self.repo
        if repo.is_clean():
            return

        repo.add(".")
        return repo.commit(m)


if __name__ == '__main__':
    testing = True
    if testing:
        g = GitRepo('~/projects/python/kevinlulee/')
        # print(g.create_branch('dev'))
        # print(g.branch)
        g.debug = False

        # res = g.commands.set_remote(apikey=True)
        # print(res)
        # print(g.commands.commit_all())
        # print(g.commands.commit_all())
        # print(g.status)
        # print(g.push())
