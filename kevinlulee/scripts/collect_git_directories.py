from pprint import pprint
from kevinlulee import fdfind, myenv

def collect_git_directories():
    return fdfind(
        dirs=['~/'],
        query=".git",
        ignore_dirs=myenv("grep.directories.ignored"),
        only_directories=True,
        include_dirs=[".git"],
    )
