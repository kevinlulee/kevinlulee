from os.path import isdir
from pathlib import Path
import pathlib
import sys
from typing import Union
import re
from pprint import pprint
import os
import importlib

from kevinlulee.ao import flat
from kevinlulee.base import noop
from kevinlulee.file_utils import EXTENSIONS, add_extension_if_not_present, get_extension, is_dir, remove_extension
from kevinlulee.string_utils import matchstr, remove_ending_slash

from pathlib import Path
import os

from kevinlulee.validation import is_word



def collect_python_paths():
    home = os.path.expanduser("~/")
    paths = sys.path
    store = []
    exclude = re.compile(r"site-packages|\.(?:cache|local)")
    for path in paths:
        if path not in store and home in path and not re.search(exclude, path):
            store.append(re.sub("/$", "", path))
    return sorted(store, key = len, reverse = True)
    return store


PYTHON_MODULE_PATHS = collect_python_paths()



def get_modname_from_file(file):
    if not file.endswith(".py"):
        if '.' in file:
            return file
        else:
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
    module = get_module(modname, reload = True)
    func = getattr(module, fname,None)
    return func

def get_implicit_module_func(s):
    parts = s.split('.')
    fname = parts[-1]
    modname = '.'.join(parts)
    module = get_module(modname, reload = True)
    func = getattr(module, fname,None)
    return func

def run_module_func(s, *args, reload = True, **kwargs):
    func = get_module_func_from_string(s)
    return func(*args, **kwargs)


def use(s, *args):
    key = f'kevinlulee.lib.{s}.{s}'
    return run_module_func(key, *args, reload = False)

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

def get_root_directory_via_python_paths(key):

    assert is_word(key), f"the provided key '{key}' ... must be something like 'yoya'"

    for path in PYTHON_MODULE_PATHS:
        j = os.path.join(path, key)
        if is_dir(j):
            return j


def get_root_directory_from_path(path):
    """
    print(get_root_directory_from_path("/home/kdog3682/projects/python/maelstrom/lib/aicmp/agent/code_request.py")) returns aicmp
    """
    p = Path(path)
    for part in p.parents:
        directory = remove_ending_slash(part.parent)
        if directory in PYTHON_MODULE_PATHS:
            return os.path.join(directory, part.name)

def path_unexpand(path):
    """
    this is a more robust implementation than the previous nvim.pathfix.
    nothing is hardcoded. the directories are retrieved from python path.
    """
        
    path = os.path.expanduser(path)
    if '/scratch/' in path:
        name = os.path.basename(path)
        return f'@scratch/{name}'
    root = get_root_directory_from_path(path)
    if root:
        return path.replace(root, '@' + remove_ending_slash(os.path.basename(root)))
    else:
        return path.replace(os.path.expanduser('~/'), '')

def path_expand(path):
    """
    this is a more robust implementation than the previous nvim.pathfix.
    nothing is hardcoded. the directories are retrieved from python path.
    """
    crostini_str = 'file:///media/fuse/crostini_25bd1ae3ef71bac8d459747ce670faa67d509f14_termina_penguin/'
    if path.startswith(crostini_str):
        return os.path.expanduser(path.replace(crostini_str, '~/'))
    if path.startswith('@') and re.search('^@\w+(?:/|$)', path):
        def replacer(x):
            key = x.group(1)
            c = os.path.join(os.path.expanduser('~/projects'), key)
            if is_dir(c):
                return c
            root = get_root_directory_via_python_paths(key)
            assert root, f"unable to determine a root for '{key}'"
            return root

        return re.sub('^@(\w+)', replacer, path)

    if path.startswith('~'):
        return os.path.expanduser(path)

    if path.startswith('./'):
        raise Exception('do not know how to handle "./" yet.')
    return path

def path_join(*args):
    assert len(args) > 1, "path_join requires at least 2 arguments"
    a, *rest, last = args
    a = os.path.expanduser(a)
    if last in EXTENSIONS:
        rest[-1] = add_extension_if_not_present(rest[-1], last)
    else:
        rest.append(last)
    return os.path.join(path_expand(a), *rest)
        
if __name__ == '__main__':
    # print(path_join('@hammymathclass', 'a', 'typ'))
    # pprint(PYTHON_MODULE_PATHS)
    # print(path_expand('@yoya/utils/foobar.py'))
    # print(path_unexpand("~/projects/python/maelstrosdm/lasdib/aidscmp/agent/code_request.py"))
    # print(get_root_directory_from_path("/home/kdog3682/projects/python/maelstrom/lib/aicmp/agent/code_request.py"))
    # print(get_modname_from_file('/home/kdog3682/projects/python/maelstrom/lib/nvim/plugins/v1/file_runner.py'))
    # content = get_implicit_module_func('yoya.utils.prepare_text')
    pass
    # print(content)
