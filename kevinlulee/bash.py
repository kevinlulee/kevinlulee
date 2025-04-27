from typing import List, Union
import os

import re
from pprint import pprint
from typing import List, Optional
import os
from pathlib import Path

from kevinlulee.ao import to_array
from kevinlulee.module_utils import get_modname_from_file
from kevinlulee.string_utils import split
from kevinlulee.ao import join_spaces

from .file_utils import find_git_directory, find_project_root
from .base import display
from .validation import empty
import subprocess

from typing import TypedDict

def bash(*args, cwd=None, on_error=None, silent=True, debug = False, strict = False, shell = False):
    cwd = os.path.expanduser(cwd) if cwd else None
    s = join_spaces(args)
    if debug:
        return print('[DEBUG]', s)
    cmd = s if shell else s.split(' ')
    result = subprocess.run(cmd, text=True, cwd=cwd, capture_output=True, shell = shell, check = True)

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
        module_path = get_modname_from_file(file)
        cwd = '~/projects/python'
        if module_path:
            display(module_path = module_path, cwd = cwd)
            return bash("python3", "-m", module_path, *args, cwd=cwd, on_error=on_error, silent=False)
        else:
            print('could not find a module_path for the current file')
    else:
        return bash("python3", file, *args, on_error=on_error, silent=False)


if __name__ == '__main__':
    pass
    # bash('python3 -m kevinlulee.experiments.foobar')
