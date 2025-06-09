from kevinlulee import kx


class LiveObject:
    """Base class for live data structures that automatically persist to disk."""

    def __init__(self, data_path):
        self._data_path = kx.os.path.expanduser(data_path)
        self._data = self._load()

    def _default_fallback(self):
        return None

    def load(self, data):
        """
        part of the public api
        """
        self._data = data
        self._save()

    def _load(self):
        return kx.readfile(self._data_path) or self._default_fallback()

    def _save(self):
        kx.writefile(self._data_path, self._data, strict=False)

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    def __repr__(self):
        return kx.serialize_data(self._data)


class LiveDict(LiveObject):
    """A dictionary that automatically persists changes to disk."""

    def _default_fallback(self):
        return {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._save()

    def __delitem__(self, key):
        del self._data[key]
        self._save()

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"LiveDict({self._data!r})"

    def get(self, key, default=None):
        return self._data.get(key, default)

    def pop(self, key, default=None):
        if default is None:
            result = self._data.pop(key)
        else:
            result = self._data.pop(key, default)
        self._save()
        return result

    def update(self, other):
        self._data.update(other)
        self._save()

    def clear(self):
        self._data.clear()
        self._save()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def setdefault(self, key, default=None):
        if key not in self._data:
            self._data[key] = default
            self._save()
        return self._data[key]


class LiveArray(LiveObject):
    """A list/array that automatically persists changes to disk."""

    def _default_fallback(self):
        return []

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value
        self._save()

    def __delitem__(self, index):
        del self._data[index]
        self._save()

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"LiveArray({self._data!r})"

    def append(self, item):
        self._data.append(item)
        self._save()

    def extend(self, items):
        self._data.extend(items)
        self._save()

    def insert(self, index, item):
        self._data.insert(index, item)
        self._save()

    def remove(self, item):
        self._data.remove(item)
        self._save()

    def pop(self, index=-1):
        result = self._data.pop(index)
        self._save()
        return result

    def clear(self):
        self._data.clear()
        self._save()

    def reverse(self):
        self._data.reverse()
        self._save()

    def sort(self, key=None, reverse=False):
        self._data.sort(key=key, reverse=reverse)
        self._save()

    def index(self, item, start=0, stop=None):
        if stop is None:
            return self._data.index(item, start)
        return self._data.index(item, start, stop)

    def count(self, item):
        return self._data.count(item)

    def copy(self):
        """Returns a regular list copy (not a LiveArray)."""
        return self._data.copy()
