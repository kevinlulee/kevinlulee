from pprint import pprint
from kevinlulee import fdfind

# 2025-04-14 aicmp: move dirs as a param and also map the results with re.sub to remove the ending /.git/?
def collect_git_directories():
    return fdfind(
        dirs=['~/'],
        query=".git",
        only_directories=True,
        include_dirs=[".git"],
    )

