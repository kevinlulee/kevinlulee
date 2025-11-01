from typing import List, Union
import os

import re
from pprint import pprint
from typing import List, Optional
import os
from pathlib import Path

from kevinlulee.ao import filtered, flat, to_array
from kevinlulee.module_utils import get_modname_from_file
from kevinlulee.string_utils import split, trimdent
from kevinlulee.ao import join_spaces

from .file_utils import (
    assert_file,
    ensure_directory_exists,
    find_git_directory,
    find_project_root,
    writefile,
)
from .base import display, identity
from .validation import empty, is_array
import subprocess

from typing import TypedDict


def bash(
    *args,
    cwd=None,
    on_error=None,
    silent=True,
    debug=False,
    strict=False,
    shell=False,
):
    cwd = os.path.expanduser(cwd) if cwd else None
    s = join_spaces(args)
    if debug:
        return print("[DEBUG]", s)
    cmd = s if shell else s.split(" ")
    result = subprocess.run(
        cmd, text=True, cwd=cwd, capture_output=True, shell=shell, check=True
    )

    err = result.stderr.strip()
    success = result.stdout.strip()
    print(err, success)

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


def bash2(
    *args,
    cwd=None,
    on_error=None,
    strict=False,
    verbose=False,
    debug=False,
    silent=None,
):
    if silent is not None:
        verbose = not silent
    cwd = os.path.expanduser(cwd) if cwd else None
    cmd = filtered(args)

    if debug:
        print(cmd)
        return
    try:
        result = subprocess.run(
            cmd, text=True, cwd=cwd, capture_output=True, check=True
        )
        stdout = result.stdout.strip()
        if verbose:
            print(stdout)
        return stdout
    except Exception as e:
        if on_error:
            return on_error(e)
        elif strict:
            raise e
        else:
            stdout = e.stdout.strip()
            stderr = e.stderr.strip()

            print("[STDOUT]", stdout)
            print("[STDERR]", stderr)




def python3(file, *args, as_module=False, on_error=None):
    if as_module:
        module_path = get_modname_from_file(file)
        cwd = "~/projects/python"
        if module_path:
            display(module_path=module_path, cwd=cwd)
            return bash(
                "python3",
                "-m",
                module_path,
                *args,
                cwd=cwd,
                on_error=on_error,
                silent=False,
            )
        else:
            print("could not find a module_path for the current file")
    else:
        return bash("python3", file, *args, on_error=on_error, silent=False)




def bash3(*args, cwd=None, on_error=None):
    """
    simplified version of bash
    no debugging
    no printing

    these parts need to be manually controlled
    """
    cwd = os.path.expanduser(cwd) if cwd else None
    cmd = filtered(args)

    try:
        result = subprocess.run(
            cmd, text=True, cwd=cwd, capture_output=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        if on_error:
            return on_error(e)
        raise e


def pip(key, cwd=None):
    return bash("pip", "install", key, "--break-system-packages", cwd=cwd)


def chmod(x):
    assert_file(x)
    return bash("sudo", "chmod", "755", x)


def bash_nvim(*args, cwd=None, on_error=identity, as_list = False, ignore_stderr = lambda x: False):
    cwd = os.path.expanduser(cwd) if cwd else None
    cmd = flat(args)
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=cwd
    )
    out, err = p.communicate()
    stdout, stderr = out.decode("utf-8").strip(), err.decode("utf-8").strip()
    # print((stdout, stderr))
    if stderr and not ignore_stderr(stderr):
        return on_error(stderr)
    if as_list:
        return [l.strip() for l in stdout.splitlines() if l.strip()]
    return stdout

def bash_shell(cmd, cwd = None):
    
    cmd = trimdent(" ".join(cmd) if is_array(cmd) else cmd)

    res = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )
    return res.stdout.strip()

def git_bash(*args, cwd=".", debug=False):
    args =[str(el) for el in flat(args)]

    if debug:
        return print(*args)

    r = subprocess.run(
        args, text=True, cwd=cwd, capture_output=True, check=True
    )
    return r.stdout.strip()

def typst(
    inpath,
    outpath="~/scratch/temp.pdf",
    open=False,
    mode="compile",
    on_error=identity,
):
    """
    params:
        inpath: the inpath typ file
        outpath: the outbound pdf file
        open: whether to open the created pdf (false)
        mode: `compile` or `watch` (compile)
    """

    inpath = os.path.expanduser(inpath)
    outpath = os.path.expanduser(outpath)
    ensure_directory_exists(outpath)

    open = "--open" if open else ""
    return bash_nvim(
        "typst", mode, inpath, outpath, open, "--root", "/", on_error=on_error
    )

def typst_file(s: str):
    path = writefile("~/scratch/temp.typ", trimdent(str(s)))
    typst(path, open = True)
    return path


