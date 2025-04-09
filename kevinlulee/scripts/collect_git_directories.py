from pprint import pprint
from kevinlulee import fdfind

def collect_git_directories():
    return fdfind(
        dirs=['~/'],
        query=".git",
        only_directories=True,
        include_dirs=[".git"],
    )
