import os
import subprocess
from typing import List, Union, TypedDict

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
    "trash",
    "scratch",
    "github",
]

class RipgrepLine(TypedDict):
    path: str
    lnum: int
    excerpt: str

def parse_ripgrep_line(line: str) -> RipgrepLine:
    parts = line.split(":", 2)
    if len(parts) != 3:
        return {}

    path, lnum_str, excerpt = parts
    try:
        lnum = int(lnum_str)
    except ValueError:
        return {}

    return {"path": path, "lnum": lnum, "excerpt": excerpt.strip()}

def ripgrep(
    pattern: str = ".",
    dirs: list = ['.'],
    respect_gitignore: bool = False,
    follow_symlinks: bool = False,
    hidden: bool = False,
    case_insensitive: bool = True,
    multiline: bool = False,
    ignore_file: str = '',
    respect_ignore_file: bool = True,
    show_lnum: bool = True,
) -> List[RipgrepLine]:
    cmd = ["rg"]
    if show_lnum:
        cmd.append("--line-number")

    assert isinstance(dirs, (list, tuple)), "dirs must be an array"
    if ignore_file:
        cmd += ["--ignore-file", os.path.expanduser(ignore_file)]
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

    cmd.append(pattern)

    dirs = [os.path.expanduser(d) for d in dirs]
    cmd.extend(dirs)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode > 1:
        raise RuntimeError(f"rg failed with error: {result.stderr}")

    lines = result.stdout.splitlines()
    return [parse_ripgrep_line(s) for s in lines if parse_ripgrep_line(s)]

def fdfind(
    dirs: list = ["~/"],
    query: str = ".",
    exclude_dirs: List[str] = [],
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
    exclude_dirs = set(GLOBAL_COMMON_IGNORE_DIRS + exclude_dirs or [])
    include_dirs = set(include_dirs or [])

    # Exclude patterns (minus those in include list)
    final_ignores = exclude_dirs - include_dirs
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


if __name__ == '__main__':
    print(ripgrep(pattern='def group', dirs = ['/home/kdog3682/projects/python/kevinlulee/kevinlulee/']))
