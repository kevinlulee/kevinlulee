from copy import deepcopy
from typing import Any


def deep_merge(a: Any, b: Any) -> Any:
    """
    Deep-merge b into a (without mutating either) and return the result.

    Rules:
      - dict + dict: keys are unioned; values merged recursively.
      - list + list: merged index-wise; trailing elements from the longer list are appended.
      - tuple + tuple: same as list, result kept as tuple.
      - set + set: union.
      - If types differ (or either side is a scalar/other type), b replaces a.
      - If a is None -> return deepcopy(b); if b is None -> return deepcopy(a).

    Examples:
      deep_merge({"x":1,"y":{"z":[1,2]}}, {"y":{"z":[None,3,4]}}) -> {"x":1,"y":{"z":[1,3,4]}}
      deep_merge(None, {"a":1}) -> {"a":1}
      deep_merge({"a":1}, None) -> {"a":1}
    """
    if b is None:
        return deepcopy(a)
    if a is None:
        return deepcopy(b)

    # dicts: recursive merge per key
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        keys = set(a.keys()) | set(b.keys())
        for k in keys:
            if k in a and k in b:
                out[k] = deep_merge(a[k], b[k])
            elif k in a:
                out[k] = deepcopy(a[k])
            else:
                out[k] = deepcopy(b[k])
        return out

    # lists: index-wise merge, append extras
    if isinstance(a, list) and isinstance(b, list):
        n = max(len(a), len(b))
        merged = []
        for i in range(n):
            if i < len(a) and i < len(b):
                merged.append(deep_merge(a[i], b[i]))
            elif i < len(a):
                merged.append(deepcopy(a[i]))
            else:
                merged.append(deepcopy(b[i]))
        return merged

    # tuples: same as lists, keep type
    if isinstance(a, tuple) and isinstance(b, tuple):
        n = max(len(a), len(b))
        merged = []
        for i in range(n):
            if i < len(a) and i < len(b):
                merged.append(deep_merge(a[i], b[i]))
            elif i < len(a):
                merged.append(deepcopy(a[i]))
            else:
                merged.append(deepcopy(b[i]))
        return tuple(merged)

    # sets: union
    if isinstance(a, set) and isinstance(b, set):
        return deepcopy(a | b)

    # fallback: b overrides a
    return deepcopy(b)
