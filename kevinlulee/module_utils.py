from os.path import isdir
from pathlib import Path
import sys
from typing import Union
import re
from pprint import pprint
import os
import importlib

from kevinlulee.ao import flat
from kevinlulee.base import noop
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
    return sorted(store, reverse=True)
    return store


PYTHON_MODULE_PATHS = collect_python_paths()



def get_modname_from_file(file):
    if not file.endswith(".py"):
        return 

    path = os.path.expanduser(file)
    for root in PYTHON_MODULE_PATHS:
        m = path.replace(root + '/', "")
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




def load_module(key, reload=False):
    key = get_modname_from_file(key)

    if reload:
        if key in sys.modules:
            del sys.modules[key]
    return __import__(key, fromlist=(key.split(".")))


def load_func(module, func=None, reload = True):
    if not func:
        if isinstance(module, str) and "." in module:
            func = module.split(".")[-1]
        else:
            raise Exception("func is needed")
    return getattr(get_module(module, reload = reload), func, None)


def get_module_func_from_string(s):
    # private
    parts = s.split('.')
    fname = parts.pop()
    modname = '.'.join(parts)
    func = getattr(get_module(modname, reload = True), fname,None)
    return func

def run_module_func(s, *args, reload = True, **kwargs):
    func = get_module_func_from_string(s)
    return func(*args, **kwargs)


def get_module(file_name: str, reload = False, from_anywhere = False):
    """
    if from_anywhere, gets a module from anywhere. does not need to be on path
    """
    if not file_name:
        return 

    module_name = get_modname_from_file(file_name)

    if not module_name:
        return 

    if reload and module_name in sys.modules:
        del sys.modules[module_name]

    if from_anywhere:
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return __import__(module_name, fromlist=(module_name.split(".")))
        

def get_modules(*names, reload = True, on_error = None):
    store = []
    for key in names:
        if not key:
            continue
        try:
            mod = get_module(key, reload=reload)
            if mod: store.append(mod)
        except Exception as e:
            if on_error:
                return on_error(e, key)

    return store
def tempfunc():
    print('hi')
if __name__ == "__main__":
    # this is super cool
    #
    pass
    # load_func('kevinlulee.scripts.generate_pytypst_funcs')('abc')
    # print(PYTHON_MODULE_PATHS)
    # print(get_modname_and_cwd('/home/kdog3682/projects/python/kevinlulee/kevinlulee/experiments/abc.py'))


def reload_module(key):
    get_module(key, reload = True)

def reload_modules(*keys, on_error = None):
    return get_modules(flat(keys), reload = True, on_error=on_error)

def get_module_directory(modname) -> Path:
    module = importlib.import_module(modname)
    return Path(os.path.dirname(inspect.getabsfile(module)))



# print(get_modname_from_file('/home/kdog3682/projects/python/maelstrom/lib/nvim/plugins/v1/file_runner.py'))
