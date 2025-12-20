from __future__ import annotations
import kevinlulee as kx

"""
ephemeral_workspace.py

A small context manager for executing dynamically generated / temporary code
inside a controlled workspace.

What it does
------------
- Temporarily exposes a directory as a module workspace (adds it to sys.path)
- Optionally changes the current working directory (cwd) for the duration
- Restores all state on exit

Design notes
------------
- The workspace is treated as a *namespace* that may contain many modules
- No cleanup is performed here; lifecycle management belongs to the caller
- `cwd` defaults to True because dynamically generated code often assumes
  relative paths resolve from its root
- Paths are expanded and resolved explicitly for correctness and predictability

This file is intended to live in permanent, importable project code
(not inside the temporary workspace itself).
"""

from contextlib import contextmanager
from pathlib import Path
import os
import sys


@contextmanager
def ephemeral_workspace(root, *, cwd=True):
    """
    Execute code within a temporary module workspace.

    Parameters
    ----------
    root : str or Path
        Directory that should be treated as the workspace root.
        This directory may contain one or more Python modules.
    cwd : bool, default=True
        If True, temporarily change the current working directory to `root`.

    Effects during the context
    --------------------------
    - `root` is added to the front of `sys.path`
    - Optionally sets the process working directory to `root`

    All changes are reverted on exit.
    """
    root = Path(root).expanduser().resolve()
    root_str = str(root)

    # Track prior state
    old_cwd = None
    path_added = False

    try:
        # Expose modules
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
            path_added = True

        # Change working directory if requested
        if cwd:
            old_cwd = Path.cwd()
            os.chdir(root)

        yield

    finally:
        # Restore cwd
        if old_cwd is not None:
            os.chdir(old_cwd)

        # Restore import path
        if path_added and root_str in sys.path:
            sys.path.remove(root_str)


__all__ = ['ephemeral_workspace']
