"""
Persistent mtime-based file cache.

Responsibilities:
- Load and save cache state from disk
- Validate cached paths using mtime
- Update or remove cache entries

Cache file:
~/.cache/maelstrom/mtime-file-cache.json
"""

import os
import json
from contextlib import contextmanager

CACHE_PATH = os.path.expanduser(
    "~/.cache/maelstrom/mtime-file-cache.json"
)


def _load():
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    # 2025-12-18 aicmp: json errors should still emit errors
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(state):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(state, f, indent=2)


class MTimeCache:
    def __init__(self, state):
        self._state = state

    def has(self, path):
        """
        Return True if the path exists and its mtime matches the cached value.
        """
        if not os.path.exists(path):
            return False

        cached = self._state.get(path)
        if cached is None:
            return False

        return os.path.getmtime(path) == cached

    def update(self, path):
        """
        Record the current mtime of a path (if it exists).
        """
        if os.path.exists(path):
            self._state[path] = os.path.getmtime(path)

    def pop(self, path):
        """
        Remove a path from the cache.
        """
        self._state.pop(path, None)


@contextmanager
def mtime_cache():
    """
    Context manager providing an MTimeCache instance
    with automatic load/save semantics.
    """
    state = _load()
    cache = MTimeCache(state)
    try:
        yield cache
    finally:
        _save(state)

