from typing import List
import os

import re
from pprint import pprint
from typing import List, Optional
import os
from pathlib import Path

from kevinlulee.string_utils import split

from .file_utils import find_git_directory, find_project_root
from .base import display
from .validation import empty
import subprocess

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


def ripgrep(
    *directories: str,
    pattern: str = ".",
    respect_gitignore: bool = False,
    follow_symlinks: bool = False,
    hidden: bool = False,
    case_insensitive: bool = True,
    multiline: bool = False,
    ignore_file: str = None,
    respect_ignore_file: bool = True,
    show_lnum: bool = True,
) -> List[str]:
    """
    A Python wrapper for the `rg` (ripgrep) command.

    Args:
        *directories (str): Directories to search (splat operator for multiple directories).
        pattern (str): The search pattern (default is "." to match all files, effectively listing all files).
        respect_gitignore (bool): Whether to respect `.gitignore` files (default is True).
        follow_symlinks (bool): Whether to follow symbolic links (default is False).
        hidden (bool): Whether to include hidden files (default is False).
        case_insensitive (bool): Whether to perform case-insensitive search (default is False).
        multiline (bool): Whether to enable multiline search (default is False).
        respect_ignore_file (bool): Whether to respect ignore files like .gitignore or .ignore (default is True).

    Returns:
        List[str]: A list of file paths and matching lines. Each element is a line of rg output.
    """
    # Base command
    cmd = ["rg"]
    if show_lnum:
        cmd.append("--line-number")  # <-- Add this line

    # Add options based on arguments
    if ignore_file:
        cmd.append("--ignore-file")
        cmd.append(ignore_file)
    elif not respect_ignore_file:
        cmd.append("--no-ignore")

    if not respect_gitignore:
        cmd.append("--no-ignore-vcs")
    if follow_symlinks:
        cmd.append("--follow")
    if hidden:
        cmd.append("--hidden")
    if case_insensitive:
        cmd.append("--ignore-case")
    if multiline:
        cmd.append("--multiline")

    # Add pattern
    cmd.append(pattern)

    # Add directories
    directories = [os.path.expanduser(d) for d in directories]
    cmd.extend(directories)

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check for errors
    if result.returncode > 1:  # rg returns 1 if no matches are found, >1 for errors
        raise RuntimeError(f"rg failed with error: {result.stderr}")

    m = result.stdout.splitlines()
    return [parse_ripgrep_line(s) for s in m]


def parse_ripgrep_line(line: str) -> dict:
    """
    Parses a single line of ripgrep output into a dictionary with:
    - file: path to the file
    - lnum: line number (as int)
    - excerpt: the matching line text
    """
    parts = line.split(":", 2)  # split into [file, lnum, excerpt]
    if len(parts) != 3:
        return {}

    path, lnum_str, excerpt = parts
    try:
        lnum = int(lnum_str)
    except ValueError:
        return {}

    return {"path": path, "lnum": lnum, "excerpt": excerpt.strip()}


def fdfind(
    directories: list = ["~/"],
    query: str = ".",
    ignore_dirs: List[str] = None,
    include_dirs: List[str] = None,
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
    directories = [os.path.expanduser(d) for d in directories]
    cmd.extend(directories)

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
