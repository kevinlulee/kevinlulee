def dotaccess(val, key):
    parts = key.split(".")
    for part in parts:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val


def smallify(arr):
    return arr[0] if len(arr) == 1 else arr


def to_array(items):
    return items if isinstance(items, (list, tuple)) else [items]


def mapfilter(items, fn, validator = lambda x: x):
    store = []
    for item in items:
        p = fn(item)
        if validator(p):
            store.append(p)
    return store


def find_index(items, fn):
    for i, item in enumerate(items):
        if fn(item):
            return i
