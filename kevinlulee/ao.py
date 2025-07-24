import json
from kevinlulee.base import get_field_value, testf
import re
import itertools
from kevinlulee.typing import Selector, Union
from kevinlulee.validation import (
    exists,
    is_array,
    is_dict,
    is_primitive,
    not_none,
    is_primitive_array,
    is_object_array,
)


def dotaccess(val, key):
    parts = key.split(".")
    for part in parts:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val


def smallify(arr):
    if is_array(arr):
        return arr[0] if len(arr) == 1 else arr
    else:
        return arr


def to_array(items):
    if not items:
        return []
    return items if isinstance(items, (list, tuple)) else [items]


def to_lines(x):
    if isinstance(x, str):
        return x.splitlines()
    elif is_dict(x):
        return json.dumps(x, indent=2).splitlines()
    elif is_object_array(x):
        if is_dict(x[0]):
            return json.dumps(x, indent=2).splitlines()
        else:
            return json.dumps(x, indent=2).splitlines()
    else:
        return list(x)


def mapfilter(items, fn, validator=lambda x: x):
    store = []
    for item in items:
        if item is None:
            continue
        p = fn(item)
        if validator(p):
            store.append(p)
    return store


def xtest(x, selector: Selector = None, key=None, flags=0, anti=0):
    if x is None or selector is None:
        return False

    if key:
        x = get_field_value(x, key)
        if x is None:
            return False

    def get(x):
        if isinstance(selector, str):
            return bool(re.search(selector, x, flags=flags))
        elif isinstance(selector, re.Pattern):
            return bool(selector.search(x, flags=flags))
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


def xtestf(selector, flags=0, anti=0, key=None):
    return lambda s: xtest(s, selector, flags, anti, key)


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


def modular_increment_values(items, key, dir = 1):
    if key is None:
        return items[0]
    i = items.index(key)
    return items[modular_increment_indexes(items, i, dir)]
def modular_increment(items, item, dir=1):

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


def pop(items, x, key=None):
    index = find_index(items, x, key)
    if index is not None:
        return items.pop(index)


def flat(*items, validator=exists):
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
    flatten_array_values=False,
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
            assert (
                key
            ), "Must provide a key (str or callable) when grouping dicts."
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
    return " ".join(flat(args))


def join_delimiter(*args, delimiter=" "):
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
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
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
    return [item for item in items if fn(item)]


def walk(x, fn):
    nargs = fn.__code__.co_argcount

    def walker(v, k, parent, depth):
        if isinstance(v, (tuple, list, set)):
            items = [walker(el, k, v, depth + 1) for el in v]
            return filtered(items, not_none)

        if isinstance(v, dict):
            return {a: walker(b, a, v, depth + 1) for a, b in v.items()}

        match nargs:
            case 1:
                return fn(v)
            case 2:
                return fn(v, k)
            case 3:
                return fn(v, k, parent)
            case 4:
                return fn(v, k, parent, depth)

    return walker(x, None, None, 0)


def reduce2(items, fn, *args, **kwargs):
    """
    desc:
        the callback only takes one argument (v)
        not the standard (k, v)

        the rest of *args and **kwargs are injected
        into the callback
    """
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


def merge_dicts(*dcts):
    store = {}
    for dct in dcts:
        if dct:
            for k, v in dct.items():
                store[k] = v

    return store


def split_dict(d, keys):
    a = {}
    b = {}
    for k, v in d.items():
        if k in keys:
            a[k] = v
        else:
            b[k] = v
    return a, b


def map(
    x: Iterable, *args, callback=None, template=None, key=None, keys=None
) -> Union[dict, list]:
    if isinstance(x, (list, tuple, set)):
        if template:
            return [template.format(el) for el in x]
        if callback:
            return [callback(el, *args) for el in x]
        if key:
            return [(get_field_value(el, key)) for el in x]
    raise Exception("only list like entries")


def filter_none(data):
    if isinstance(data, (list, tuple, set)):
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
        fallback = key
        return (
            ref.get(key, fallback)
            if isinstance(ref, dict)
            else getattr(ref, key, fallback)
        )

    return callback


def flat_map(items, fn):
    return [fn(el) for el in flat(items)]


def filter_seen(items, key=None):
    if key:
        store = []
        seen = set()
        for item in items:
            ref = item.get(key)
            if ref in seen:
                continue
            seen.add(ref)
            store.append(item)
        return store
    else:
        return list(set(items))


def dict_partition(kwargs, *funcs):
    """
    Partition a dictionary into multiple bins based on functions.

    Args:
        kwargs: Dictionary to partition
        *funcs: Functions that take (key, value) and return True if item belongs in that bin

    Returns:
        List of dictionaries - one for each function, plus a default bin at the end
    """
    # Initialize bins: one for each function + one default bin
    bins = [dict() for _ in range(len(funcs) + 1)]

    for key, value in kwargs.items():
        placed = False

        # Try each function in order
        for i, func in enumerate(funcs):
            if func(key, value):
                bins[i][key] = value
                placed = True
                break

        # If no function matched, put in default bin (last bin)
        if not placed:
            bins[-1][key] = value

    return bins


def list_partition(items, *funcs):
    # Initialize bins: one for each function + one default bin
    bins = [list() for _ in range(len(funcs) + 1)]

    for item in items:
        placed = False

        for i, func in enumerate(funcs):
            if func(item):
                bins[i].append(item)
                placed = True
                break

        if not placed:
            bins[-1].append(item)

    return bins


def modify_array(items, func, key=None):
    for i, item in enumerate(items):
        value = func(item)
        if value is not None:
            if key:
                items[i][key] = value
            else:
                items[i] = valuee
    return items


def edit_dict(dct, key, editor: dict):
    """
    the keys of the editor dict will determine what gets edited
    """
    section = dct.get(key)
    if not section:
        return dct

    def apply(base, v):
        if isinstance(base, (list, tuple)):
            return [v(el) for el in base]
        else:
            return v(base)

    if isinstance(editor, dict):
        for k, v in editor.items():
            to_be_edited = section.get(k)
            if to_be_edited is not None:
                new_value = apply(to_be_edited, v)
                if new_value is not None:
                    section[k] = new_value
    else:
        raise Exception("todo")

    return dct


def array_to_dict(data, key):
    store = {}
    for arg in data:
        store[key(arg) if callable(key) else arg[key]] = arg
    return store


def unique(x):
    return [el for el in set(x) if el is not None]

def dict_setter(base, *args):
    def merge(a, b):
        if is_array(b):
            return a + b
        if is_object(b):
            return deep_assign(a, b)
        return b

    first = args[0] if len(args) else None
    if not first:
        return base
    if is_object(first):
        return deep_assign(base, first)

    ref = base
    length = len(args) - 1
    for i in range(length):
        arg = args[i]
        if i == length - 1:
            value = args[i + 1]
            current = ref.get(arg)
            ref[arg] = merge(current, value)
            return base
        else:
            if arg not in ref:
                ref[arg] = {}
            ref = ref[arg]

def dict_getter(base, *args):
    if not args[-1]:
        return 
    length = len(args)
    if length == 1 and "." in args[0]:
        args = args[0].split(".")
        length = len(args)

    try:
        if length == 1:
            return base[args[0]]
        if length == 2:
            return base[args[0]][args[1]]
        if length == 3:
            return base[args[0]][args[1]][args[2]]
        if length == 4:
            return base[args[0]][args[1]][args[2]][args[3]]
        if length == 5:
            return base[args[0]][args[1]][args[2]][args[3]][args[4]]
    except Exception as e:
        return None



# def object_getter(o, key):
#     if not is_string(key):
#         return
#     if is_object(o) and key in o:
#         return o[key]
#     elif hasattr(o, key):
#         return getattr(o, key)
#
#
# def gather_object(o, keys):
#     def gatherer(key):
#         value = object_getter(o, key)
#         if value != None:
#             return (key, value)
#
#     return reduce(list(keys), gatherer)
