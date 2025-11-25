import functools
import json
import os
from typing import Callable, Any
import kevinlulee as kx

def get_name(obj):
    """
    Try several ways to extract a 'name' value from arbitrary objects:
    - attribute: obj.name
    - method: obj.name() or obj.get_name()
    - dict-style: obj["name"]
    - mapping: obj.get("name")
    """
    # 1. attribute
    if hasattr(obj, "name"):
        val = getattr(obj, "name")
        if callable(val):
            return val()
        return val

    # 2. get_name() method
    if hasattr(obj, "get_name") and callable(obj.get_name):
        return obj.get_name()

    # 3. dict indexing
    try:
        return obj["name"]
    except Exception:
        pass

    # 4. mapping .get()
    try:
        return obj.get("name")
    except Exception:
        pass

    return None


def cache_on_file(path: str, key: Callable[..., Any] = get_name):
    """
    Decorator factory that caches function results in an on-disk index.
    - key: callable(*args, **kwargs) -> a hashable key (usually str/int)
    - path: path to persistent index (used with kx.readfile / kx.writefile if available,
            otherwise a JSON file fallback)[]
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # compute cache key for this call
            cache_key = key(*args, **kwargs) if callable(key) else key

            index = kx.readfile(path) or {}
            if cache_key in index:
                return index[cache_key]

            result = fn(*args, **kwargs)
            index[cache_key] = result
            kx.writefile(path, index)
            return result

        return wrapper

    return decorator


