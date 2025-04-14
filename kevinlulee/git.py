import os
import re
import textwrap
from .bash import bash

def trim_lines(s):
    return [line.strip() for line in s.splitlines()]

class HistoryData:
    def get_history(self):
        cmd = ["log", "--numstat", "--date=iso", "--pretty=format:%H|%an|%ad|%s"]
        result = self.cmd(*cmd)

        commits = []
        commit = None

        for line in result.splitlines():
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

                    deletions = 0 if deletions == '-' else int(deletions)
                    insertions = 0 if insertions == '-' else int(insertions)

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
    def get_files(self, filter='*'):
        s = self.cmd('status')
        changes = []

        # Untracked files
        untracked_match = re.search(r'Untracked files:\n.*?\n((?:\s{4}.+\n)+)', s)
        if untracked_match:
            untracked = [line.strip() for line in untracked_match.group(1).splitlines()]
            changes.extend({
                'status': 'created',
                'file': os.path.abspath(os.path.join(self.cwd, f))
            } for f in untracked)

        # Modified, deleted, renamed
        matches = re.findall(r'^\s*(modified|deleted|renamed):\s+(.+)', s, re.MULTILINE)
        changes.extend({
            'status': status,
            'file': os.path.abspath(os.path.join(self.cwd, f.strip()))
        } for status, f in matches)

        if filter == '*':
            return changes

        return [c for c in changes if c['status'] == filter]




class GitRepo(HistoryData, StatusData):
    def is_git_directory(self):
        return os.path.isdir(os.path.join(self.cwd, ".git"))
    def diff(self, *files):
        return self.cmd('diff', *files)
    def on_error(self, err):
        return err
    def cmd(self, *args):
        return bash('git', *args, cwd = self.cwd, debug = self.debug, silent=True, on_error = self.on_error)

    def __init__(self, cwd):
        self.cwd = os.path.expanduser(cwd)
        self.debug = False
        self.commands = GitCommands(self)

    def init(self):
        return self.cmd('init')

    def add(self, *args):
        return self.cmd('add', *args)

    def push(self, remote, branch):
        return self.cmd('push', remote, branch)

    def commit(self, message):
        return self.cmd('commit', '-m', message)

    def create_branch(self, branch_name):
        return self.cmd('branch', branch_name)

    def checkout(self, branch_name):
        return self.cmd('checkout', branch_name)

    @property
    def branch(self):
        return self.cmd('branch', '--show-current')

    @property
    def symbolic_full_name(self):
        a = self.cmd('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}')
        if 'fatal' in a:
            return 
        return a
    @property
    def remote(self):
        m = self.symbolic_full_name
        if m:
            return m.split('/')[0]
    @property
    def status(self):
        return self.cmd('status')
    @property
    def branches(self):
        output = self.cmd('branch').replace('*', '')
        return trim_lines(output)

    @property
    def remotes(self):
        output = self.cmd('remote')
        return trim_lines(output)

    @property
    def url(self):
        remote_name = 'origin'
        output = self.cmd('remote', "get-url", remote_name)
        return output

    def create_remote(self, name, url):
        self.cmd('remote', 'add', name, url)

    @property
    def username(self):
        return self.cmd('config', 'user.name')

    def is_clean(self):
        return 'nothing to commit, working tree clean' in self.status

    def has_remote_repository(self):
        r = 'repository not found|permission denied'
        return not re.search(r, self.cmd('ls-remote', self.url), flags = re.I)


class GitCommands:
    def __init__(self, repo: GitRepo):
        self.repo = repo

    def implicitly_create_remote(self):
        if 'origin' in self.repo.remotes:
            return 
        repo = os.path.basename(re.sub('/$', '', self.repo.cwd))
        username = self.repo.username
        return self.repo.cmd('remote', 'add', 'origin', f'git@github.com:{username}/{repo}.git')

    def push_to_origin(self):

        remote = 'origin'

        remotes = self.repo.remotes
        if remote not in remotes:
            self.implicitly_create_remote()

        return self.repo.cmd('push', 'origin')

    def commit_all(self, m = 'autocommit'):
        repo = self.repo
        if repo.is_clean():
            return 

        repo.add('.')
        return repo.commit(m)
