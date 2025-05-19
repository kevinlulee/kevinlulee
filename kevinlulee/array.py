from __future__ import annotations
class Array:
    def __init__(self, items=None):
        self.items = list(items) or []

    def insert(self, index, item):
        self.items.insert(index, item)
        return self

    def extend(self, items):
        if isinstance(items, Array):
            self.items.extend(items.items)
        else:
            self.items.extend(items)
        return self

    def append(self, item):
        self.items.append(item)
        return self

    def map_func(self):
        raise Exception('abstract')

    def filter_func(self):
        raise Exception('abstract')

    def map(self, func = None) -> Array:
        func = func or self.map_func
        return Array([func(x) for x in self.items])

    def filter(self, func = None):
        func = func or self.filter_func
        return Array([x for x in self.items if func(x)])

    def join(self):
        return join_text(self.items)

    def __repr__(self):
        return self.map(str).join().strip()

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)
