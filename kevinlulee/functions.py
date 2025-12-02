from copy import deepcopy
import re
from _collections_abc import dict_values, dict_keys, dict_items
import shutil
import kevinlulee as kx
import functools

from kevinlulee.ao import reduce2
from kevinlulee.base import identity
from kevinlulee.validation import existant, exists
from typing import List, Tuple, Optional







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
        if kx.test(value, '#let|#import|\) *= *{'):
            return 'typst'

        if kx.test(value, '^ *(?:function \w+|const +\w+ *=)', flags = kx.re.M):
            return 'typescript'

        if kx.test(value, '^ *def +\w+\(|TypedDict|^from ', flags = kx.re.M):
            return "python"

        return 'python'
        raise Exception('unable to infer a language')

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


from kevinlulee.extras.brace_templater import brace_templater
from kevinlulee.extras.deep_merge import deep_merge
from kevinlulee.extras.colon_dict import colon_dict


def run_tests(tests, func):
    items = tests if isinstance(tests, (list, tuple)) else kx.to_lines(kx.trimdent(tests))
    kx.prettyprint(kx.map(items, func))


def printable(**kwargs):
    s = kx.StringBuilder()
    for k, v in kwargs.items():
        s.add_field(k, v)

    return kx.stop(s)


def file_cache(cache_path: str = '', update_on_touch=True, verbose = False, **time_opts):
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

from kevinlulee.class_introspection_ops import get_class_method_names





def get_data(key):
    raise Exception('no')
    def replacer(x):
        key = x.group(0)
        return key
        
    key = re.sub("^\w+", replacer, key, flags = 0)
    file = kx.add_extension_if_not_present(key, 'json')
    path = f'~/data/{file}'
    return kx.readfile(path)

def get_doc_string(func):
    return kx.trimdent(func.__doc__)





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


def get_horizontal_length(s):
    return len(s)

def bar_wrap(s, bar_width = None, delimiter = '-'):
    s = kx.serialize_data(s)
    m = bar_width or min(get_horizontal_length(s), 70)
    bar = delimiter * m
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
    indexes = indexes or [-1]
    a = kx.readfile("/home/kdog3682/documents/notes/notes2.txt")
    parts = kx.split(a, '^\d\d\d\d-\d\d-\d\d.*', flags = re.M)
    return kx.smallify(kx.map(indexes, lambda idx: parts[to_negative(idx)]))


def raw_code(value, lang):
        return kx.parens(lang + "\n" + value + "\n", "```")



def dirmap(dir, func, exts = []):
    files = kx.get_files(dir, exts = kx.xsplit(exts), recursive=True)
    return kx.map(files, func)

import kevinlulee as kx



def cache_write(path, payload):
    kx.assert_relative_path(path)
    path = kx.add_extension_if_not_present(path, 'json')
    kx.writefile(f"~/data/maelstrom/cache/{path}", payload)

def cache_read(path):
    kx.assert_relative_path(path)
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


def get_func_name(func):
    return get_anonymous_func_name(func)

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



def create_delimited_section(top, before, after, delimiter1="=", delimiter2 = '-', n=50):
    # n = 95
    top = kx.serialize_data(top)
    before = kx.serialize_data(before)
    after = kx.serialize_data(after)
    bar = delimiter1 * n
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


def run_callback(callback, *args, **kwargs):
    result = callback(*args, **kwargs) if kx.get_parameters(callback) else callback()
    return result

def replicate(x, n=5):
    return kx.map(n, lambda _: deepcopy(x))


def ternf(a, b, c = identity):
    def _tern(x):
        if (callable(a) and a(x)) or isinstance(x, a):
            return b(x)
        else:
            return c(x)
        
    return _tern

def collect_directories(dir, query):
    return kx.fdfind(
        dirs=[dir],
        query=query,
        only_directories=True,
    )


def hit(funcs, *args, **kwargs):
    for func in funcs:
        m = func(*args, **kwargs)
        if m is not None:
            return m

    

def check(value, validator):
    assert validator(value), f"{value} does not meet validation requirements."
    return value


def call(key, *args, **kwargs):
    return kx.run_module_func(f'kevinlulee.extras.{key}', *args, **kwargs)



def infer_nargs(template: str) -> int:
    nums = re.findall(r"\$(\d+)", template)
    return len(set(nums))


def id_from_index(i: int) -> str:
    s = ""
    i0 = i
    while True:
        i0, rem = divmod(i0, 26)
        s = chr(65 + rem) + s
        if i0 == 0:
            break
        i0 -= 1
    return s.upper()




def pathf(*segments):
    def path_func(*args):
        return kx.path_join(*segments, *kx.map(args, str))

    return path_func

def show_matplotlib(plt):
    """Save matplotlib figure to ~/scratch/temp.png and open in browser.
    
    Parameters:
    - plt: matplotlib.pyplot instance
    
    Returns:
    - filepath: Path object to the saved file
    """

    import webbrowser
    from pathlib import Path
    # Expand home directory
    scratch_dir = Path.home() / "scratch"
    scratch_dir.mkdir(exist_ok=True)
    
    filepath = scratch_dir / "temp.png"
    
    # Save the figure
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f"Saved to: {filepath}")
    
    # Open in web browser
    webbrowser.open(f'file://{filepath.absolute()}')
    
    return filepath


def run_script(key, *args, **kwargs):
    """
    a handy function for quickly running scripts located in nvim.scripts
    the requirement is that the main function matches the module name.
    """

    places = [
        'nvim.scripts',
        'kevinlulee.scripts'
    ]
    for place in places:
        func_key = f'{place}.{key}'
        func = kx.get_implicit_module_func(func_key, strict=False)
        if func:
            return func(*args, **kwargs)

def extf(*filetypes):
    def func(path):
        return kx.resolve_filetype(path) in filetypes

    return func



def wrap_with_dollar_signs(base):
    base = str(base)
    if base.startswith("$"):
        return base
    s = kx.parens(base, "$")
    return s


def stop(*args):
    if args:
        for arg in args:
            kx.pretty_print(arg)

    raise Exception("__EXIT__")



import re
from typing import Callable, Pattern, Union


def preserve_and_transform(
    text: str,
    operation: Callable[[str], str],
    pattern: Union[str, Pattern] = r'\$\$\$[^$]+\$\$\$|\$[^$]+\$|```[^`]+```|`[^`]+`',
    placeholder: str = "<<<PLACEHOLDER>>>"
) -> str:
    """
    Remove content matching a pattern, perform an operation, then restore it.
    
    Args:
        text: Input string to process
        pattern: Regex pattern to temporarily remove (can be string or compiled Pattern)
        operation: Function to apply to text with patterns removed
        placeholder: Template for temporary placeholders (must contain {})
    
    Returns:
        Processed string with original patterns restored
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    # Store removed content
    removed_content = []
    
    def store_and_replace(match):
        removed_content.append(match.group(0))
        return placeholder
    
    # Remove matching patterns
    text_without_patterns = pattern.sub(store_and_replace, text)
    
    # Perform operation
    processed_text = operation(text_without_patterns)
    
    # Restore patterns
    def replacer(x):
        return removed_content.pop(0)
    processed_text = re.sub(re.escape(placeholder), replacer, processed_text)
    return processed_text



def split_chunks(arr, n=2):
    size = (len(arr) + n - 1) // n
    return [arr[i:i+size] for i in range(0, len(arr), size)]



def regex_boundary(key):
    return f'\\b{key}\\b'



def bullet_list(s):
    
    def bullet(s):
        lines = "- " + kx.trimdent(s)
        lines = lines.split("\n")
        return "\n".join(
            [lines[0]] + kx.map(lines[1:], lambda line: kx.indent(line, 2))
        )
    

    bullets = kx.map(s, bullet)
    return kx.join_text(bullets)



def sort_by_date(files, reverse=True):
    """
    the most recent dates come first
    """
    
    return sorted(files, key=kx.to_datetime, reverse=reverse)


def get_cache_path(name: str, key="misc") -> str:
    """Get cache file path for directory."""
    dir_hash = str(abs(hash(name)))
    return os.path.join(kx.CACHE_DIRECTORY, key, f"{dir_hash}.json")
