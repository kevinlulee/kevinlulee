from __future__ import annotations
from .ao import flat
from .string_utils import trimdent
from .pythonfmt import pythonfmt
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

def yamload(x, strict = False):
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
        print(e)
        if strict:
            raise e
        return {}


def pycall(*args, **kwargs):
    return pythonfmt.call(*args, **filter_none(kwargs))




def hashify(key):
    import hashlib

    return hashlib.md5(key.encode()).hexdigest()


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
        return float(value)
    return int(value)


# def join_comma(*args, newline = False, ending_comma = False):
#     space = '\n' if newline else ' '
#     delimiter = ',' + space
#     p = delimiter.join(flat(args))
#     if ending_comma:
#         return p+','
#     return p



def tern(*args):
    l = len(args)
    if l == 2:
        a, b = args
        return a if exists(a) else b
    if l == 3:
        a, b, c = args
        return b if exists(a) else c



def templaterf(callback):
    # kx
    def wrapper(s, reference):
        def replacer(x):
            key = x.group(1)
            return callback(key, reference)

        regex = "\$(\w+)"
        return re.sub(regex, replacer, s)

    return wrapper


def collect(file, pattern, sort=False, unique=False):
    s = text_getter(file)
    flags = re.M if pattern.startswith("^") else 0

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


def opposite(word):
    lower = word.lower()
    if lower in OPPOSITES:
        return match_case(word, OPPOSITES[lower])
    return None


def toggle(state, key):
    if is_dict(state):
        v = state.get(key)
        new = opposite(v)
        state[key] = new
    else:
        v = getattr(state, key, False)
        new = opposite(v)
        setattr(state, key, new)
    return state



def state_toggle(state, key):
    if is_dict(state):
        v = state.get(key)
        new = opposite(v)
        state[key] = new
    else:
        v = getattr(state, key, False)
        new = opposite(v)
        setattr(state, key, new)
    return state



def get_length(x):
    assert is_lenable(x), f"{x} is not lenable"
    return len(x)


def announcef(func):
    def wrapper(*args, **kwargs):
        v = func(*args, **kwargs)
        if v is not None:
            print(v)

    return wrapper

def sort_files_by_date(files, reverse=True):
    """
    most recent files comes first
    """
    
    return sorted(files, key=os.path.getmtime, reverse=reverse)

def sort_by_date(files, reverse=True):
    return sorted(files, key=os.path.getmtime, reverse=reverse)


def looks_like_path(x):
    return test(x, "^(?:[/~])|\./")


def instantiate_cls(cls):
    return cls() if is_class_constructor(cls) else cls


def xsplit(x):
    if isinstance(x, (list, tuple)):
        return x

    return [coerce_argument(el) for el in split(x, "\s+")]


def colon_split(s, content_key = 'value'):
    """
    a very useful split function
    an example is shown below

    abc:
        def:
            ghi: hi

        this will also be aggregated in as the key: value
        multiple lines too

        multiple lines too
        multiple lines too ... and newlines.
    """
    regex = "^([\w-]+):"
    parts = re.split(regex, trimdent(s), flags=re.M)
    parts = filtered(each(parts, trimdent))
    chunks = partition(parts)

    store = {}
    for a, b in chunks:
        s, fm = extract_frontmatter(b)
        if fm:
            value = trimdent(s)
            if value:
                fm[content_key] = value
            store[a] = fm
        else:
            store[a] = coerce_argument(s)
    return store

def extract_frontmatter2(text):
    if text.startswith('---\n'):
        def replacer(x):
            key = x.group(0)
            return ''
            
        regex = '^---\n*([\w\W]+?)\n---\n*'
        s = re.sub(regex, '', text, flags = 0)
        fm = matchstr(text, regex)
        return s, colon_split(fm, content_key='description')

    return extract_frontmatter(text)

