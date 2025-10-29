import inspect
from pprint import pprint
from kevinlulee.typing import Selector
from typing import Callable
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


class Real:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class real:
    def __new__(cls, value):
        if not isinstance(value, str):
            return value

        self = super().__new__(cls)
        self.value = value
        return self

    def __str__(self):
        return self.value

def real(x):
    if isinstance(x, (list, tuple, set)):
        return [Real(el) for el in x]
    if isinstance(x, dict):
        return {
            k: Real(v) for k,v in x.items()
        }
    return Real(x)

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

def no(*args, **kwargs):
    return False

def each(items, fn, *args, **kwargs):
    params = get_parameters(fn)
    if len(params) > 1:
        if params[1] in ('i', "index"):
            return [
                fn(item, index, *args, **kwargs)
                for index, item in enumerate(items)
            ]
        elif isinstance(items[0], (list, tuple)):
            return [fn(*item, *args, **kwargs) for item in items]
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


def coerce_argument(x):
        if not isinstance(x, str):
            return x
        if x == 'false' or x == 'False': return False
        if x == 'true' or x == 'True': return True
        if x.startswith("\"") or x.startswith("'"):
            return x[1:1]
        if re.search('^\d+\.?\d*$', x):
            if '.' in x:
                return float(x)
            else:
                return int(x)

        return x

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
        fn = lambda s: selector.search(s)
        
    elif isinstance(selector, (list, tuple, set)):
        fn = lambda s: s in selector
    elif callable(selector):
        fn = selector
    else:
        fn = lambda x: x == fn

    if anti and key:
        return lambda x: not fn(get_field_value(x, key))
    elif anti:
        return lambda x: not fn(x)
    elif key:
        return lambda x: fn(get_field_value(x, key))
    else:
        return fn


def testf2(selectors):
    testers = [testf(a) for a in selectors]
    return lambda x: all(test(x) for test in testers)

def n2char(num: int) -> str:
    """Convert a number (0-25) to a corresponding lowercase letter (a-z)."""
    if 0 <= num <= 25:
        return chr(97 + num)
    else:
        raise ValueError("Number must be between 0 and 25.")


def char2n(letter: str) -> int:
    """Convert a lowercase letter (a-z) to a corresponding number (0-25)."""
    if len(letter) == 1 and letter.islower():
        return ord(letter) - 97
    else:
        raise ValueError("Input must be a single lowercase letter.")




def noop(*args, **kwargs):
    return 


def identity(x):
    return x


def bar(n=50, dash_delimiter = '-'):
    return dash_delimiter * n

def prettyprint(*args, **kwargs):
    for arg in args:
        if not arg:
            continue
        if isinstance(arg, (float, int, complex, str, bool)):
            print(arg)
        else:
            pprint(arg)



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
        raise RuntimeError(
            f"Loop exceeded {max_iterations} iterations - possible infinite loop detected"
        )

def curry_start(func, *top_args, **top_kwargs):
    def curried(*args, **kwargs):
        return func(*top_args, *args, **top_kwargs, **kwargs)

    return curried

def curry(func, *top_args, **top_kwargs):
    def curried(*args, **kwargs):
        return func(*args, *top_args, **kwargs, **top_kwargs)

    return curried



def bug(value):
    print("bugging")
    print("---")
    print("type", type(value))
    print("value", value)
    print("---")
    stop()


def panic(*args, **kwargs):
    for arg in args:
        print(arg)
    display(kwargs)
    stop()

def bring_to_life(code, scope=None) -> Callable:
    """
    Evaluates Python function code and returns the callable.
    
    Args:
        code (str): Python function code as a string
        scope (dict, optional): Dictionary to use as the global scope for exec.
                               If None, uses an empty dictionary.
                               
    Returns:
        callable: The function defined in the code
    """
    scope = scope or globals()
    # Create a local namespace for execution
    local_namespace = {}
    # Execute the code in the provided scope
    exec(code, scope, local_namespace)
    
    # Find the function name by parsing the code
    lines = code.strip().split('\n')
    first_line = lines[0].strip()
    
    # Extract function name from the def statement
    import re
    match = re.match(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', first_line)
    
    if not match:
        raise ValueError("Could not find function definition in the provided code")
    
    function_name = match.group(1)
    
    # Return the function from the local namespace
    if function_name not in local_namespace:
        raise ValueError(f"Function '{function_name}' was not defined in the provided code")
    
    return local_namespace[function_name]

def keycache(key_func):
    cache = {}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if key in cache:
                return cache[key]
            result = fn(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    return decorator

class Watcher:
    def __init__(self, key_func = repr):
        self.seen = set()
        self.store = []
        self.count = 0
        self.key_func = key_func
        
    def __contains__(self, item):
        reference = self.key_func(item)
        if reference in self.seen:
            return True
        else:
            self.seen.add(reference)
            return False

def must(input, key):
    if not input:
        return

    if key in input:
        return input[key]

    raise Exception(f"{key} was not in found in {input.keys()}")


