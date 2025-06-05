import re

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

def is_array(value):
    return isinstance(value, (list, tuple))

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

# 2025-05-28 test: true
if __name__ == "__main__":
    # Define a sample class
    class MyClass:
        def __init__(self, value):
            self.value = value
    
    # Create an instance
    my_instance = MyClass(42)
    
    # Test cases
    print("Testing is_class_constructor:")
    print(f"MyClass: {is_class_constructor(MyClass)}")  # True
    print(f"my_instance: {is_class_constructor(my_instance)}")  # False
    print(f"int: {is_class_constructor(int)}")  # True
    print(f"42: {is_class_constructor(42)}")  # False
    print(f"'hello': {is_class_constructor('hello')}")  # False
    
    print("\nTesting is_class_instance:")
    print(f"MyClass: {is_class_instance(MyClass)}")  # False
    print(f"my_instance: {is_class_instance(my_instance)}")  # True
    print(f"42: {is_class_instance(42)}")  # False (built-in type)
    print(f"'hello': {is_class_instance('hello')}")  # False (built-in type)
    print(f"[1,2,3]: {is_class_instance([1,2,3])}")  # False (built-in type)
    
    
    # Test with functions to make sure they're excluded
    def my_function():
        pass
    
    print(f"\nAdditional tests:")
    print(f"function: {is_class_constructor(my_function)}")  # False
    print(f"function: {is_class_instance(my_function)}")  # False
