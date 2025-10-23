"""
this file currently doesnt work.
"""

import kevinlulee as kx
import re
import subprocess
from pathlib import Path
from typing import Union, Optional, Dict, Any
from dataclasses import dataclass

def parse_result(stdout: str):
    m = 'Successfully formatted stdin'
    if m in stdout:
        ansi_pattern = r'^\x1b\[[0-9;]*[a-zA-Z].+\n.+'
        return re.sub(ansi_pattern, '', stdout, flags = re.M).strip()

    return ''

def typstfmt(
    source: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    inplace: bool = False,
    config_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Format Typst code using typstfmt.

    Args:
        source: Either a string of Typst code or a path to a .typ file
        output: Optional output file path (only used if source is a file)
        inplace: If True, format the file in place (only used if source is a file)
        config: Optional path to configuration file

    Returns:
        FormatResult object containing success status and formatted code
    """


    cmd = ['typstfmt']

    if config_path is not None:
        cmd.extend(['--config-path', str(config_path)])

    result = subprocess.run(
        cmd,
        input=source.encode(),
        capture_output=True,
        text=False
    )

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()
    if stderr:
        kx.stop(stderr)
    return parse_result(stdout)
    
# Example usage:

import subprocess

def typstyle(text: str, max_width: int = 20, indent_width: int = 2) -> str:
    """
    Format Typst code using the `typstyle` CLI.

    Args:
        text: The Typst source to format.
        max_width: Maximum line width (default 20).
        indent_width: Spaces per indent level (default 2).

    Returns:
        The formatted Typst string, or '' if an error occurs (prints the error).
    """
    if not isinstance(text, str) or text == "":
        return ""

    binary_name = 'typstyle-aarch64-unknown-linux-gnu'
    cmd = kx.DLDIR + binary_name
    proc = subprocess.run(
        [cmd, "-l", str(max_width), "-t", str(indent_width), '--wrap-text'],
        input=text,
        text=True,
        capture_output=True,
        shell = True,
    )

    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        if err:
            print(err)
        else:
            print("typstyle failed with exit code", proc.returncode)
        return ""

    return proc.stdout


if __name__ == "__main__":
    code = "#let x                   = 5\n#let y=10"
    result = typstyle(code)
    kx.pretty_print(result)
    # doesnt work because the cli

    # this doesnt work
