from .file_utils import writefile, readfile
from .validation import is_array

class DynamicDataObject:
    def __init__(self, file = None, debug = False):
        self._file = file
        self._debug = debug
        self._data = readfile(self._file) if self._file else None

    def _update(self):
        if self._debug:
            print("writing")
            print(self._data)
        elif self._file:
            writefile(self._file, self._data)
        else:
            print(self._data)
    def __len__(self):
        if self._data:
            return len(self._data)
        else:
            return 0

    def __iter__(self):
        if is_array(self._data):
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
                self._update()
            else:
                raise AttributeError(
                    "Cannot use attribute assignment on non-dict data."
                )

    def append(self, value):
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.append(value)
            self._update()
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
        self._update()

    def __str__(self):
        return self.__repr__(self._data)

    def __repr__(self):
        if self._data is None:
            return ""
        else:
            return json.dumps(self._data, indent=2)

    def clear(self):
        if self._data == None:
            return
        self._data = None
        self._update()

    def pop(self, key=-1):
        self._data.pop(key)
        self._update()

    def extend(self, iterable):
        if not iterable:
            return
        if self._data is None:
            self._data = []
        if isinstance(self._data, list):
            self._data.extend(iterable)
            self._update()
        else:
            raise TypeError("Cannot extend non-list data.")

    def update(self, other):
        if not other:
            return
        if self._data is None:
            self._data = {}
        if isinstance(self._data, dict):
            self._data.update(other)
            self._update()
        else:
            raise TypeError("Cannot update non-dict data.")

# ddo = DynamicDataObject()
# ddo.append('hi')
# ddo.append('hi')
# ddo.append('hi')
# ddo.clear()
# ddo['asd'] = 'a'
# ddo.asdf = 1
# ddo.append('hi')

# 
