from kevinlulee.base import get_field_value, testf
import re
import itertools
from kevinlulee.typing import Selector, Union
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
    if not items: return []
    return items if isinstance(items, (list, tuple)) else [items]

def to_lines(x):
    if isinstance(x, str):
        return x.splitlines()
    else:
        return list(x)


def mapfilter(items, fn, validator = lambda x: x):
    store = []
    for item in items:
        if item is None:
            continue
        p = fn(item)
        if validator(p):
            store.append(p)
    return store

def xtest(x, selector: Selector = None, key = None, flags=0, anti=0):
    if x is None or selector is None:
        return False

    if key:
        x = get_field_value(x, key)

    def get(x):
        if isinstance(selector, str):
            return bool(re.search(selector, x, flags = flags))
        elif isinstance(selector, re.Pattern):
            return bool(selector.search(s, flags=flags))
        elif isinstance(selector, (list, tuple, set)):
            return x in selector
        elif callable(selector):
            return selector(x)
        elif isinstance(selector, dict):
            for k, v in selector.items():
                value = get_field_value(x, k)
                # print(x, k, v, value, xtest(value, v))

                if not xtest(value, v):
                    return False
            return True
        elif selector is not None:
            return selector == x

    return not get(x) if anti else get(x)

def xtestf(selector, key = None, flags=0, anti=0):
    return lambda s: xtest(s, selector, flags, anti, key, **kwargs)

def find_index(items, query, **kwargs):
    for i, item in enumerate(items):
        if xtest(item, query, **kwargs):
            return i


def find(items, query, **kwargs):
    index = find_index(items, query, **kwargs)
    if index is not None:
        return items[index]


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
def modular_increment(items, item, dir = 1):

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

from typing import Any, Iterable, Union, Callable

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

def join_delimiter(*args, delimiter = ' '):
    return delimiter.join([str(x) for x in flat(args)])
def merge_dicts_recursively(*dicts):
    """
    Creates a dict whose keyset is the union of all the
    input dictionaries.  The value for each key is based
    on the first dict in the list with that key.

    dicts later in the list have higher priority

    When values are dictionaries, it is applied recursively
    """
    result = dict()
    all_items = itertools.chain(*[d.items() for d in dicts if d])
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



def filtered(items, selector: Selector = exists):
    if not selector:
        return items

    fn = testf(selector)
    if not fn:
        return items 
    if isinstance(items, dict):
        return {k: v for k, v in items.items() if fn(v)}
    return [ item for item in items if fn(item) ] 


def walk(x, fn):
    nargs = fn.__code__.co_argcount

    def walker(v, k, parent, depth):

        if isinstance(v, (tuple, list, set)):
            items = [walker(el, k, v, depth + 1) for el in v]
            return filtered(items)

        if isinstance(v, dict):
            return {
                a: walker(b, a, v, depth + 1) for a, b in v.items()
            }

        match nargs:
            case 1: return fn(v)
            case 2: return fn(v, k)
            case 3: return fn(v, k, parent)
            case 4: return fn(v, k, parent, depth)

    return walker(x, None, None, 0)

def reduce2(items, fn, *args, **kwargs):
    '''
        desc: 
            the callback only takes one argument (v)
            not the standard (k, v)

            the rest of *args and **kwargs are injected
            into the callback
    '''
    store = {}

    for k, v in items.items():
        value = fn(k, v, *args, **kwargs)
        if value is not None:
            if isinstance(value, tuple):
                a, b = value
                store[a] = b
            else:
                store[k] = value
    return store

def reduce(o, fn, *args, **kwargs):
    store = {}

    for k, v in o.items():
        value = fn(v, *args, **kwargs)
        if value is not None:
            store[k] = value
    return store


def on_off(state, key, on, off):
    if getattr(state, key, None):
        setattr(state, key, 0)
        off()
    else:
        setattr(state, key, 1)
        on()


def assign_fresh(*dicts: dict) -> dict:
    result = {}
    for d in dicts:
        if not d:
            continue  # Skip empty dictionaries
        for key, value in d.items():
            if key not in result or result[key] is None:
                result[key] = value
    return result



def merge_dicts(*dicts):
    return {k: v for d in dicts for k, v in d.items() if d}



def split_dict(d, keys):
    a = {}
    b = {}
    for k,v in d.items():
        if k in keys:
            a[k] = v
        else:
            b[k] = v
    return a, b

def map(x: Iterable, *args, callback = None, template = None, key = None, keys = None) -> Union[dict, list]:
    if isinstance(x, (list, tuple, set)):
        if template:
            return [template.format(el) for el in x]
        if callback:
            return [callback(el, *args) for el in x]
        if key:
            return [(get_field_value(el, key)) for el in x]
    raise Exception('only list like entries')


def filter_none(data):
    if isinstance(data, list):
        return [x for x in data if x is not None]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}
    else:
        raise Exception("only lists and dicts")


def partition_by_functions(data, *funcs):
    """
    Returns:
    - A list of partitions where:
      - Each partition corresponds to items matching each function
      - The last partition contains all remaining items not matched by any function
    """
    result = []
    remaining = list(data)
    
    # Process each function
    for func in flat(funcs):
        matched = []
        not_matched = []
        
        # Apply the current function to each remaining item
        for item in remaining:
            if func(item):
                matched.append(item)
            else:
                not_matched.append(item)
                
        # Add matched items to the result
        result.append(matched)
        
        # Update remaining items for the next function
        remaining = not_matched
    
    # Add any remaining unmatched items as the last partition
    result.append(remaining)
    
    return result


def dictf(ref):
    def callback(key):
        return ref[key] if isinstance(ref, dict) else getattr(ref, key)
    return callback


def flat_map(items, fn):
    return [fn(el) for el in flat(items)]
