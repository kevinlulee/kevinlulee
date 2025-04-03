import os
import functools
import pickle
import hashlib
from pathlib import Path

CACHE_DIR = '~/.kdog3682/snapshots/pickles'

def snapshotter(func):
    """
    Decorator that caches the output of a function based on its arguments.
    
    If `cached=True` is passed when calling the decorated function:
    - It generates a unique cache key from the arguments.
    - It checks for a cached result in the cache dir using that key.
    - If a snapshot exists, it loads and returns it.
    - Otherwise, it computes the result, stores it, and returns it.
    
    """
    def _make_cache_key(args, kwargs):
        key = pickle.dumps((args, kwargs))
        return hashlib.md5(key).hexdigest()

    @functools.wraps(func)
    def wrapper(*args, cached=True, verbose = True, **kwargs):
        if not cached:
            return func(*args, **kwargs)

        cache_dir = Path(os.path.expanduser(CACHE_DIR))
        cache_dir.mkdir(parents=True, exist_ok=True)

        key = _make_cache_key(args, kwargs)
        cache_file = cache_dir / f'{key}.pkl'

        if cache_file.exists():
            with cache_file.open('rb') as f:
                if verbose:
                    print('returning existant pickled value')
                return pickle.load(f)

        result = func(*args, **kwargs)

        with cache_file.open('wb') as f:
            pickle.dump(result, f)

        return result
    return wrapper

