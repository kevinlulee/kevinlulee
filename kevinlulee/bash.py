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
