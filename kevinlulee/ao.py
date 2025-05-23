from kevinlulee.base import testf
from kevinlulee.typing import Selector
from kevinlulee.validation import exists, is_array


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

def to_lines(x):
    if isinstance(x, str):
        return x.splitlines()
    else:
        return list(x)


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


def flat(*items, validator = exists):
    def runner(items):
        for item in items:
            if isinstance(item, (list, tuple)):
                runner(item)
            elif validator(item):
                store.append(item)

    store = []
    runner(items)
    return store

from typing import Any, Union, Callable

def group(
    items: Union[list[tuple[str, Any]], list[dict]],
    key: Union[Callable[[Any], str], str, None] = None,
    flatten_array_values = False,
) -> dict[str, list[Any]]:
    """Groups items by a specified key or callable.

    Args:
        items: A list of 2-element tuples/lists or dicts.
        key: A string key (for dicts) or a callable to extract the grouping key.

    Returns:
        A dict mapping keys to lists of grouped values.
    """
    assert isinstance(items, (list, tuple)), "Input must be a list or tuple."

    result = {}
    for item in items:
        if isinstance(item, dict):
            assert key, "Must provide a key (str or callable) when grouping dicts."
            iden = item[key] if isinstance(key, str) else key(item)
            result.setdefault(iden, []).append(item)
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            iden, value = item
            if flatten_array_values and is_array(value):
                result.setdefault(iden, []).extend(value)
            else:
                result.setdefault(iden, []).append(value)
        else:
            raise ValueError("Items must be 2-element tuple/list or dict.")
    return result


def join_spaces(*args):
    return ' '.join(flat(args))

def merge_dicts_recursively(*dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.

    dicts later in the list have higher priority

    When values are dictionaries, it is applied recursively
    """
    result = dict()
    all_items = it.chain(*[d.items() for d in dicts])
    for key, value in all_items:
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_recursively(result[key], value)
        else:
            result[key] = value
    return result


def deep_map(obj, callback):
    if isinstance(obj, dict):
        for key, value in obj.items():
            updated = deep_map(value, callback)
            if updated is not None:
                obj[key] = updated
    elif isinstance(obj, (list, tuple)):
        seq_type = type(obj)
        updated_seq = []
        changed = False
        for item in obj:
            updated = deep_map(item, callback)
            updated_seq.append(updated if updated is not None else item)
            changed = changed or updated is not None
        return seq_type(updated_seq) if changed else None
    else:
        return callback(obj)



def filtered(items, selector: Selector):
    if not selector:
        return items

    fn = testf(selector)
    return [ item for item in items if fn(item) ] 

