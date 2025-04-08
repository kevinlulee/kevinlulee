class DynamicDataObject:
    def __init__(self, data = None):
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

    def append(self, value):
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.append(value)
        else:
            raise TypeError("Cannot append to non-list data.")

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

    def clear(self):
        if self._data == None:
            return
        self._data = None

    def pop(self, key=-1):
        self._data.pop(key)

    def extend(self, iterable):
        if not iterable:
            return
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.extend(iterable)
        else:
            raise TypeError("Cannot extend non-list data.")

    def update(self, other):
        if not other:
            return
        if self._data is None:
            self._data = {}
        if isinstance(self._data, dict):
            self._data.update(other)
        else:
            raise TypeError("Cannot update non-dict data.")
    @property
    def value(self):
        return self._data
