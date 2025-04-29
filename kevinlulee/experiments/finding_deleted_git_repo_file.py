from kevinlulee import GitRepo, clip, each
from pprint import pprint
import re
import os
from datetime import datetime


def save(**kwargs):
    pprint(kwargs)
    # clip(kwargs)
    


repo = GitRepo('~/projects/typst/mathematical/')
convex_files = repo.get_historical_files('convex')

def callback(file):
    commits = repo.get_file_commits(file)
    return div(file, div(commits))

def get_text(commit, file):
    return repo.commands.show(commit, file)

# payload = each(convex_files, callback)
