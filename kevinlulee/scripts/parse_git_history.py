from pprint import pprint
import subprocess
import re
import os
from kevinlulee import GitRepo
from kevinlulee.date_utils import strftime
from kevinlulee.file_utils import writefile

if __name__ == '__main__':
    path = "/home/kdog3682/projects/old_projects/VSCodeExtensions/qwe-jump/"
    repo = GitRepo(path)
    # repo.debug = True
    # pprint(repo.get_history())
    # print(repo.cmd('remote', '-v'))
    # git remote add origin https://github.com/your-username/your-repo.git

    # repo.

    # print(repo.remotes)
    # print(repo.commands.implicitly_create_remote())
    # writefile(os.path.join(repo.cwd, 'hi.txt'), strftime(mode = 'timestamp'))
    # print(repo.cwd)
    # print(repo.remote)
    # print(repo.url)
    # print('hi', )
    # print(repo.remote, repo.remotes)
    # pprint(parse_git_history(path))
    # print(repo.commands.safety_commit())
    # message = repo.commands.push_to_origin()
    # print(message)

