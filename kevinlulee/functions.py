import re
from _collections_abc import dict_values, dict_keys, dict_items
import shutil
import kevinlulee as kx
import functools

from kevinlulee.ao import reduce2
from kevinlulee.validation import existant, exists


HEADER_RE = re.compile(r'^(?P<key>@?[\w-]+):(?:\s*(?P<val>.*\S))?\s*$')
import re
from typing import List, Tuple, Optional


# colon_dict.py
from typing import List, Tuple, Optional
import re
import kevinlulee as kx


HEADER_RE = re.compile(r'^(?P<key>@?[\w-]+):(?:\s*(?P<val>.*\S))?\s*$')


def colon_dict(
    text: str,
    *,
    strict: bool = False,
    skip_empty_strings: bool = True,
    allow_repeated_keys: bool = False,
    transformers: Optional[dict] = None,
) -> dict:
    """
    Parse a headered block format.

    Each header is of the form "key:" or "key: inline value".
    Subsequent non-header lines belong to the current key until the next header.

    - Returns: dict; if allow_repeated_keys=False the last value wins,
      else values are returned under a pluralized key as a list.
    - strict=True: if a key has an inline value (e.g., "a: v") and any
      subsequent non-empty content line appears before the next header,
      raise ValueError.
    - If `transformers` is provided, only keys in transformers are treated
      as headers; other "X:" lines are treated as plain content.
    """
    allowed_keys = set(transformers) if transformers else None

    items: List[Tuple[str, str]] = []
    current_key: Optional[str] = None
    buf: List[str] = []
    had_inline = False  # whether the *current* key had an inline value

    def flush_block() -> None:
        nonlocal current_key, buf, had_inline
        if current_key is not None:
            value = "\n".join(buf).strip()
            if not (skip_empty_strings and value == ""):
                items.append((current_key, value))
        current_key = None
        buf = []
        had_inline = False

    for raw in text.splitlines():
        m = HEADER_RE.match(raw)

        # Valid header only if either no allowlist, or key is allowlisted
        if m and (allowed_keys is None or m.group("key") in allowed_keys):
            flush_block()
            current_key = m.group("key")
            inline = m.group("val")
            had_inline = inline is not None
            if inline is not None:
                buf.append(inline)
            continue  # move to next line after opening a new block

        # Not a recognized header → treat as content (if we have a current block)
        if current_key is None:
            # No active block: ignore leading/preamble content or disallowed headers.
            # (Matches original behavior which doesn't emit items without a key.)
            continue

        # Enforce strict inline rule: any non-empty content after an inline value
        if strict and had_inline and raw.strip() != "":
            raise ValueError(
                f"Inline value given for '{current_key}', but additional content found on a following line."
            )

        if not (skip_empty_strings and raw == ""):
            buf.append(raw)

    # Flush the final block
    flush_block()

    # Transform values and collapse/group
    def transform_value(k: str, v: str):
        base = kx.coerce_argument(v)
        return transformers[k](base) if transformers and k in transformers else base

    transformed = [(k, transform_value(k, v)) for (k, v) in items]
    grouped = kx.group(transformed)  # {key: [values...]}

    store: dict = {}
    for k, vals in grouped.items():
        if allow_repeated_keys:
            store[kx.pluralize(k)] = vals
        else:
            store[k] = vals[-1]
    return store



def rpw(file, fn):
    kx.writefile(file, fn(kx.readfile(file)))

def to_string(x):
    if isinstance(x, str):
        return x

    for key in ("text", "body", "value", "content"):
        if hasattr(x, key):
            return getattr(x, key)

    if callable(x):
        return kx.inspect.getsource(x)
    if isinstance(x, (list, tuple, set, dict, dict_keys, dict_values, dict_items)):
        return kx.json.dumps(x, indent=2)

    return str(x)


def infer_lang(value):
    if callable(value):
        return "python"

    if kx.is_string(value):
        return "python"

    return "json"


def join_comma(items, max_length=60, newline=False, ending_comma=False):
    citems = [str(item) for item in items]
    sample = ", ".join(citems)
    ending_comma = "," if ending_comma else ""
    if newline == False and len(sample) <= max_length:
        return sample + ending_comma
    return ",\n".join(citems) + ending_comma


def join_comma(*args, newline=False, ending_comma=False):
    elements = kx.flat(args, validator=kx.not_none)
    computed = [str(x) for x in elements]

    space = "\n" if newline else " "
    delimiter = "," + space
    p = delimiter.join(computed)
    if ending_comma:
        return p + ","
    return p


def join(*args, delimiter=" "):
    els = kx.flat(args)
    if els[-1] in [",", "/", ".", " ", "\n"]:
        return els[-1].join(els[:-1])
    return delimiter.join(els)


def bug_call(*args, **kwargs):
    from codefmt.python import pythonfmt

    caller = kx.introspect.get_caller(1).function
    call_expr = pythonfmt.call(caller, args, kwargs, condensed=True)
    print("[DEBUG]", call_expr)


def get_qualified_func_name(func):
    """
    returns Foo.bar if the func is a method or a abcde() if it is a function
    """
    mod = getattr(func, "__module__", None)
    if mod == '__main__':
        mod = None
    name = func.__qualname__
    cname = kx.join(mod, name, ".")
    return cname


def get_class_methods(cls, pattern="^[a-z]") -> list[callable]:
    store = []

    def add(name, func):
        if callable(func):
            if not pattern or (pattern and kx.test(name, pattern)):
                store.append(func)

    if kx.is_class_constructor(cls):
        for name, func in cls.__dict__.items():
            add(name, func)
    elif kx.is_class_instance(cls):
        for key in dir(cls):
            add(key, getattr(cls, key))

    return store


def brace_templater(s, ref, cls=None):
    """
    a simpler version of templater.
    uses {braces}.

    class objects are allowed
    the entity contained in {brace} must be an expression.
    otherwise it will not be pattern matched.

    """
    if kx.is_array(ref):
        ref = kx.array_to_dict(ref)

    if cls:
        ref["self"] = cls

    TEMPLATER_PATTERN2 = re.compile(
        r"""
        (?:(\n)([ \t]+))?  # optional newline spaces
        {(\d+|[a-zA-Z]\w*(?:\.\w+(?:\(.*?\))?)*)}   # bracket containing an expr-like string
    """,
        flags=re.VERBOSE,
    )

    def get(expr):
        if kx.test(expr, r"\bself\b"):
            s = eval(expr, ref)
            return s

        if kx.test(expr, r"\w+\("):
            s = eval(expr)
            return s
        return ref.get(expr)

    def replacer(match):
        newline, ind, expr = match.groups()
        g = get(expr)
        if not g:
            return '<EMPTY>'
        payload = kx.serialize_data(g)
        return kx.newline_indent(payload, ind) if newline else payload

    s = kx.trimdent(s)
    s = re.sub(TEMPLATER_PATTERN2, replacer, s)
    # print([s])
    s = re.sub("(?:.+\n)?(?:---\n)? *<EMPTY> *(?:\n---\n+)?", '', s).strip()
    s = re.sub(".+<EMPTY> *$", '', s).strip()

    return s


def run_tests(tests, func):
    items = kx.to_lines(kx.trimdent(tests))
    kx.prettyprint(kx.map(items, func))


def printable(**kwargs):
    s = kx.StringBuilder()
    for k, v in kwargs.items():
        s.add_field(k, v)

    return kx.stop(s)


def file_cache(cache_path: str, update_on_touch=True, **time_opts):
    if not time_opts:
        time_opts = dict(minutes=30)

    last_touched = None
    is_recent = kx.is_recentf(**time_opts)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if is_recent(cache_path):
                return kx.readfile(cache_path)

            elif (
                update_on_touch
                and last_touched
                and kx.is_file(cache_path)
                and is_recent(last_touched)
            ):
                last_touched = kx.timestamp()
                return kx.readfile(cache_path)

            # initialize because caching did yield a value
            result = func(*args, **kwargs)
            if cache_path:
                kx.writefile(cache_path, result)
                last_touched = kx.now()
            return result

        return wrapper

    return decorator


import os


def mv(a, b):
    raise Exception("use mvfile or mvdir")
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    if not os.path.exists(a):
        return
    return kx.bash3("mv", a, b)

def read_write(file, func, *args, raw=False, dst_path=None, **kwargs):
    if dst_path:
        dst_path = kx.fnamemodify(file, **dst_path)
    else:
        dst_path = file

    value = func(kx.readfile(file), *args, **kwargs)
    path = kx.writefile(dst_path, value)
    return path


def reducef(func):
    return lambda x: kx.reduce(x, func)


import inspect, re
from typing import Iterable

default_ignored_methods = [
    'construct', '__init__', '__str__', 'setup', 'load'
]
def get_class_method_names(obj_or_cls,
                      pattern: str = r"^[a-z]",
                      ignore_methods: Iterable[str] | None = default_ignored_methods,
                      ignore_parents: Iterable[str] | None = None,
                      ignore_inherited: bool = True,
                      ignore_static: bool = True,
                      ignore_classmethods: bool = True) -> list[str]:
    """
    Return method *names* on a class (or instance's class), filtered by regex.
    Safe: reads class __dict__ (no getattr on instance), so properties/descriptors won't run.

    - ignore_inherited=True  -> only methods defined directly on the class
    - ignore_static=True     -> exclude @staticmethod
    - ignore_classmethods=True -> exclude @classmethod
    """
    klass = obj_or_cls if inspect.isclass(obj_or_cls) else obj_or_cls.__class__
    rx = re.compile(pattern) if pattern else None
    ignore_methods = set(ignore_methods or [])
    names, seen = [], set()

    classes = [klass] if ignore_inherited else list(klass.__mro__)

    for C in classes:
        for name, attr in C.__dict__.items():
            if rx and not rx.match(name):
                continue
            if name in ignore_methods:
                continue

            # Handle staticmethod / classmethod explicitly
            if isinstance(attr, staticmethod):
                if ignore_static:
                    continue
                func = attr.__func__
            elif isinstance(attr, classmethod):
                if ignore_classmethods:
                    continue
                func = attr.__func__
            else:
                func = attr

            # Keep only plain functions (i.e., instance methods before binding)
            if not inspect.isfunction(func):
                continue

            # Optional parent filtering when scanning MRO
            if not ignore_inherited and ignore_parents:
                qual_candidates = (func.__qualname__, f"{C.__name__}.{name}", C.__name__)
                if any(
                    any(qc == p or qc.startswith(p if p.endswith('.') else p + '.') for qc in qual_candidates)
                    for p in ignore_parents
                ):
                    continue

            if name not in seen:
                seen.add(name)
                names.append(name)

    return names



class Base:
    def base_method(self): ...
    @property
    def before_render(self):
        raise RuntimeError("should not run")

class Child(Base):
    def render(self): ...
    @staticmethod
    def util(): ...
    @classmethod
    def build(cls): ...

# print(get_class_method_names(Child))



def assertion_factory(t):
    def runner(x):
        assert isinstance(x, t), kx.trimdent(f'''
            the input is of type "{type(x)}". the required type is {t}.
        ''')

    return runner

assert_str= assertion_factory(str)
assert_dict = assertion_factory(dict)
assert_list = assertion_factory((list, tuple, set))
def assert_existance(x, message = ''):
    assert existant(x), kx.trimdent(message or f'''
        the provided input {type(x)} MUST exist. 
    ''')


def get_data(key):
    def replacer(x):
        key = x.group(0)
        return key
        
    key = re.sub("^\w+", replacer, key, flags = 0)
    file = kx.add_extension_if_not_present(key, 'json')
    path = f'~/data/{file}'
    return kx.readfile(path)

def get_doc_string(func):
    return kx.trimdent(func.__doc__)





s = """

    hi

    asfasdf
    ---
    {snippet}
    ---

    howdy
"""
# print(brace_templater(s, dict(snippet = None)))


def normalize_padding(padding, fallback = 0):
    """
    Return (px, py) as INTs.
    Accepts an int or a 2-sequence [px, py]. Any extra elements are ignored.
    """
    if isinstance(padding, (list, tuple)):
        if len(padding) == 0:
            return fallback, fallback
        if len(padding) == 1:
            v = padding[0]
            return v, v
        return padding

    return v, v


def text_frame(s):
    return kx.newline_indent(s) + "\n"

def get_capitalizer_function(key) -> callable:
    """
    returns a function based on an input for how to capitalize it.
    """
    if key == key.upper():
        return lambda x: x.upper()
    elif key == key.lower():
        if "-" in key:
            return kx.dash_case
        elif '_' in key:
            return kx.snake_case
        else:
            return kx.identity
    elif re.search("^[A-Z]", key):
        return kx.pascal_case
    else:
        return kx.camel_case

import json
def minimized_json(s):
            try:
                return json.dumps(s)
            except Exception as e:
                return s


def quick_template_clip(s, *args):
    def replacer(x):
        key = x.group(1)
        return kx.parens(key, '{}')
        
    template = kx.re.sub("\$(\d+)", replacer, s, flags = 0)
    ref = kx.array_to_dict(args)
    kx.clip(kx.brace_templater(template, ref))


# 2025-08-24 aicmp: 
def get_horizontal_length(s):
    return len(s)

def bar_wrap(s):
    s = kx.serialize_data(s)
    m = get_horizontal_length(s)
    bar = '-' * m
    return f'{bar}\n{s}\n{bar}'


def stringify(x):
    if callable(x):
        return kx.get_qualified_func_name(x)
    return kx.to_string(x)


def to_negative(idx):
    if idx > 0:
        return -1 * idx
    return idx
    
def get_note(*indexes):
    a = kx.readfile("/home/kdog3682/documents/notes/notes2.txt")
    parts = kx.split(a, '^\d\d\d\d-\d\d-\d\d.+', flags = re.M)
    return kx.smallify(kx.map(parts, lambda idx: parts[to_negative(idx)]))


def raw_code(value, lang):
        return kx.parens(lang + "\n" + value + "\n", "```")



def dirmap(dir, func, exts = []):
    files = kx.get_files(dir, exts = kx.xsplit(exts), recursive=True)
    return kx.map(files, func)

from copy import deepcopy
from typing import Any

def deep_merge(a: Any, b: Any) -> Any:
    """
    Deep-merge b into a (without mutating either) and return the result.

    Rules:
      - dict + dict: keys are unioned; values merged recursively.
      - list + list: merged index-wise; trailing elements from the longer list are appended.
      - tuple + tuple: same as list, result kept as tuple.
      - set + set: union.
      - If types differ (or either side is a scalar/other type), b replaces a.
      - If a is None -> return deepcopy(b); if b is None -> return deepcopy(a).

    Examples:
      deep_merge({"x":1,"y":{"z":[1,2]}}, {"y":{"z":[None,3,4]}}) -> {"x":1,"y":{"z":[1,3,4]}}
      deep_merge(None, {"a":1}) -> {"a":1}
      deep_merge({"a":1}, None) -> {"a":1}
    """
    if b is None:
        return deepcopy(a)
    if a is None:
        return deepcopy(b)

    # dicts: recursive merge per key
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        keys = set(a.keys()) | set(b.keys())
        for k in keys:
            if k in a and k in b:
                out[k] = deep_merge(a[k], b[k])
            elif k in a:
                out[k] = deepcopy(a[k])
            else:
                out[k] = deepcopy(b[k])
        return out

    # lists: index-wise merge, append extras
    if isinstance(a, list) and isinstance(b, list):
        n = max(len(a), len(b))
        merged = []
        for i in range(n):
            if i < len(a) and i < len(b):
                merged.append(deep_merge(a[i], b[i]))
            elif i < len(a):
                merged.append(deepcopy(a[i]))
            else:
                merged.append(deepcopy(b[i]))
        return merged

    # tuples: same as lists, keep type
    if isinstance(a, tuple) and isinstance(b, tuple):
        n = max(len(a), len(b))
        merged = []
        for i in range(n):
            if i < len(a) and i < len(b):
                merged.append(deep_merge(a[i], b[i]))
            elif i < len(a):
                merged.append(deepcopy(a[i]))
            else:
                merged.append(deepcopy(b[i]))
        return tuple(merged)

    # sets: union
    if isinstance(a, set) and isinstance(b, set):
        return deepcopy(a | b)

    # fallback: b overrides a
    return deepcopy(b)


import kevinlulee as kx


def is_relative_path(file: str):
    return file[0].isalpha() and file[-1].isalpha() and not '/home/' in os.path.expanduser(file)
def assert_relative_path(file):
    assert is_relative_path(file), f''' the provided path: "{path}" is not a relative input. (it has /home/ in it)'''

def cache_write(path, payload):
    assert_relative_path(path)
    path = kx.add_extension_if_not_present(path, 'json')
    kx.writefile(f"~/data/maelstrom/cache/{path}", payload)

def cache_read(path):
    assert_relative_path(path)
    path = kx.add_extension_if_not_present(path, 'json')
    return kx.readfile(f"~/data/maelstrom/cache/{path}")

class LiveCache:
    """
    Persistent key–value cache.
    - Preloads from `path` on init.
    - Saves to `path` on every `set`.
    - uses the base cache directory
    """

    def __init__(self, path):
        self.path = path
        self.data = cache_read(path) or {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        cache_write(self.path, self.data)
        return value


def conditional_apply(func, input, *args, **kwargs):
    if input is None:
        return 

    return func(input, *args, **kwargs)


import re
import inspect
import functools

# Matches the callable at the start of a lambda body, e.g. lambda x: pkg.fn(...)
_LAMBDA_CALL_RE = re.compile(
    r'lambda +\w+:\s*([A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)',
)

def get_anonymous_func_name(obj):
    """
    - If `obj` is a str: return it as-is.
    - If `obj` is a functools.partial: return wrapped function's name.
      If that wrapped function is a lambda, return the inner callable name
      parsed via `re.match` against the lambda source.
    - If `obj` is a lambda: return the inner callable name parsed via `re.match`.
      If no callable found at the start of the body, return '<lambda>'.
    - Otherwise (regular function): return its __name__.
    """
    if isinstance(obj, str):
        return obj

    if isinstance(obj, functools.partial):
        f = obj.func
        name = f.__name__
        if name == "<lambda>":
            src = inspect.getsource(f)
            m = _LAMBDA_CALL_RE.search(src)
            return m.group(1) if m else "<lambda>"
        return name

    # callable function (incl. lambda)
    name = obj.__name__
    if name == "<lambda>":
        src = inspect.getsource(obj)
        m = _LAMBDA_CALL_RE.search(src)
        return m.group(1) if m else "<lambda>"
    return name



import re
from typing import List, Dict, Any, Callable, Optional, Union
from datetime import datetime, timedelta

def smart_coerce(value: str) -> Union[int, float, bool, datetime, str]:
    
    if not value or not isinstance(value, str):
        return value
    
    value = value.strip()
    
    if not value:
        return value
    
    # Boolean detection
    if value.lower() in ['true', 'false', 'yes', 'no', 'on', 'off']:
        return value.lower() in ['true', 'yes', 'on']
    
    if re.match(r'^-?\d+$', value):
        return int(value)
    
    if re.match(r'^-?\d*\.\d+$', value):
        return float(value)
    
    try:
        return kx.to_datetime(value)
    except Exception as e:
        pass
    
    return value


# if __name__ == '__main__':
    # print(colon_dict('abc:\ng:\nfoo:', transformers = dict(abc = kx.identity, g = kx.identity)))

import subprocess

def bash_shell(cmd, cwd = None):
    
    cmd = " ".join(cmd) if kx.is_array(cmd) else cmd

    res = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )
    return res.stdout

def pytest(
    *paths,
    config_file="~/dotfiles/templates/pytest.ini",
    cwd=None,
    verbose: bool = True, 
    maxfail: int = 0,
    collect_only: bool = False,
    rootdir = True,
):
    parts = ["pytest"]
    paths = kx.flat(paths)

    if config_file:
        parts += ["--config-file", str(os.path.expanduser(config_file))]

    if collect_only:
        parts.append('--collect-only')

    for p in paths:
        parts.append(str(p))

    if verbose:
        parts.append("-v")

    if maxfail:
        parts += ["--maxfail", str(maxfail)]

    if rootdir:
        if rootdir == True:
            rootdir = kx.find_project_root(paths[0])
        parts += ["--rootdir", rootdir]

    return bash_shell(parts)

def create_delimited_section(top, before, after, delimiter1="=", delimiter2 = '-', n=50):
    # n = 95
    bar = delimiter * n
    bar2 = "\n" + delimiter2 * n + "\n"
    s = kx.parens(top, bar) + "\n" + bar2.join([before, after])
    return s

def parse_delimited_section(s, delimiter1="=", delimiter2="-"):
    bar = f"{delimiter1}{{3,}}"
    bar2 = f"{delimiter2}{{3,}}"
    any = "([\w\W]+?)"
    r = rf"^{bar}\n{any}\n{bar}\n+{any}\n{bar2}\n{any}(?=\n{bar}|\Z)"
    matches = re.findall(r, s, flags=re.M)

    def fix(s):
        return kx.map(s, kx.trimdent)

    return kx.map(matches, fix)

def replace_at_index(s: str, idx: int, token: str = "<cursor>") -> str:
    """
    Replace the character at position `idx` with `token`.
    Supports negative indices (like Python slicing).
    """
    if idx < 0:
        idx += len(s)
    if not (0 <= idx < len(s)):
        raise IndexError("idx out of range")

    return s[:idx] + token + s[idx + 1 :]

# print(replace_at_index('abc', 1))



from pathlib import Path
import kevinlulee as kx



class PNPM:
    """
    Simple npm helper.

    Args:
        dir (str | Path): Directory containing package.json

    Methods:
        test()   -> runs `npm run test` if a test script exists
        dev()    -> runs `npm run dev`  if a dev script exists
        publish() -> runs `npm run publish` if a publish script exists,
                     otherwise runs `npm publish`
    """

    def __init__(self, cwd, verbose = False):
        self.cwd = str(Path(cwd).expanduser())
        self.verbose = verbose

    def _has_script(self, name):
        pkg = kx.readfile(Path(self.cwd) / "package.json")
        scripts = pkg.get("scripts", {})
        return (
            isinstance(scripts, dict)
            and name in scripts
            and scripts[name] not in (None, "")
        )

    def _run(self, cmd):
        if not self._has_script(cmd):
            raise ValueError(f"No '{cmd}' script found in package.json.")
        parts = ["pnpm", "run", cmd]
        return self.cmd(parts)


    def cmd(self, parts):
        r = bash_shell(parts, cwd=self.cwd)
        if self.verbose:
            print(r)
        return r

    def test(self):
        return self._run("test")

    def test_once(self):
        return self._run("test:once")

    def dev(self):
        return self._run("dev")

    def publish(self):
        return self._run("publish")

    def production(self):
        return self._run("production")

    def install(self):
        result = self.cmd(['pnpm', 'install'])
        pat = '^npm ERR! notarget No matching version found for ([\w-]+)'
        matches = kx.unique(kx.re.findall(pat, result, flags = re.M))
        downloaded = kx.map(matches, self.install_package)

        return kx.join_text(result, downloaded)

    def install_package(self, pkg_name):
        return self.cmd(['pnpm', 'add', pkg_name + "@latest"])

# pnpm = PNPM('~/projects/webdev/fs-view/', verbose = True)
# pnpm.test_once()
# print(pnpm.install())
# pnpm.install_package('react-fzf')


class FunctionalCache:
    def __init__(self, func):
        """
        Initialize the cache with a function to be memoized.
        
        Args:
            func: The function to cache results for
        """
        self.func = func
        self.cache = {}
    
    def get(self, *args, **kwargs):
        """
        Get the result for the given arguments. If not in cache, 
        compute using the stored function and cache the result.
        
        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The function result (cached or newly computed)
        """
        # Create a cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in self.cache:
            # Not in cache, compute and store
            self.cache[key] = self.func(*args, **kwargs)
        
        return self.cache[key]
