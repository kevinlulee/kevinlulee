import sys
from typing import Union
import re
import os
import importlib

from kevinlulee.file_utils import get_extension


def collect_python_paths():
    home = os.path.expanduser('~/')
    paths = sys.path
    store = []
    for p in paths:
        if p not in store and home in p:
            store.append(re.sub("/$", "", p))
    return store

PYTHON_MODULE_PATHS = collect_python_paths()


def get_modname_from_file(file):
    if not file.endswith('.py'):
        return file
    
    path = os.path.expanduser(file)
    for root in PYTHON_MODULE_PATHS:
        m = path.replace(root, "")
        if len(m) < len(path):
            a = m.replace('.py', '').replace("/", ".")
            b = re.sub("^\.", "", a)
            return b.replace('__init__', '')


def get_file_from_modname(modname):
    if not modname:
        return 
    if modname.endswith('.py') and os.path.exists(os.path.expanduser(modname)):
        return os.path.expanduser(modname)
    suffix = modname.replace(".", "/")
    for root in PYTHON_MODULE_PATHS:
        candidate = os.path.join(root, suffix + ".py")
        if os.path.isfile(candidate):
            return candidate

        candidate = os.path.join(root, suffix)
        if os.path.isdir(candidate):
            p = os.path.join(candidate, '__init__.py')
            if os.path.isfile(p):
                return p
            

def delete_module(key):
    key = get_modname_from_file(key)
    if key in sys.modules:
        del sys.modules[key]
        return True

def get_modname(x: Union["path", "package_name"]):
    return get_modname_from_file(x) if os.path.exists(os.path.expanduser(x)) else x

def reload_module(key):
    return importlib.reload(get_modname_from_file(key))

def load_module(key, reload = False):
    key = get_modname_from_file(key)

    if reload:
        if key in sys.modules:
            del sys.modules[key]
    return __import__(key, fromlist=(key.split(".")))

def load_func(module, func):
    return getattr(load_module(module), func, None)

# print(get_file_from_modname('kevinlulee'))
