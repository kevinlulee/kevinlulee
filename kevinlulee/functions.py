import re
from _collections_abc import dict_values, dict_keys, dict_items
import shutil
import kevinlulee as kx
import functools

from kevinlulee.ao import reduce2
from kevinlulee.validation import existant, exists


def colon_dict(s, keys=None, allow_repeated_keys=False, transformers=None):
    """
    when allow_repeated_keys is true,
    items with the same keys are grouped as arrays

    be careful!
    any line which starts with \w+: will be captured.

    transformers is a source of keys, if keys is not provided.
    """

    if transformers and not keys:
        keys = transformers.keys()
    regex = kx.re_wrap(keys, "^($1): *") if keys else "^([.\w-]+): *"
    parts = kx.split(s, regex, flags=kx.re.M)
    items = kx.partition(parts)

    storage = kx.defaultdict(list)
    try:
        for a, b in items:
            base = kx.coerce_argument(b)
            value = (
                transformers[a](base)
                if transformers and a in transformers
                else base
            )
            storage[a].append(value)
    except Exception as e:
        kx.stop(items)
        raise e

    store = {}
    for k, v in storage.items():
        if len(v) == 1:
            store[k] = v[0]
        elif allow_repeated_keys:
            store[kx.pluralize(k)] = v
        else:
            store[k] = v[-1]

    return store


def rpw(file, fn):
    kx.writefile(file, fn(kx.readfile(file)))

def to_text(x):
    if isinstance(x, str):
        return str

    if callable(x):
        return kx.inspect.getsource(x)

    for key in ("text", "body", "value", "content"):
        if hasattr(x, key):
            return getattr(x, key)

    return x
def to_string(x):
    if isinstance(x, str):
        return x

    if callable(x):
        return kx.inspect.getsource(x)

    for key in ("text", "body", "value", "content"):
        if hasattr(x, key):
            return getattr(x, key)

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

def mvfile(a, b):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    kx.assert_file(a)
    shutil.move(a, b)

def mvdir(a, b):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    kx.assert_directory(a)
    shutil.move(a, b)

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
    file = kx.add_extension_if_not_present(kx.dash_case(key), 'json')
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
