
from __future__ import annotations
import kevinlulee as kx

import json
import hashlib
from functools import wraps
from pathlib import Path


class PersistentFileCache:
    """Simple cache that persists to disk and reads from file when available."""
    
    def __init__(self, cache_file=None, verbose = False, serializer = lambda x: x):
        self.cache_file = cache_file
        self.cache = {}
        self.serializer = serializer
        self.verbose = verbose
    
    def _load_from_file(self):
        """Load cache from file if it exists."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.cache = {}
    
    def _save_to_file(self):
        """Save cache to file."""
        kx.writefile(self.cache_file, self.cache, verbose=self.verbose)
    
    def _make_key(self, args, kwargs):
        """Create a hashable key from function arguments."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """Get value from cache."""
        return self.cache.get(key)
    
    def put(self, key, value):
        """Put value in cache and save to file."""
        self.cache[key] = self.serializer(value)
        self._save_to_file()
    
    def __call__(self, func):
        """Decorator to cache function results."""

        key = func.__name__
        if self.cache_file is None:
            self.cache_file = Path(f'~/data/persistent-file-cache/{key}.json').expanduser()
            self._load_from_file()

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(args, kwargs)
            
            # Check if result is cached
            cached_result = self.get(key)
            if cached_result is not None:
                if self.verbose: print(f"Cache hit for '{func.__name__}'")
                return cached_result
            
            # Compute result and cache it
            if self.verbose: print(f"Cache miss for \"{func.__name__}\", computing...")
            result = func(*args, **kwargs)
            if not result:
                if result == 0:
                    pass
                else:
                    return 
            self.put(key, result)
            return result
        
        return wrapper


# Example usage
if __name__ == "__main__":
    # Create a cache instance
    cache = PersistentFileCache(verbose = True)
    
    @cache
    def expensive_computation(x, y):
        """Simulate an expensive computation."""
        import time
        time.sleep(1)  # Simulate work
        return x ** 2 + y ** 2
    
    # First call - cache miss, will compute
    print("First call:")
    result1 = expensive_computation(3, 4)
    print(f"Result: {result1}\n")
    
    # Second call with same args - cache hit, instant return
    print("Second call (same args):")
    result2 = expensive_computation(3, 4)
    print(f"Result: {result2}\n")
    
    # Third call with different args - cache miss
    print("Third call (different args):")
    result3 = expensive_computation(5, 12)
    print(f"Result: {result3}\n")
    
