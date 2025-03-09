import subprocess
import re
from typing import List, Optional
import os


def fix(success, error):
    bash_error_success_patterns = [
        {
            "regex": "^hint",
            "spacing": " ",
        },
        {
            "regex": "^Switched to branch '(\w+)'$",
            "spacing": " ",
        },
        {
            "regex": "^To github",
            "spacing": "",
        },
        {
            "regex": "^Previous HEAD",
            "spacing": "",
        },
        {
            "regex": "^Note:",
            "spacing": " ",
        },
        {
            "regex": "^ Cloning:",
            "spacing": " ",
        },
        {
            "regex": "^grep:",
            "spacing": " ",
        },
        {
            "regex": "^HEAD",
            "spacing": "\n",
        },
    ]

    if not error:
        return success
    if error == success:
        return success

    for pattern in bash_error_success_patterns:
        if re.search(pattern.get("regex"), success):
            success += pattern.get("spacing") + error

            return success.strip().replace("\t", "    ")
    raise Exception(error)


def bash(*args, cwd=None):
    cwd = os.path.expanduser(cwd) if cwd else None
    cmd = list(args)

    if 'log' in cmd:
        return subprocess.check_output(cmd, text=True, cwd=cwd).strip()

    cmd = ' '.join(args)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    success, error = process.communicate()
    success = success.decode("utf-8").strip()
    error = error.decode("utf-8").strip()
    success = fix(success, error)
    return success


def ripgrep(
    *directories: str,
    pattern: str = ".",
    respect_gitignore: bool = False,
    follow_symlinks: bool = False,
    hidden: bool = False,
    case_insensitive: bool = True,
    multiline: bool = False,
    respect_ignore_file: bool = True,
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

    # Add options based on arguments
    if not respect_ignore_file:
        cmd.append("--no-ignore")
    elif not respect_gitignore:
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

    return result.stdout.splitlines()


def fdfind(
    *directories: str,
    pattern: str = ".",
    respect_gitignore: bool = False,
    respect_ignore: bool = True,
    show_hidden_files: bool = False,
) -> List[str]:
    """
    A Python wrapper for the `fdfind` command.

    Args:
        *directories (str): Directories to search (splat operator for multiple directories).
        pattern (str): The search pattern (default is "." to match all files).
                       - If the pattern contains a backslash (`\`), it is treated as a regex.
                       - If the pattern contains an asterisk (`*`), it is treated as a glob.
                       - Otherwise, it is treated as a fixed string.
        respect_gitignore (bool): Whether to respect `.gitignore` files (default is False).
        respect_ignore (bool): Whether to respect `.ignore` files (default is True).
        show_hidden_files (bool): Whether to include hidden files (default is False).

    Returns:
        List[str]: A list of file paths matching the search criteria.
    """
    # Base command
    cmd = ["fdfind"]

    # Determine pattern type
    if "\\" in pattern:
        cmd.extend(["--regex", pattern])  # Treat as regex
    elif "*" in pattern:
        cmd.extend(["--glob", pattern])  # Treat as glob
    else:
        cmd.extend(["--fixed-strings", pattern])  # Treat as fixed string

    # Add directories
    directories = [os.path.expanduser(d) for d in directories]
    cmd.extend(directories)

    # Add options based on arguments
    if not respect_gitignore:
        cmd.append("--no-ignore-vcs")
    if not respect_ignore:
        cmd.append("--no-ignore")
    if show_hidden_files:
        cmd.append("--hidden")

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        raise RuntimeError(f"fdfind failed with error: {result.stderr}")

    return result.stdout.splitlines()

