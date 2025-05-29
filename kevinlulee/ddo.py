from kevinlulee import writefile, readfile, kx
from kevinlulee.file_utils import serialize_data


class DynamicDataObject:
    def _update(self):
        pass

    def __init__(self, data=None):
        self._data = data

    def __len__(self):
        if self._data:
            return len(self._data)
        else:
            return 0

    def __iter__(self):
        if isinstance(self._data, (list, tuple)):
            for arg in self._data:
                yield arg

        elif is_object(self._data):
            for k, v in self._data.items():
                yield (k, v)

    def __getattr__(self, name):
        if self._data is None:
            raise AttributeError("No data structure initialized yet.")
        if isinstance(self._data, dict):
            return self._data.get(name)
        raise AttributeError("Cannot use getattr on non-dict data.")

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            if self._data is None:
                self._data = {}
            if isinstance(self._data, dict):
                self._data[name] = value
            else:
                raise AttributeError(
                    "Cannot use attribute assignment on non-dict data."
                )
            self._update()

    def append(self, value):
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.append(value)
        else:
            raise TypeError("Cannot append to non-list data.")
        self._update()

    def __getitem__(self, key):
        if self._data is None:
            raise KeyError("No data structure initialized yet.")
        return self._data[key]

    def __setitem__(self, key, value):
        if self._data is None:
            if isinstance(key, int):
                self._data = []
            else:
                self._data = {}
        self._data[key] = value
        self._update()

    def clear(self):
        if self._data == None:
            return
        data = self._data
        if isinstance(self._data, dict):
            self._data = {}
        else:
            self._data = []
        self._update()
        return data

    def pop(self, key=-1):
        self._data.pop(key)
        self._update()

    def update(self, other):
        if not other:
            return
        if self._data is None:
            self._data = {}
        if isinstance(self._data, dict):
            self._data.update(other)
        else:
            raise TypeError("Cannot update non-dict data.")
        self._update()

    def extend(self, iterable):
        if not iterable:
            return
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.extend(iterable)
        else:
            raise TypeError("Cannot extend non-list data.")
        self._update()

    @property
    def value(self):
        return self._data


import os


class LiveObject:
    """Base class for live data structures that automatically persist to disk."""

    def __init__(self, data_path, loader=None, dumper=None):
        self.data_path = os.path.expanduser(data_path)
        self.loader = loader or self._default_loader
        self.dumper = dumper or self._default_dumper
        self._data = self._load()

    def _default_loader(self, data):
        return data

    def _default_dumper(self, data):
        return data

    def _default_fallback(self):
        """Override in subclasses to provide appropriate default data structure."""
        return None

    def _load(self):
        try:
            loaded_data = kx.readfile(self.data_path)
            return (
                self.loader(loaded_data)
                if loaded_data is not None
                else self._default_fallback()
            )
        except:
            return self._default_fallback()

    def _save(self):
        kx.writefile(self.data_path, self.dumper(self._data), strict=False)

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)


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
