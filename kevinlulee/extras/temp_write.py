"""
Temporary scratch-file utilities.
"""

import os
from contextlib import contextmanager
from kevinlulee.extras.mtime_cache import mtime_cache
import kevinlulee as kx

DEFAULT_SCRATCH_DIR = "~/SCRATCH/TEMP"


@contextmanager
def temp_write(root_dir=DEFAULT_SCRATCH_DIR, verbose = False, cache=False):
    """
    Context manager for writing temporary files under a scratch directory.

    Defaults:
    - root_dir: ~/SCRATCH/TEMP
        The directory under which all files are written.
        The directory itself is never removed.
    - cache: False

    Behavior:
    - Files are written relative to root_dir.
    - Only files written during this context are tracked.

    Cache semantics:
    - cache=False (default):
        * Files are always written.
        * Files written in this context are deleted on exit.
    - cache=True:
        * If a file exists and its mtime matches the persistent cache,
          the write is skipped.
        * No files are deleted on exit.

    Notes:
    - Paths passed to write() must be relative.
    - Directory creation and actual writes are handled by kx.writefile.
    - Content is normalized using kx.trimdent before writing.
    """
    root_dir = os.path.expanduser(root_dir)
    os.makedirs(root_dir, exist_ok=True)

    written = set()

    with mtime_cache() as mcache:

        def write(relative_path, content):
            assert not os.path.isabs(relative_path), (
                "write() expects a relative path"
            )

            path = os.path.join(root_dir, relative_path)

            if cache and mcache.has(path):
                if verbose:
                    print(f'returning cache: {path}')
                return path

            pretty = kx.trimdent(content)
            kx.writefile(path, pretty, verbose = verbose)

            mcache.update(path)
            written.add(path)

            return path

        try:
            yield write
        finally:
            if not cache:
                for path in written:
                    try:
                        os.remove(path)
                    except FileNotFoundError:
                        pass

__all__ = ["temp_write"]
