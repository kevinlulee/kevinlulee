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
    return os.path.splitext(path)[1].lstrip(".").lower()


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
        else:
            if mode == 'copy':
                shutil.copytree(src, dst)
                return 

    func(src, dst)


def cp(a, b):
    return _copy_or_move(a, b, 'copy')

def mv(a, b):
    return _copy_or_move(a, b, 'move')

from pathlib import Path
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def find_ancestor(
    start_path: Path | str,
    callback: Callable[[Path, str], Optional[T]],
) -> Optional[str]:
    path = Path(start_path).expanduser().absolute()
    current = path if path.is_dir() else path.parent
    home = Path.home()

    while True:
        parent = current.parent

        result = callback(current, parent)
        if result is not None:
            return str(result)

        # stop at home directory (no match)
        if current == home:
            return None

        # stop at filesystem root
        if parent == current:
            return None

        current = parent


from pathlib import Path
from typing import Iterable


STRUCTURAL_DIRS = {"frontend", "packages", "python", "typst"}

PYTHON_MARKERS = {
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
}

WEBDEV_MARKERS = {
    "package.json",
    "vite.config.ts",
    "next.config.js",
    "astro.config.mjs",
}

TYPST_MARKERS = {
    "typst.toml",
}


WEBDEV_FILETYPES = {"react", "typescript", "javascript"}


def has_any(directory: Path, markers: Iterable[str]) -> bool:
    return any((directory / m).exists() for m in markers)


def find_project_directory(path: Path, filetype: str) -> Path | None:
    """
    Find the nearest *project directory* containing `path`.

    A project directory is the smallest directory that explicitly declares
    itself as a project for the given filetype (via marker files).

    In a monorepo, this typically resolves to a leaf project rather than the
    workspace root.

    Returns None if no matching project is found.
    """
    start = path if path.is_dir() else path.parent

    def callback(current: Path, prev: Path):
        if current.name in STRUCTURAL_DIRS:
            return prev

        if filetype == "python":
            if has_any(current, PYTHON_MARKERS):
                return current

        elif filetype == "typst":
            if has_any(current, TYPST_MARKERS):
                return current

        elif filetype in WEBDEV_FILETYPES:
            if has_any(current, WEBDEV_MARKERS):
                return current

        return

    return find_ancestor(start, callback)


def find_project_root_directory(
    path: Path,
    *,
    candidates: Iterable[Path],
) -> Path | None:
    """
    Find the *project root directory* containing `path`.

    A project root directory is a higher-level workspace boundary, typically
    used to group multiple projects (e.g. a monorepo or personal projects
    directory).

    Unlike `find_project_directory`, the result here is expected to be broader
    in scope and may sit above several independent project directories.
    """
    expanded = {c.expanduser().resolve() for c in candidates}

    def callback(current: Path, prev: Path):
        if current.resolve() in expanded:
            return current
        return

    return find_ancestor(start, callback)

from pathlib import Path


def find_git_directory(path: Path) -> Path | None:
    """
    Find the nearest Git repository directory containing `path`.

    A Git directory is defined as the closest ancestor directory that contains
    a `.git` entry (directory or file).
    """

    def callback(current: Path, prev: Path):
        if (current / ".git").exists():
            return current

    return find_ancestor(path, callback)

__all__ = [
    "cp",
    "mv",
    "find_project_directory",
    "find_project_root_directory",
    "find_git_directory"
]
