from kevinlulee import readfile, join_text, clip, fd, each
from kevinlulee.module_utils import get_file_from_modname, get_modname_from_file

def clip_directory_contents(dir):
    """
    finds all files in a directory via fd
    reads them and joins them together

    useful when you forget where a function is
    and want to look through all the text files

    for example, i lost track of where loadspec was.
    """

    files = fd(dir)

    def runner(file):
        bar = "=" * 50
        return file, readfile(file), bar

    payload = join_text(runner(file) for file in files if file)
    clip(payload)


def generate_import_all_file_from_directory_files(dir):
    s = join_text(get_modname_from_file(file) for file in fd(dir))
    return s
