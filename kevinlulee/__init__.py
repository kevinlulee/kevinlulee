from functools import wraps
from .date_utils import *
from .assertion import *
from .file_utils import *
from .string_utils import *
from .text_tools import *
from .base import *
from .validation import *
from .ao import *
from .constants import *
from .extended import *
from .array import *
from .templater import *
from .module_utils import *
from .bash import *
from .ripgrep import *
from .file_ops import *
from .components.string_builders import *
from .git import GitRepo
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt
from .ddo import LiveDict, LiveArray
import kevinlulee.ascii as ascii
import kevinlulee.introspect as introspect


def mgetall(s, regex, flags = 0):
    # string_utils
    matches = []
    
    def replacer(match):
        matches.append(match.group(1))
        return ''
        
    result = re.sub(regex, replacer, s.strip(), flags=flags).strip()
    return result, matches


def bring_to_life(code, scope=None) -> Callable:
    """
    Evaluates Python function code and returns the callable.
    
    Args:
        code (str): Python function code as a string
        scope (dict, optional): Dictionary to use as the global scope for exec.
                               If None, uses an empty dictionary.
                               
    Returns:
        callable: The function defined in the code
    """
    scope = scope or globals()
    # Create a local namespace for execution
    local_namespace = {}
    # Execute the code in the provided scope
    exec(code, scope, local_namespace)
    
    # Find the function name by parsing the code
    lines = code.strip().split('\n')
    first_line = lines[0].strip()
    
    # Extract function name from the def statement
    import re
    match = re.match(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', first_line)
    
    if not match:
        raise ValueError("Could not find function definition in the provided code")
    
    function_name = match.group(1)
    
    # Return the function from the local namespace
    if function_name not in local_namespace:
        raise ValueError(f"Function '{function_name}' was not defined in the provided code")
    
    return local_namespace[function_name]


def modify_array(items, func, key = None):
    # kx.ao
    for i, item in enumerate(items):
        value = func(item)
        if value is not None:
            if key:
                items[i][key] = value
            else:
                items[i] = valuee
    return items

def edit_dict(dct, key, editor):
    section = dct.get(key)
    if not section:
        return dct

    def apply(base, v):
        if isinstance(base, (list, tuple)):
            return [v(el) for el in base]
        else:
            return v(base)

    if isinstance(editor, dict):
        for k, v in editor.items():
            to_be_edited = section.get(k)
            if to_be_edited is not None:
                new_value = apply(to_be_edited, v)
                if new_value is not None:
                    section[k] = new_value
    else:
        raise Exception("todo")

    return dct

def keycache(key_func):
    cache = {}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if key in cache:
                return cache[key]
            result = fn(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    return decorator

get_caller = introspect.get_caller

class Watcher:
    def __init__(self, key_func = repr):
        self.seen = set()
        self.store = []
        self.count = 0
        self.key_func = key_func
        
    def __contains__(self, item):
        reference = self.key_func(item)
        if reference in self.seen:
            return True
        else:
            self.seen.add(reference)
            return False

def delete_file(file):
    path = os.path.expanduser(str(file))
    os.unlink(path)
    return path

def remove_commented_lines(s, filetype=None):
    r = '^( *)(?:#+|//+|"|--+) *.*'
    return re.sub(r, "", s, flags=re.M)

from collections import defaultdict


def remove_quotes(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    elif s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    else:
        return s

from typing import *

def templaterf(callback):
    # kx
    def wrapper(s, reference):

        def replacer(x):
            key = x.group(1)
            return callback(key, reference)
        regex = '\$(\w+)'
        return re.sub(regex, replacer, s)
        
    return wrapper


    


def collect(file, pattern, sort=False, unique=False):
    s = text_getter(file)
    flags = re.M if pattern.startswith('^') else 0
    
    matches = []
    for match in re.finditer(pattern, s, flags=flags):
        m = get_match(match)
        if m:
            matches.append(m)
    
    if unique:
        matches = list(set(matches))
    
    if sort:
        matches.sort()
    
    return matches


def opposite(x):
    match x:
        case 0: return 1
        case 1: return 0
        case True: return False
        case False: return True
        case _: return not bool(x)
def toggle(state, key, verbose = False):
    v = getattr(state, key, False)
    new = opposite(v)
    setattr(state, key, new)
    if verbose: print(f'setting state.{key} as {new}')
