
from kevinlulee import GitRepo, clip, each
from pprint import pprint
import re
import os
from datetime import datetime


def save(**kwargs):
    pprint(kwargs)
    # clip(kwargs)
    
a = GitRepo('~/projects/typst/mathematical/')

convex_files = a.get_historical_files('convex')
file = convex_files[0]
commits = a.get_file_commits(file)

a.strict = True
for commit in commits:
    print('commit', commit)
    try:
        r = a.cmd('show', commit, file)
        clip(r)
        break
    except Exception as e:
        print('err', e)
        pass
# c = commits[0]
# data = a.get_commit_info(c)
#
#
# save(convex_files = convex_files, commits = commits, data = data)
