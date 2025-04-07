from kevinlulee.string_utils import testf


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


def find_index(items, query, key = None):
    validate = testf(query, key)
    for i, item in enumerate(items):
        if validate(item):
            return i


def find(items, fn, key = None):
    index = find_index(items, fn, key)
    if index is not None:
        return items[index]


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

def partition(arr, n=2):
    if len(arr) <= 1:
        return arr

    def by_numbers(arr, n):
        store = []
        for i in range(0, len(arr), n):
            store.append(arr[i : i + n])
        return store

    def by_functions(arr, f):
        store = [[], []]
        for item in arr:
            if f(item):
                store[0].append(item)
            else:
                store[1].append(item)
        return store

    if callable(n):
        return by_functions(arr, n)
    if isinstance(n, int):
        return by_numbers(arr, n)

def pop(items, x, key = None):
    index = find_index(items, x, key)
    if index is not None:
        return items.pop(index)


def flat(*items):
    def runner(items):
        for item in items:
            if isinstance(item, (list, tuple)):
                runner(item)
            elif item is not None or item != 0:
                store.append(item)

    store = []
    runner(items)
    return store

# print(find_index([1,2,3], '2'))
