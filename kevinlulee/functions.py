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

    return kx.json.dumps(x, indent=2)


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
    return delimiter.join(els)
    
