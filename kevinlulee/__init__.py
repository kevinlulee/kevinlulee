import re
import os

from collections import defaultdict
from typing import *
from dataclasses import dataclass


from .base import *
from .date_utils import *
from .assertion import *
from .ao import *
from .string_utils import *
from .serialize_ops import normalize_data, serialize_data
from .file_utils import *
from .text_tools import *
from .validation import *
from .constants import *
from .array import *
from .templater import *
from .module_utils import *
from .bash import *
from .ripgrep import *
from .file_ops import *
from .test_ops import run_test_cases

# from .components.string_builders import *
from typing import *
from .git import GitRepo
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt
from .functions import *
from .class_introspection_ops import *
import kevinlulee.yb as yb
import kevinlulee.ascii as ascii
import kevinlulee.introspect as introspect
import kevinlulee.lorem as lorem
import kevinlulee.rng as rng
import kevinlulee.utf as utf
import kevinlulee.env as env
import kevinlulee.math_ops as math_ops
import kevinlulee.debug_ops as debug_ops
from .extended import *
from .ddo import LiveDict, LiveArray
from .text import StringBuilder
# from .extensions import *
from .misc import *
from pprint import pprint

get_caller = introspect.get_caller

def pretty_print(*args):
    for arg in args:
        if arg is None:
            continue
        if isinstance(arg, (float, int, complex, str, bool)):
            print(arg)
        elif hasattr(arg, 'render'):
            print(str(arg))
        else:
            pprint(arg)


def fparse(input, *args, **kwargs):
    if not is_primitive(input) and callable(input):
        return input(*args, **kwargs)
    else:
        return input


def newline_padding(s, padding):
    if not padding:
        return s

    a, b = padding if is_array(padding) else (padding, padding)
    return "\n" * (a) + s + "\n" * (b)


def path_in(paths, src_path):
    src_path = os.path.expanduser(src_path)
    for path in paths:
        path = os.path.expanduser(path)
        if path in src_path:
            return path


def announce(*args, **kwargs):
    print(*args, **kwargs)
def throw_on(x):
    def foo(el):
        if el == x:
            raise Exception(f"throw on {x}")
        return el
    return foo


def tprint(s):
    print(trimdent(s))

def json_load(x):
    try:
        return json.loads(x)
    except Exception as e:
        return x


def ordinal(n: int) -> str:
    # returns a string like 3rd or 4th or 5th or 66th
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}" 

def slugify(title: str) -> str:
    """
    Conservative, filesystem-safe slug:
    - normalize whitespace
    - keep ASCII letters, digits, space, underscore, dash
    - spaces -> single dash
    """
    t = re.sub(r"\s+", " ", title.strip())
    t = re.sub(r"[^0-9A-Za-z _\-]", "", t)
    t = re.sub(r"[\s]+", "-", t)
    return t.lower()

def compose(*funcs):
    start = len(funcs) - 1
    def wrapper(*args, **kwargs):
        result = None
        for i in range(start, 0, -1):
            if i == start:
                result = funcs[i](*args, **kwargs)
            else:
                result = funcs[i](result)

        return result
            

    return wrapper



def slice_quotes(template):
    return re.sub(r'^[\'"]|[\'"]$', '', template)



def auto_cast(s):
    try:
        return int(s)
    except Exception:
        try:
            return float(s)
        except Exception:
            return s
