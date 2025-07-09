from kevinlulee.string_utils import test
from kevinlulee.validation import is_class_constructor, is_class_instance


def get_class_methods(cls, pattern="^[a-z]") -> list[callable]:
    store = []

    def add(name, func):
        if callable(func):
            if not pattern or (pattern and test(name, pattern)):
                store.append(func)

    if is_class_constructor(cls):
        for name, func in cls.__dict__.items():
            add(name, func)
    elif is_class_instance(cls):
        for key in dir(cls):
            add(key, getattr(cls, key))

    return store
