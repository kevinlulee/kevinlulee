from kevinlulee import readfile, join_text, clip, fd, each
from kevinlulee.module_utils import get_file_from_modname, get_modname_from_file

def clip_directory_contents(dir):
    """
    finds all files in a directory via fd
    reads them and joins them together
    """

    files = fd(dir)

    def runner(file):
        bar = "=" * 50
        return file, readfile(file), bar

    return join_text(runner(file) for file in files if file)
