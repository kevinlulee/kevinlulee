"""
Caching decorators: daily (calendar-based) and file_time (mtime-based).
"""
import os
import json
import functools
from collections import Counter
from datetime import date

DAILY_CACHE_DIR = os.path.expanduser("~/.cache/daily")
FILE_TIME_CACHE_PATH = os.path.expanduser("~/.cache/file_time_cache.json")


def _cache_key(func, args, kwargs):
    return f"{func.__name__}_{hash(str((args, sorted(kwargs.items()))))}"


def daily_cache(func):
    """
    Cache results once per day, keyed by input args. Persists to disk.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = _cache_key(func, args, kwargs)
        cache_path = os.path.join(DAILY_CACHE_DIR, str(date.today()), f"{key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)
        result = func(*args, **kwargs)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(result, f)
        return result
    return wrapper


def _load_file_time_state():
    try:
        with open(FILE_TIME_CACHE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_file_time_state(state):
    os.makedirs(os.path.dirname(FILE_TIME_CACHE_PATH), exist_ok=True)
    with open(FILE_TIME_CACHE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def file_time_cache(func):
    """
    Cache results until the input file's mtime changes.
    First positional arg must be a filepath. Persists to disk.
    """
    @functools.wraps(func)
    def wrapper(filepath, *args, **kwargs):
        if not os.path.exists(filepath):
            return func(filepath, *args, **kwargs)
        state = _load_file_time_state()
        key = _cache_key(func, (filepath, *args), kwargs)
        mtime = os.path.getmtime(filepath)
        cached = state.get(key)
        if cached and cached.get("mtime") == mtime:
            return cached["result"]
        result = func(filepath, *args, **kwargs)
        state[key] = {"mtime": mtime, "result": result}
        _save_file_time_state(state)
        return result
    return wrapper


