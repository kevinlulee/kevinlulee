import kevinlulee as kx


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
    for a, b in items:
        base = kx.coerce_argument(b)
        value = (
            transformers[a](base)
            if transformers and a in transformers
            else base
        )
        storage[a].append(value)

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


def to_string(x):
    if isinstance(x, str):
        return str

    if callable(x):
        return kx.inspect.getsource(x)

    try:
        return kx.json.dumps(x, indent=2)
    except Exception as e:
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





def join(*args, delimiter = ' '):
    els = kx.flat(args)
    if els[-1] in [',', '/', '.', ' ', '\n']:
        return els[-1].join(els[:-1])
    return delimiter.join(els)
    



def bug_call(*args, **kwargs):
    from codefmt.python import pythonfmt
    caller = kx.introspect.get_caller(1).function
    call_expr = pythonfmt.call(caller, args, kwargs, condensed = True)
    print('[DEBUG]', call_expr)



def get_qualified_func_name(func):
    """
        returns Foo.bar if the func is a method or a abcde() if it is a function
    """
    mod = getattr(func, '__module__', None)
    name = func.__qualname__
    cname = kx.join(mod, name, '.')
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
