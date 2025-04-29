from .date_utils import *
from .file_utils import *
from .string_utils import *
from .text_tools import *
from .module_utils import *
from .base import *
from .validation import *
from .ao import *
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt
from .bash import *
from .ripgrep import *
from .git import GitRepo


import inspect
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


def uncomment(s):
    r = '^( *)(?:#+|//+|"|--+) +'
    return re.sub(r , lambda x: x.group(1), s, flags = re.M)

def pycall(*args, **kwargs):
    return pythonfmt.call(*args, **kwargs)


def get_required_args(func):
    p = inspect.getfullargspec(func)
    delta = len(p.args) - len(p.defaults or [])
    required_args = p.args[0:delta]
    return required_args


def hashify(key):
    import hashlib
    return hashlib.md5(key).hexdigest()


def representative(self, *args, **kwargs):
    return pycall(nameof(self), *args, **kwargs)



def breaker(max_iterations=1000):
    """
    Function to prevent infinite loops by raising an exception after a certain number of iterations.
    
    Args:
        max_iterations (int): Maximum allowed iterations before raising an exception.
        
    Raises:
        RuntimeError: If the number of iterations exceeds max_iterations.

    Example:

        c = 0
        while c < 10:
            c += 1
            print(c)
            breaker(max_iterations=5)
    """
    # Create or increment counter attribute in the function itself
    if not hasattr(breaker, "counter"):
        breaker.counter = 0
    breaker.counter += 1
    
    # Check if iteration limit has been reached
    if breaker.counter >= max_iterations:
        breaker.counter = 0  # Reset for next use
        raise RuntimeError(f"Loop exceeded {max_iterations} iterations - possible infinite loop detected")

def curry(func, *top_args, **top_kwargs):
    def inner(*args, **kwargs):
        return func(*args, *top_args, **kwargs, **top_kwargs)

    return inner


def tern(*args):
    l = len(args)
    if l == 2:
        a, b = args
        return a if exists(a) else b
    if l == 3:
        a, b, c = args
        return b if exists(a) else c

def bartender(s, delimiter = '=', amount = 50):
    a = delimiter * amount
    p = a + "\n" + s + "\n" + a
    print(p)

def comparable(a, b):
    if a == None:
        return True

    if a and not b:
        return False

    if not a and b:
        return False

    return True
