import re
from _collections_abc import dict_values, dict_keys, dict_items

def not_none(x):
    return x is not None

def test(s, r, flags=0):
    return bool(re.search(r, str(s), flags))


NUMBER_STRING_PATTERN = re.compile('^\d+(?:\.\d+)?$')

def exists(x):
    if isinstance(x, str):
        return len(x.strip()) > 0
    if hasattr(x, '__iter__'):
        return len(x) > 0
    if x == 0:
        return True

    return bool(x)

def empty(x):
    return not exists(x)

def is_string(value):
    return isinstance(value, str)

def is_number(value):
    return isinstance(value, (int, float, complex)) and not isinstance(value, bool)

def is_string_number(s):
    return re.search(NUMBER_STRING_PATTERN, s)
def looks_like_number(value):
    return is_number(value) or is_string_number(value)
def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)

def is_boolean(value):
    return isinstance(value, bool)

def is_nested_array(value):
    return isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], (list, tuple))

def is_array(value):
    return isinstance(value, (list, tuple, dict_keys, dict_values, dict_items))

def is_dict(value):
    return isinstance(value, dict)

def is_none(value):
    return value is None

def is_function(value):
    return callable(value)



def is_primitive(el):
    return el is None or isinstance(el, (str, int, float, bool))


def is_integer_float(value):
    return (
        isinstance(value, int)
        or isinstance(value, float)
        and value.is_integer()
    )



def is_word(s):
    return re.search("^[a-zA-Z]+$", s)


def looks_like_number(s):
    return bool(re.search(r"^\d+(?:\.\d+)?$", str(s)))

def exists_in_list(obj, lst):
    return any(x is obj for x in lst)

def comparable(a, b):
    if a == None:
        return True

    if a and not b:
        return False

    if not a and b:
        return False

    return True


def is_class_constructor(x):
    BASE_TYPES =(list, dict, tuple, set, str, int, float, bool)
    if x in BASE_TYPES:
        return False
    return isinstance(x, type)

def is_class_constructor(obj):
    """
    Check if an object is a user-defined class constructor (excluding built-in types).
    
    Args:
        obj: Any Python object
        
    Returns:
        bool: True if obj is a user-defined class, False otherwise
    """
    # Check if it has class attributes and is not a built-in type
    return (hasattr(obj, '__name__') and 
            hasattr(obj, '__bases__') and 
            hasattr(obj, '__dict__') and
            hasattr(obj, '__module__') and
            obj.__module__ != 'builtins' and
            callable(obj))

def is_class_instance(obj):
    """
    Check if an object is an instance of a user-defined class (excluding built-in types).
    
    Args:
        obj: Any Python object
        
    Returns:
        bool: True if obj is an instance of a user-defined class, False otherwise
    """
    # Check if it's an instance of a user-defined class
    return (hasattr(obj, '__class__') and 
            hasattr(obj.__class__, '__module__') and
            obj.__class__.__module__ != 'builtins' and
            not is_class_constructor(obj) and
            type(obj).__name__ != 'function' and
            type(obj).__name__ != 'method' and
            type(obj).__name__ != 'builtin_function_or_method')

def is_hex_color(s):
    return test(s, '^#\w{3}(?:\w{3})?$')

def deep_equal(a, b):
    # Check if objects are of the same type
    # if dump(a) == dump(b):
        # return True

    if isinstance(a, tuple):
        a = list(a)
    if isinstance(b, tuple):
        b = list(b)

    ta = type(a)
    tb = type(b)
    if ta != tb:
        return False
    
    # Handle None
    if a is None and b is None:
        return True
    
    # Handle basic types (int, float, string, bool)
        
    def normalized_newlines(s):
        return re.sub("^[ \t]+(?=\n)", "", s, flags = re.M).rstrip()

    if is_string(a):
        return normalized_newlines(a) == normalized_newlines(b)

    if is_primitive(a):
        return a == b
    
    # Handle lists
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(deep_equal(a[i], b[i]) for i in range(len(a)))
    
    # Handle dictionaries
    if isinstance(a, dict):
        if len(a) != len(b):
            return False
        if set(a.keys()) != set(b.keys()):
            return False
        return all(deep_equal(a[key], b[key]) for key in a)
    
    # Handle sets
    if isinstance(a, set):
        if len(a) != len(b):
            return False
        return all(any(deep_equal(item_a, item_b) for item_b in b) for item_a in a)
    
    # For other types, use the default equality
    try:
        return a == b
    except Exception as e:
        return False

def total_overlap(a, b):
    return deep_equal(sorted(a), sorted(b))


