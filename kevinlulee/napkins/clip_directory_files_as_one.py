from kevinlulee import readfile, join_text, clip, fd, ensure_directory
from kevinlulee.file_utils import find_git_directory

def clip_directory_files_as_one(dir, git = True):
    """
    finds all files in a directory via fd
    reads them and joins them together
    """

    dir = find_git_directory(dir) if git else ensure_directory(dir) 
    files = fd(dir)

    def show(file):
        bar = "=" * 50
        return (file, readfile(file), bar)

    payload = join_text(each(files, show))
    clip(payload)
