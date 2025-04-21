import inspect
from kevinlulee.typing import Selector
import re


def get_parameters(func):
    return list(inspect.signature(func).parameters.keys())



def display(**kwargs):
    if not kwargs:
        return 
    s = '---\n'
    for k,v in kwargs.items():
        s+= f'{k}: "{v}"\n'

    s += '---'
    print(s)



def sayhi(name="Bob", prefix="howdy"):
    return f"{prefix.capitalize()} from {name.capitalize()}"


class real:
    def __new__(cls, value):
        if not isinstance(value, str):
            return value

        self = super().__new__(cls)
        self.value = value
        return self

    def __str__(self):
        return self.value

def nameof(x):
    """
    class Foo:
        def __init__(self):
            print(nameof(self))

    class Boo(Foo):
        pass

    Boo() # the name will be Boo
    """
    if callable(x):
        return x.__name__

    if isinstance(x, str):
        return x
    else:
        return x.__class__.__name__

def yes(*args, **kwargs):
    return True


def stop(*args, **kwargs):
    if args:
        for arg in args:
            print(arg)
    display(**kwargs)
    raise Exception("__EXIT__")

def each(items, fn, *args, **kwargs):
    params = get_parameters(fn)
    if len(params) > 1 and params[1] == "index":
        return [
            fn(item, index, *args, **kwargs)
            for index, item in enumerate(items)
        ]
    else:
        return [fn(item, *args, **kwargs) for item in items]





def to_argument(x):
    """
    creates a real python argument
    foobar('true') -> foobar(True)

    the argument is coerced into a python form
    """
    reference = {
      'true': True,
      'false': False,
      'none': None,
      'null': None,
    }
    if isinstance(x, str):
        if re.search('^\d+\.\d+$', x):
            return float(x)
        if re.search('^\d+$', x):
            return int(x)
        return reference.get(x, x)
    return x

def coerce_type(val, expected):
    if expected == "str":
        return str(val)
    if expected == "int":
        return int(val)
    if expected == "float":
        return float(val)
    if expected == "bool":
        if val == 'false': return False
        if val == 'true': return True
    if expected == "list":
        if isinstance(val, str):
            return [x.strip() for x in val.split(',')]
        if isinstance(val, list):
            return val
        raise TypeError(f"Cannot coerce value to list: {val}")
    if expected == "dict":
        if isinstance(val, dict):
            return val
        raise TypeError(f"Expected dict for value: {val}")
    raise TypeError(f"Unknown expected type: {expected}")



class Singleton(type):
    """Metaclass for creating Singleton classes"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

def instantiate(x):
    return x() if type(x) == type else x


def get_field_value(obj, field_path, default=None):
    """
    Get a field value from a dict or non-dict object (including nested paths).
    
    Args:
        obj: The object (dict, class instance, etc.).
        field_path (str): Dot-separated path (e.g., "user.address.city").
        default: Value to return if the field doesn't exist.
    
    Returns:
        The field value or `default` if not found.
    """
    if not field_path:
        return default

    keys = field_path.split('.')
    current = obj

    for key in keys:
        if isinstance(current, dict):
            if key not in current:
                return default
            current = current[key]
        elif hasattr(current, '__dict__'):  # Class instance with __dict__
            if not hasattr(current, key):
                return default
            current = getattr(current, key)
        else:  # Other objects (e.g., namedtuple, @property)
            try:
                current = getattr(current, key)
            except AttributeError:
                return default
    return current



def testf(selector: Selector, flags=0, anti=0, key=None):
    if not selector:
        return None

    fn = selector

    if isinstance(selector, str):
        pat = re.compile(selector, flags = flags)
        fn = lambda s: pat.search(s)
    elif isinstance(selector, re.Pattern):
        fn = lambda s: selector.search(s, flags = flags)
        
    elif isinstance(selector, (list, tuple)):
        fn = lambda s: s in selector

    if anti and key:
        return lambda x: not fn(get_field_value(x, key))
    elif anti:
        return lambda x: not fn(x)
    elif key:
        return lambda x: fn(get_field_value(x, key))
    else:
        return fn
