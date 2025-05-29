from __future__ import annotations
from .ao import flat
from .string_utils import trimdent
from .pythonfmt import pythonfmt
from .base import stop
from .date_utils import *
from .file_utils import *
from .string_utils import *
from .text_tools import *
from .module_utils import *
from .templater import *
from .base import *
from .validation import *
from .ao import *
import inspect
import yaml
import re

def yamload(x):
    if not x:
        return {}

    if callable(x):
        while hasattr(x, "__wrapped__"):
            x = x.__wrapped__
        x = getattr(x, "__doc__")

    if not x:
        return {}

    s = trimdent(x)
    try:
        m = yaml.safe_load(s)
        if type(m) == str:
            return {}
        
        return m
        
    except Exception as e:
        return {}


def pycall(*args, **kwargs):
    return pythonfmt.call(*args, **filter_none(kwargs))




def hashify(key):
    import hashlib

    return hashlib.md5(key).hexdigest()


# deprecate
# def representative(self, *args, **kwargs):
#     if len(args) and is_array(args[0]):
#         return repr(self, args[0])
#
#     def gather(self, keys):
#         return {attr for key in keys if (attr := getattr(self, key, None))}
#
#     repr_keys = getattr(self, "repr_keys", None)
#     if repr_keys:
#         kwargs = gather(self, repr_keys)
#     return pycall(nameof(self), *args, **kwargs)

def representative(self, keys):
    get = lambda key: getattr(self, key, None)
    kwargs = {key: get(key) for key in keys}
    return pycall(nameof(self), **kwargs)

def linecount(text):
    lines = text.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return len(non_empty_lines)



def add_unit(value, unit):
    base = str(value)
    if base.endswith(unit):
        return base
    return base + unit



def get_doc_string(s):
    return trimdent(getattr(s, "__doc__", "")) if s else ""


DATE_PATTERN = re.compile("^\d{4}-\d{2}-\d{2}")
NEWLINE = "\n"

def possibly_normalize_number(value):
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return value
    return value


def join_comma(*args, newline = False):
    space = '\n' if newline else ' '
    delimiter = ',' + space
    return delimiter.join(flat(args))



def tern(*args):
    l = len(args)
    if l == 2:
        a, b = args
        return a if exists(a) else b
    if l == 3:
        a, b, c = args
        return b if exists(a) else c

