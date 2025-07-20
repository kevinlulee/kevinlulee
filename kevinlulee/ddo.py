from kevinlulee import kx

class LiveObject:
    """Base class for live data structures that automatically persist to disk."""

    def __init__(self, data_path, loader=kx.identity, dumper=kx.identity):
        self._data_path = kx.os.path.expanduser(data_path)
        self._loader = loader
        self._dumper = dumper
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
        """Load data from disk using custom loader or default method."""
        raw_data = kx.readfile(self._data_path)
        
        if raw_data is None:
            return self._default_fallback()
        return self._loader(raw_data)

    def _save(self):
        """Save data to disk using custom dumper or default method."""
        serialized_data = self._dumper(self._data)
        kx.writefile(self._data_path, serialized_data, strict=False)

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    def __repr__(self):
        return kx.serialize_data(self._data)


# Example usage with NvimKeypress



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


class TrackedList(list):
    """A list that notifies its parent when modified."""
    
    def __init__(self, data, parent_save_callback):
        super().__init__(data)
        self._parent_save = parent_save_callback
    
    def append(self, item):
        super().append(item)
        self._parent_save()
    
    def extend(self, items):
        super().extend(items)
        self._parent_save()
    
    def insert(self, index, item):
        super().insert(index, item)
        self._parent_save()
    
    def remove(self, item):
        super().remove(item)
        self._parent_save()
    
    def pop(self, index=-1):
        result = super().pop(index)
        self._parent_save()
        return result
    
    def clear(self):
        super().clear()
        self._parent_save()
    
    def reverse(self):
        super().reverse()
        self._parent_save()
    
    def sort(self, key=None, reverse=False):
        super().sort(key=key, reverse=reverse)
        self._parent_save()
    
    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._parent_save()
    
    def __delitem__(self, index):
        super().__delitem__(index)
        self._parent_save()
    
    def __iadd__(self, other):
        result = super().__iadd__(other)
        self._parent_save()
        return result
    
    def __imul__(self, other):
        result = super().__imul__(other)
        self._parent_save()
        return result


class TrackedDict(dict):
    """A dict that notifies its parent when modified."""
    
    def __init__(self, data, parent_save_callback):
        super().__init__(data)
        self._parent_save = parent_save_callback
    
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._parent_save()
    
    def __delitem__(self, key):
        super().__delitem__(key)
        self._parent_save()
    
    def clear(self):
        super().clear()
        self._parent_save()
    
    def pop(self, key, default=None):
        if default is None:
            result = super().pop(key)
        else:
            result = super().pop(key, default)
        self._parent_save()
        return result
    
    def popitem(self):
        result = super().popitem()
        self._parent_save()
        return result
    
    def setdefault(self, key, default=None):
        if key not in self:
            result = super().setdefault(key, default)
            self._parent_save()
            return result
        return super().setdefault(key, default)
    
    def update(self, other):
        super().update(other)
        self._parent_save()


class LiveArray(LiveObject):
    """A list/array that automatically persists changes to disk."""

    def _default_fallback(self):
        return []

    def _wrap_if_mutable(self, item):
        """Wrap mutable objects to track nested changes."""
        if isinstance(item, list) and not isinstance(item, TrackedList):
            return TrackedList(item, self._save)
        elif isinstance(item, dict) and not isinstance(item, TrackedDict):
            return TrackedDict(item, self._save)
        return item

    def __getitem__(self, index):
        item = self._data[index]
        wrapped = self._wrap_if_mutable(item)
        if wrapped is not item:
            # Replace the original with the wrapped version
            self._data[index] = wrapped
        return wrapped

    def __setitem__(self, index, value):
        self._data[index] = value
        self._save()

    def __delitem__(self, index):
        del self._data[index]
        self._save()

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        # For iteration, we don't need to wrap since we're not modifying
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
