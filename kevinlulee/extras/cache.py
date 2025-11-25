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


