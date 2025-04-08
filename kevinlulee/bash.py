from typing import List, Union
import os

import re
from pprint import pprint
from typing import List, Optional
import os
from pathlib import Path

from kevinlulee.ao import to_array
from kevinlulee.string_utils import split

from .file_utils import find_git_directory, find_project_root
from .base import display
from .validation import empty
import subprocess

from typing import TypedDict

class RipgrepLine(TypedDict):
    path: str
    lnum: int
    excerpt: str


GLOBAL_COMMON_IGNORE_DIRS = [
    ".config",
    ".local",
    ".cache",
    ".vim",
    ".vscode",
    ".rustup",
    ".cargo",
    ".bun",
    ".deno",
    ".dotnet",
    ".gnupg",
    ".pki",
    ".scalac",
    ".ssh",
    ".npm",
    ".fzf",
    ".venv",
    ".github",
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "dist",
    "build",
]

def bash(*args, cwd=None, on_error=None, silent=True, debug = False, strict = False):
    cwd = os.path.expanduser(cwd) if cwd else None
    args = [a for arg in args if (a := str(arg).strip())]
    if debug:
        return print('[DEBUG]', ' '.join(args))
    result = subprocess.run(args, text=True, cwd=cwd, capture_output=True)

    err = result.stderr.strip()
    success = result.stdout.strip()

    if success and not silent:
        print(success)

    if err and result.returncode:
            
        if on_error:
            return on_error(err)
        elif strict:
            raise err
        else:
            print(err)
            return err

    return success






def fdfind(
    dirs: list = ["~/"],
    query: str = ".",
    ignore_dirs: List[str] = [],
    include_dirs: List[str] = [],
    respect_gitignore: bool = False,
    respect_ignore: bool = False,
    show_hidden_files: bool = True,
    only_directories: bool = False,
    ignore_file: str = None,
    debug=False,
) -> List[str]:
    """
    A Python wrapper for the `fdfind` command.

    Args:
        directories (list): Directories to search.
        query (str): Search pattern (default is "." to match all files).
        ignore_dirs (List[str]): Directories or glob patterns to ignore.
        include_dirs (List[str]): Directories or patterns to force-include (overrides ignore).
        respect_gitignore (bool): Whether to respect .gitignore files.
        respect_ignore (bool): Whether to respect .ignore files.
        show_hidden_files (bool): Whether to include hidden files.
        only_directories (bool): Whether to search for directories only.

    Returns:
        List[str]: A list of paths matching the search criteria.
    """
    cmd = ["fdfind"]

    # Pattern handling
    if "*" in query:
        cmd.extend(["--glob", query])
    else:
        cmd.extend(["--fixed-strings", query])
    # Search directories
    dirs = [os.path.expanduser(d) for d in dirs]
    cmd.extend(dirs)

    # Normalize ignore/include lists
    ignore_dirs = set(GLOBAL_COMMON_IGNORE_DIRS + ignore_dirs or [])
    include_dirs = set(include_dirs or [])

    # Exclude patterns (minus those in include list)
    final_ignores = ignore_dirs - include_dirs
    for query in final_ignores:
        cmd.extend(["--exclude", query])

    if not respect_gitignore:
        cmd.append("--no-ignore-vcs")
    if not respect_ignore:
        cmd.append("--no-ignore")
    if show_hidden_files:
        cmd.append("--hidden")
    if only_directories:
        cmd.extend(["--type", "directory"])

    if debug:
        print(" ".join(cmd))
        return

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"""
            input: {' '.join(cmd)}
            ------------------------
            fdfind failed with error: {result.stderr}
        """
        )

    return result.stdout.splitlines()


def typst(inpath=None, outpath=None, open=False, mode="compile", on_error = None):
    """
    params:
        inpath: the inpath typ file
        outpath: the outbound pdf file
        open: whether to open the created pdf (false)
        mode: `compile` or `watch` (compile)
    """

    inpath = os.path.expanduser(inpath)
    outpath = os.path.expanduser(outpath)

    open = "--open" if open else ""
    return bash("typst", mode, inpath, outpath, open, "--root", "/", on_error=on_error)


def python3(file, *args, as_module=False, on_error = None):
    if as_module:
        cwd = find_project_root(file)
        if not cwd:
            return bash("python3", file, *args, on_error=on_error, silent=False)
        abs_path = Path(file).resolve()
        relative_path = abs_path.relative_to(cwd).with_suffix("")
        module_path = ".".join(relative_path.parts)
        display(module_path = module_path, cwd = cwd)
        return bash("python3", "-m", module_path, *args, cwd=cwd, on_error=on_error, silent=False)
    else:
        return bash("python3", file, *args, on_error=on_error, silent=False)



