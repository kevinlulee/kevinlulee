import os
from pathlib import Path
import shutil
from typing import Callable
import re
from kevinlulee.consts.file_types import EXTENSIONS


def _absdir(dir):
    dir = os.path.expanduser(dir)
    return [os.path.join(dir, path) for path in os.listdir(dir)]


def _get_extension(path):
    return os.path.splitext(path).lstrip(".").lower()


def _is_dir(path):
    return os.path.isdir(os.path.expanduser(path))


def _is_file(path):
    return os.path.isfile(os.path.expanduser(path))


def _looks_like_file(path):
    DOT_FILES_NAMES = [
        ".ignore",
        ".bashrc",
        ".vimrc",
        ".vim",
        ".env",
        "fish_history",
    ]
    name = os.path.basename(path)
    if name in DOT_FILES_NAMES:
        return name.lstrip(".")
    ext = _get_extension(name)

    if ext == name[1:]:
        return False
        # if .template is the name, and the ext is 'template'
        # this does not seem like a file path.

    return ext if ext in EXTENSIONS else None


def _ensure_directory_exists(path):
    path = os.path.expanduser(path)

    if _looks_like_file(path):
        path = os.path.dirname(path)

    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _copy_or_move(src_path, dst_path, mode = 'copy'):
    """
    a tentative _looks_like_file heuristic is used to determine
    what the destination is. the heuristic is based on whether or not
    the dst_path has an extension that is a known file extension (.py, .js, .skill)

    directories are greedily created.
    so one must be careful in passing in accurate dst_paths.

    we check for when the src is in the dst
    this necessarily implies that the dst is a sub_directory of the src.
    when this is the case, we need to skip over the dst
    because it doesnt make sense to copy the dst into the dst.

    """

    func = shutil.copy2 if mode == 'copy' else shutil.move
    src = os.path.expanduser(str(src_path))
    dst = os.path.expanduser(str(dst_path))

    valid_src = os.path.exists(src)
    as_file = os.path.isfile(src)

    if as_file:
        _ensure_directory_exists(dst)
        if not _looks_like_file(dst):
            # a directory was passed in. it needs to be normalized
            dst = os.path.join(dst, kx.os.path.basename(src))
    else:
        # make sure the base directory of the dst exists
        _ensure_directory_exists(os.path.basename(dst))

        if src in dst:
            # copying the source directory to within the directory
            paths = _absdir(src)
            for path in paths:
                if path == dst:
                    continue
                func(path, dst)

            return

    func(src, dst)


def cp(a, b):
    return _copy_or_move(a, b, 'copy')

def mv(a, b):
    return _copy_or_move(a, b, 'move')

def _find_parent_path(input_path, callback: Callable[Path, Path]) -> Path:
    """
    Traverses up the directory tree from input_path until callback returns a path
    """

    path = Path(input_path).expanduser()
    home = Path.home()
    count = 0
    max_iterations = 10

    if path.is_file():
        path = path.parent

    while path != home and count < max_iterations:
        result = callback(path)
        if result:
            return result

        parent = path.parent
        if parent == path:  # Reached root directory
            break
        path = parent
        count += 1

    return None

def find_parent_branch_directory(path, directory_name) -> str:
    """
    finds parent directories like ~/projects/maelstrom/.git
    the directory_name in this case would be '.git'
    """
    
    def callback(path: Path):
        candidate = path / directory_name
        if candidate._is_dir():
            return candidate

    return str(_find_parent_path(path, callback))

__all__ = [
    "cp",
    "mv",
    "find_parent_branch_directory"
]
