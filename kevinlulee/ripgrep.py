import os
import subprocess
from typing import List, Union, TypedDict

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


if __name__ == '__main__':
    print(ripgrep(pattern='def group', dirs = ['/home/kdog3682/projects/python/kevinlulee/kevinlulee/']))
