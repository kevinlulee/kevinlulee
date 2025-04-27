from os.path import isdir
from pathlib import Path
import sys
from typing import Union
import re
from pprint import pprint
import os
import importlib

from kevinlulee.file_utils import get_extension
from kevinlulee.string_utils import matchstr

from pathlib import Path
import os



def collect_python_paths():
    home = os.path.expanduser("~/")
    paths = sys.path
    store = []
    exclude = re.compile(r"site-packages|\.(?:cache|local)")
    for path in paths:
        if path not in store and home in path and not re.search(exclude, path):
            store.append(re.sub("/$", "", path))
    return store


PYTHON_MODULE_PATHS = collect_python_paths()


def get_modname_from_file(file):
    if not file.endswith(".py"):
        return file

    path = os.path.expanduser(file)
    for root in PYTHON_MODULE_PATHS:
        m = path.replace(root, "")
        if len(m) < len(path):
            b = m
            b = b[1:] if b[0] == "/" else b
            b = b.replace("/__init__", "")
            b = b.replace("/__main__", "")
            b = b.replace(".py", "").replace("/", ".")
            a = re.search("\w+", b).group(0)
            if b.startswith(a + "." + a):
                return b[len(a) + 1 :]
            return b


def get_file_from_modname(modname):
    if not modname:
        return

    if modname.endswith(".py") and os.path.exists(os.path.expanduser(modname)):
        return os.path.expanduser(modname)

    suffix = modname.replace(".", "/")
    for root in PYTHON_MODULE_PATHS:
        candidate = os.path.join(root, suffix + ".py")
        if os.path.isfile(candidate):
            return candidate

        candidate = os.path.join(root, suffix)
        if os.path.isdir(candidate):
            p = os.path.join(candidate, "__init__.py")
            if os.path.isfile(p):
                print(p)
                return p
            else:
                return candidate


def delete_module(key):
    key = get_modname_from_file(key)
    if key in sys.modules:
        del sys.modules[key]
        return True


def get_modname(x: Union["path", "package_name"]):
    return (
        get_modname_from_file(x) if os.path.exists(os.path.expanduser(x)) else x
    )


def reload_module(key):
    return importlib.reload(get_modname_from_file(key))


def load_module(key, reload=False):
    key = get_modname_from_file(key)

    if reload:
        if key in sys.modules:
            del sys.modules[key]
    return __import__(key, fromlist=(key.split(".")))


def load_func(module, func=None):
    if not func:
        if isinstance(module, str) and "." in module:
            func = module.split(".")[-1]
        else:
            raise Exception("func is needed")
    return getattr(load_module(module), func, None)



def get_module(file_name: str, reload = False, from_anywhere = False):
    """
    if from_anywhere, gets a module from anywhere. does not need to be on path
    """
    if not file_name:
        return 

    module_name = file_name.replace(os.sep, ".").replace(".py", "")

    if reload and module_name in sys.modules:
        del sys.modules[module_name]

    if from_anywhere:
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        return __import__(module_name, fromlist=(module_name.split(".")))
        
if __name__ == "__main__":
    # this is super cool
    #
    load_func('kevinlulee.scripts.generate_pytypst_funcs')('abc')
    # print(PYTHON_MODULE_PATHS)
    # print(get_modname_and_cwd('/home/kdog3682/projects/python/kevinlulee/kevinlulee/experiments/abc.py'))
