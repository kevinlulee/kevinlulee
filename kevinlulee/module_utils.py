from os.path import isdir
from pathlib import Path
import pathlib
import sys
from typing import Union
import re
from pprint import pprint
import os
import importlib

from kevinlulee.ao import filtered, flat, not_in, unique
from kevinlulee.base import noop
from kevinlulee.file_utils import (
    EXTENSIONS,
    add_extension_if_not_present,
    get_extension,
    is_dir,
    looks_like_file,
    readfile,
    remove_extension,
)
from kevinlulee.string_utils import matchstr, remove_ending_slash, pascal_case, dash_case

from pathlib import Path
import os

from kevinlulee.validation import is_string, is_word

import importlib
import sys
from pathlib import Path


def import_module_from_path(path: str, module_name = None):
    path = Path(path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {path}")

    if not path.suffix == ".py":
        raise ValueError(f"File must be a .py file: {path}")

    module_name = module_name or get_modname_from_file(str(path)) or path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e
        raise Exception(e)
        print(e)


def collect_python_paths():
    home = os.path.expanduser("~/")
    paths = sys.path
    store = []
    exclude = re.compile(r"site-packages|\.(?:cache|local)")
    for path in paths:
        if path not in store and home in path and not re.search(exclude, path):
            store.append(re.sub("/$", "", path))
    return sorted(store, key=len, reverse=True)
    return store


PYTHON_MODULE_PATHS = collect_python_paths()


def _get_modname(file):
    path = os.path.expanduser(file)
    path = remove_ending_slash(path)
    for root in PYTHON_MODULE_PATHS:
        m = path.replace(root + "/", "")
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


def get_modname_from_directory(path):
    if not is_dir(path):
        return

    return _get_modname(path)


def get_modname_from_file(file):
    file = str(file)
    m = matchstr(file, "site-packages/(.+)")
    if m:
        return remove_extension(m).replace("/", ".")

    # print(kx.get_module("/home/kdog3682/.local/lib/python3.11/site-packages/anthropic/types/beta/beta_usage.py"))
    if not file.endswith(".py"):
        return
        if "." in file:
            return file
        else:
            return

    return _get_modname(file)


def get_file_from_modname(modname, strict=True) -> str:
    """
    Resolve a module name to its file path.
    
    Args:
        modname: Module name (e.g., 'os.path') or path to a .py file.
        strict: If True, search all PYTHON_MODULE_PATHS for the full module path.
                If False, only check if the first part of the module name resolves
                to a valid path in PYTHON_MODULE_PATHS, then return the candidate
                path without verifying it exists.
    
    Returns:
        Path to the module file or directory, or None if not found.
    """
    if not modname:
        return
    if modname.endswith(".py") and os.path.exists(os.path.expanduser(modname)):
        return os.path.expanduser(modname)
    
    parts = modname.split(".")
    suffix = "/".join(parts)
    
    if not strict:
        if modname.endswith(".py"):
            return modname

        first_part = parts[0]
        for root in PYTHON_MODULE_PATHS:
            first_candidate = os.path.join(root, first_part)
            if os.path.isdir(first_candidate) or os.path.isfile(kx.add_extension_if_not_present(first_candidate, 'py')):
                return os.path.join(root, kx.add_extension_if_not_present(suffix, 'py'))
        return
    
    for root in PYTHON_MODULE_PATHS:
        candidate = os.path.join(root, suffix + ".py")
        if os.path.isfile(candidate):
            return candidate
        candidate = os.path.join(root, suffix)
        if os.path.isdir(candidate):
            p = os.path.join(candidate, "__init__.py")
            if os.path.isfile(p):
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


def load_func(module, func=None, reload=True):
    if not func:
        if isinstance(module, str) and "." in module:
            func = module.split(".")[-1]
        else:
            raise Exception("func is needed")
    return getattr(get_module(module, reload=reload), func, None)


def get_module_func_from_string(s):
    # private
    parts = s.split(".")
    fname = parts.pop()
    modname = ".".join(parts)
    module = get_module(modname, reload=True)
    func = getattr(module, fname, None)
    return func


def get_implicit_module_func(s, strict=False):
    parts = s.split(".")
    fname = parts[-1]
    modname = ".".join(parts)
    module = get_module(modname, reload=True)
    func = getattr(module, fname, None)
    if strict and not func:
        raise Exception("was unable to retrieve the func", fname)
    return func


def run_module_func(s, *args, reload=True, **kwargs):
    func = get_module_func_from_string(s)
    return func(*args, **kwargs)


def use(s, *args):
    key = f"kevinlulee.lib.{s}.{s}"
    return run_module_func(key, *args, reload=False)


def get_module(file_name: str, reload=False, from_anywhere=False):
    """
    if from_anywhere, gets a module from anywhere. does not need to be on path
    """
    if not file_name:
        return

    if is_string(file_name):
        module_name = get_modname_from_file(file_name)

        if not module_name:
            if re.search("^\w+(?:\.\w+)*$", file_name):
                module_name = file_name
            else:
                return

    if reload and module_name in sys.modules:
        del sys.modules[module_name]

    if from_anywhere:
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return __import__(module_name, fromlist=(module_name.split(".")))


def get_modules(*names, reload=True, on_error=None):
    store = []
    for key in names:
        if not key:
            continue
        try:
            mod = get_module(key, reload=reload)
            if mod:
                store.append(mod)
        except Exception as e:
            if on_error:
                return on_error(e, key)

    return store


def tempfunc():
    print("hi")


if __name__ == "__main__":
    # this is super cool
    #
    pass
    # load_func('kevinlulee.scripts.generate_pytypst_funcs')('abc')
    # print(PYTHON_MODULE_PATHS)
    # print(get_modname_and_cwd('/home/kdog3682/projects/python/kevinlulee/kevinlulee/experiments/abc.py'))


def reload_module(key):
    get_module(key, reload=True)


def reload_modules(*keys, on_error=None):
    return get_modules(flat(keys), reload=True, on_error=on_error)


def get_module_directory(modname) -> Path:
    module = importlib.import_module(modname)
    return Path(os.path.dirname(inspect.getabsfile(module)))


def get_root_directory_via_python_paths(key):
    assert is_word(
        key
    ), f"the provided key '{key}' ... must be something like 'yoya'"

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
    if "/scratch/" in path:
        name = os.path.basename(path)
        return f"@scratch/{name}"
    root = get_root_directory_from_path(path)
    if root:
        return path.replace(
            root, "@" + remove_ending_slash(os.path.basename(root))
        )
    else:
        return path.replace(os.path.expanduser("~/"), "")


def path_expand(path):
    """
    this is a more robust implementation than the previous nvim.pathfix.
    nothing is hardcoded. the directories are retrieved from python path.
    """
    if isinstance(path, Path):
        return str(path.expanduser())

    crostini_str = "file:///media/fuse/crostini_25bd1ae3ef71bac8d459747ce670faa67d509f14_termina_penguin/"
    if path.startswith(crostini_str):
        return os.path.expanduser(path.replace(crostini_str, "~/"))
    if path.startswith("@") and re.search("^@\w+(?:/|$)", path):

        def replacer(x):
            key = x.group(1)
            c = os.path.join(os.path.expanduser("~/projects"), key)
            if is_dir(c):
                return c
            root = get_root_directory_via_python_paths(key)
            assert root, f"unable to determine a root for '{key}'"
            return root

        return re.sub("^@(\w+)", replacer, path)

    if path.startswith("~"):
        return os.path.expanduser(path)

    if path.startswith("./"):
        raise Exception('do not know how to handle "./" yet.')
    return path


def get_directory_from_modname(modname):
    suffix = modname.replace(".", "/")
    for root in PYTHON_MODULE_PATHS:
        candidate = os.path.join(root, suffix)
        if os.path.isdir(candidate):
            return candidate


def path_join(*args):
    assert len(args) > 1, "path_join requires at least 2 arguments"
    a, *rest, last = args
    if looks_like_file(a):
        a = os.path.dirname(a)

    a = os.path.expanduser(a)
    if last in EXTENSIONS:
        if rest:
            rest[-1] = add_extension_if_not_present(rest[-1], last)
        else:
            a = add_extension_if_not_present(a, last)
    else:
        rest.append(last)
    return os.path.join(path_expand(a), *rest)


if __name__ == "__main__":
    # print(path_join('@hammymathclass', 'a', 'typ'))
    # pprint(PYTHON_MODULE_PATHS)
    # print(path_expand('@yoya/utils/foobar.py'))
    # print(path_unexpand("~/projects/python/maelstrosdm/lasdib/aidscmp/agent/code_request.py"))
    # print(get_root_directory_from_path("/home/kdog3682/projects/python/maelstrom/lib/aicmp/agent/code_request.py"))
    # print(get_modname_from_file('/home/kdog3682/projects/python/maelstrom/lib/nvim/plugins/v1/file_runner.py'))
    # content = get_implicit_module_func('yoya.utils.prepare_text')
    pass
    # print(content)
    # print(get_modname_from_directory('/home/kdog3682/projects/python/kevinlulee/kevinlulee/'))
    # print(get_directory_from_modname('kevinlulee'))
    # print(get_implicit_module_func('nvim.scripts.make_html_textarea'))


def collect_shallow_python_imports(file):
    src = readfile(file)
    r1 = "^from (\w+(?:\.\w+)*) import"
    r2 = "^import (\w+)"

    a = re.findall(r1, src, flags=re.M)
    # b = re.findall(r2, src, flags = re.M)
    # print(a)
    # print(b)
    ignore = [
        "__future__",
        "kevinlulee",
    ]
    a = unique(filtered(a, not_in(ignore)))
    return a


def get_module_functions(module):
    if is_string(module):
        module = get_module(module)

    all = getattr(module, "__all__")
    assert all, "'__all__' must be defined in order to use get_module_functions"

    return [getattr(module, key) for key in all]


import os
import kevinlulee as kx

project_directories = [
    "~/projects/",
    "~/projects/webdev",
    "~/projects/python",
]


def get_modname_from_project_name(x):
    path = os.path.expanduser(x)

    # Case 1: x is a path under one of the project directories — extract the leaf name.
    for base in project_directories:
        r = os.path.join(os.path.expanduser(base), r"([\w-]+)$")
        m = kx.matchstr(path, r)
        if m:
            return m

    # Case 2: x is a project name that exists in one of the project directories.
    for base in project_directories:
        p = path_join(base, x)
        if is_dir(p):
            return os.path.basename(os.path.expanduser(p))


def get_directory_from_project_name(x):
    xp = os.path.expanduser(x)

    # If x is an actual path inside any project directory, accept it.
    for base in project_directories:
        b = os.path.expanduser(base)
        if xp.startswith(b) and is_dir(xp):
            return xp

    # Otherwise, look for x as a child of each project directory.
    for base in project_directories:
        p = path_join(base, x)
        if is_dir(p):
            return p


file_from_modname = get_file_from_modname



import importlib

def reload_and_retrieve(module_path: str, class_name: str | None = None):
    module = importlib.import_module(module_path)
    importlib.reload(module)

    if class_name is None:
        last_segment = dash_case(module_path.split(".")[-1])
        class_name = getattr(module, last_segment, None) or getattr(
            module, pascal_case(last_segment), None
        )

    return getattr(module, class_name)

if __name__ == "__main__":
    kx.pretty_print(path_join("~/asdf", "pdf"))
    # a = import_module_from_path("/home/kdog3682/projects/python/maelstrom/lib/nvim/playground.py")
    # kx.pretty_print(import_module_from_path('/home/kdog3682/scratch/scratch.py'))
