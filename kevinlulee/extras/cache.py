"""
Decorator that caches function results based on file/directory modification times.
The cache is invalidated when the file/directory is modified.
"""

import os
import functools
from pathlib import Path
from typing import Callable, Any, Optional


def mtime_cache(path_arg: str = None, path_kwarg: str = None):
    """
    Decorator that caches function results based on file/directory modification time.
    
    The cached value is only recomputed when the file/directory is modified.
    If getting the modification time fails, the function is executed and the
    result is cached along with the current timestamp.
    
    Args:
        path_arg: Name of the positional argument that contains the path (e.g., 'filename')
        path_kwarg: Name of the keyword argument that contains the path (e.g., 'directory')
        
    Note: Specify either path_arg or path_kwarg, not both.
    
    Example:
        @mtime_cache(path_kwarg='filepath')
        def process_file(filepath, option=None):
            # expensive operation
            return result
    """
    if path_arg and path_kwarg:
        raise ValueError("Specify either path_arg or path_kwarg, not both")
    
    if not path_arg and not path_kwarg:
        raise ValueError("Must specify either path_arg or path_kwarg")
    
    def decorator(func: Callable) -> Callable:
        # Cache structure: {(func_id, path): (mtime, cached_result)}
        # Use a mutable default to persist across calls
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the path from arguments
            path = None
            
            if path_kwarg:
                path = kwargs.get(path_kwarg)
            elif path_arg:
                # Get function signature to find the argument position
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                if path_arg in param_names:
                    arg_index = param_names.index(path_arg)
                    if arg_index < len(args):
                        path = args[arg_index]
                    else:
                        path = kwargs.get(path_arg)
            
            if path is None:
                raise Exception('path not found')
                # If path not found, just execute the function
                return func(*args, **kwargs)
            
            # Convert to string path
            path_str = str(path)
            
            # Try to get the modification time
            try:
                current_mtime = os.path.getmtime(path_str)
                mtime_available = True
            except (OSError, FileNotFoundError):
                # If we can't get mtime, use None as a marker
                current_mtime = None
                mtime_available = False
            
            # Check if we have a cached value
            if path_str in cache:
                cached_mtime, cached_result = cache[path_str]
                
                if mtime_available:
                    # We have mtime - check if file hasn't changed
                    if cached_mtime == current_mtime:
                        return cached_result
                else:
                    # No mtime available now, but we have a cached result
                    # Return cached result (optimistic caching)
                    return cached_result
            
            # Compute the result
            result = func(*args, **kwargs)
            
            # Cache the result with the mtime (or None if unavailable)
            cache[path_str] = (current_mtime, result)
            
            return result
        
        # Add a method to clear the cache
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'entries': {path: mtime for path, (mtime, _) in cache.items()}
        }
        
        return wrapper
    
    return decorator


# Alternative: Decorator that automatically detects path arguments
def auto_mtime_cache(func: Callable) -> Callable:
    """
    Decorator that automatically caches based on mtime of path-like arguments.
    
    Detects arguments named 'path', 'file', 'filename', 'filepath', 'dir', 
    'directory', or 'folder' and uses their mtime for caching.
    
    Example:
        @auto_mtime_cache
        def read_config(filepath):
            # expensive operation
            return result
    """
    import inspect
    
    # Common names for path arguments
    PATH_NAMES = {'path', 'file', 'filename', 'filepath', 'dir', 'directory', 'folder', 'src_path', 'src'}
    
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    
    # Find the first parameter that looks like a path
    path_param = None
    for param in param_names:
        if param.lower() in PATH_NAMES:
            path_param = param
            break
    
    if path_param:
        # Use the mtime_cache decorator
        return mtime_cache(path_arg=path_param)(func)
    else:
        raise Exception('could not find a path_param')
        # No path parameter found, just return the function as-is
        return func


if __name__ == "__main__":
    # Example usage
    import time
    
    @mtime_cache(path_kwarg='filepath')
    def read_file(filepath, encoding='utf-8'):
        """Read and process a file (expensive operation simulation)"""
        print(f"  -> Executing function (cache miss)")
        time.sleep(0.05)  # Simulate expensive operation
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    
    # Create a test file
    test_file = '/tmp/test_cache.txt'
    with open(test_file, 'w') as f:
        f.write("Version 1")
    
    print("Call 1 (cache miss, file doesn't exist in cache):")
    result1 = read_file(filepath=test_file)
    print(f"Result: {result1}\n")
    
    print("Call 2 (cache hit, file unchanged):")
    result2 = read_file(filepath=test_file)
    print(f"Result: {result2}\n")
