import os
import textwrap
from .bash import bash

def trim_lines(s):
    return [line.strip() for line in s.splitlines()]

class GitRepo:
    def is_git_directory(self):
        return os.path.isdir(os.path.join(self.cwd, ".git"))
    def diff(self):
        return self.cmd('diff')
    def cmd(self, *args):
        return bash('git', *args, cwd = self.cwd, debug = self.debug)

    def __init__(self, cwd):
        self.cwd = os.path.expanduser(cwd)
        self.debug = False

    def init(self):
        self.cmd('init')

    def add(self, *args):
        self.cmd('add', *args)

    def push(self, remote, branch):
        self.cmd('push', remote, branch)

    def commit(self, message):
        # message = textwrap.wrap(message, width = 60)
        self.cmd('commit', '-m', message)

    def create_branch(self, branch_name):
        self.cmd('branch', branch_name)

    def checkout(self, branch_name):
        self.cmd('checkout', branch_name)

    @property
    def branch(self):
        return self.cmd('branch', '--show-current')

    @property
    def branches(self):
        output = self.cmd('branch').replace('*', '')
        return trim_lines(output)

    @property
    def remote(self):
        output = self.cmd('remote')
        return trim_lines(output)

    @property
    def url(self):
        remote_name = 'origin'
        output = self.cmd('remote', "get-url", remote_name)
        return output
    @property
    def remotes(self):
        output = self.cmd('remote')
        return trim_lines(output)

    def create_remote(self, name, url):
        self.cmd('remote', 'add', name, url)

    @property
    def username(self):
        return self.cmd('git', 'config', 'user.name')
