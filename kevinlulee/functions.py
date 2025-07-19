import kevinlulee as kx

def colon_dict(s, keys = None, allow_repeated_keys = False, transformers = None):
    """
        when allow_repeated_keys is true, 
        items with the same keys are grouped as arrays

        be careful! 
        any line which starts with \w+: will be captured.

        transformers is a source of keys, if keys is not provided.
    """

    if transformers and not keys:
        keys = transformers.keys()
    regex =  kx.re_wrap(keys, "^($1): *") if keys else "^([.\w-]+): *" 
    parts = kx.split(s, regex, flags=kx.re.M)
    items = kx.partition(parts)


    storage = kx.defaultdict(list)
    for a, b in items:
        base = kx.coerce_argument(b)
        value = transformers[a](base) if transformers and a in transformers else base
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

