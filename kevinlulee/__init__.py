from .date_utils import *
from .file_utils import *
from .string_utils import *
from .text_tools import *
from .module_utils import *

from .bash import ripgrep, bash, fdfind, typst, python3
from .git import GitRepo
# from .configurable import myenv
from .base import *
from .validation import *
from .ao import *
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt


def representative(self, *args, **kwargs):
    if not kwargs:
        kwargs = self.__dict__
    return pythonfmt.call(nameof(self), *args, **kwargs)


import yaml

def yamload(x):
    if not x:
        return {}

    if callable(x):
        while hasattr(x, '__wrapped__'):
            x = x.__wrapped__
        x = getattr(x, '__doc__')

    if not x:
        return {}

    s = trimdent(x)
    m = yaml.safe_load(s)

    if type(m) == str:
        return {}

    return m


def get_caller(offset=0, skippable=[]) -> inspect.FrameInfo:
    KNOWN_IMPLICIT_CALLERS = [
        "get_caller",
    ]
    backwards = ["must"]
    skippableA = [
        "log",
        "log_error",
        "__init__",
        "handler",
        "decorator",
        "wrapper",
    ]

    import inspect
    items: list = inspect.stack()

    # find_index
    start = find_index(
        items,
        lambda x: x.function in KNOWN_IMPLICIT_CALLERS,
    )
    if start == -1:
        return
    start += 1
    length = len(items)
    skip = skippable + skippableA
    while start < length:
        next = items[start]
        if next.function in backwards:
            return items[start - 1]
        if next.function in skip:
            start += 1
            continue
        if offset:
            next = items[start + offset]
        return next


def join_spaces(*args):
    return ' '.join(flat(args))
