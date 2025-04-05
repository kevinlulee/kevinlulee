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



def modular_increment(items, item, dir = 1):

    def modular_increment_indexes(items, i, dir):
        if dir == 1:
            if len(items) - 1 == i:
                return 0
            else:
                return i + 1
        else:
            if i == 0:
                return len(items) - 1
            else:
                return i - 1

    def modular_increment_values(items, item, dir):
        i = items.index(item)
        return items[modular_increment_indexes(items, i, dir)]
        
    if isinstance(item, int):
        return modular_increment_indexes(items, item, dir)
    else:
        return modular_increment_values(items, item, dir)
