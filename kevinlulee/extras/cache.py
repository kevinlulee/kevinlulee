import os
import functools
from pathlib import Path
from typing import Callable, Any, Optional
import kevinlulee as kx

def mtime_cache(cache_path: str) -> Callable[[Callable], Callable]:
    """
    Decorator that caches function results based on file/directory modification times.
    The cache is invalidated when the file/directory is modified.
    """
    
    def decorator(func: Callable) -> Callable:
        cache = kx.readfile(cache_path) or {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the path from arguments
            path = kx.path_expand(args[0])
            current_mtime = int(os.path.getmtime(path))
            if path in cache:
                cached_mtime, cached_result = cache[path]
                if current_mtime == cached_mtime:
                    return cached_result
            
            # Compute the result
            result = func(*args, **kwargs)
            cache[path] = (current_mtime, result)
            kx.writefile(cache_path, cache)
            return result
        
        return wrapper
    
    return decorator


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


def cache_to_file(cache_path: str, key: Callable[..., Any] = get_name):
    """Decorator that caches function results to a file using a key function."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # compute cache key for this call
            cache_key = key(*args, **kwargs) if callable(key) else key

            index = kx.readfile(cache_path) or {}
            if cache_key in index:
                return index[cache_key]

            result = fn(*args, **kwargs)
            index[cache_key] = result
            kx.writefile(cache_path, index)
            return result

        return wrapper

    return decorator


