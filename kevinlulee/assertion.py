def assert_array(x):
    """
    Assert that x is array-like (list, tuple, or any sequence that's not a string or dict).
    """
    if not hasattr(x, '__iter__') or isinstance(x, (str, dict, bytes, bytearray)):
        raise TypeError(f"Expected array-like object, got {type(x).__name__}")
    return x

def assert_dict(x):
    """
    Assert that x is a dictionary.
    """
    if not isinstance(x, dict):
        raise TypeError(f"Expected dictionary, got {type(x).__name__}")
    return x

def assert_string(x):
    """
    Assert that x is a string.
    """
    if not isinstance(x, str):
        raise TypeError(f"Expected string, got {type(x).__name__}")
    return x

def assert_int(x):
    """
    Assert that x is an integer.
    """
    if not isinstance(x, int) or isinstance(x, bool):
        raise TypeError(f"Expected integer, got {type(x).__name__}")
    return x

def assert_float(x):
    """
    Assert that x is a float.
    """
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        raise TypeError(f"Expected float, got {type(x).__name__}")
    return float(x)

def assert_bool(x):
    """
    Assert that x is a boolean.
    """
    if not isinstance(x, bool):
        raise TypeError(f"Expected boolean, got {type(x).__name__}")
    return x

def assert_callable(x):
    """
    Assert that x is callable.
    """
    if not callable(x):
        raise TypeError(f"Expected callable, got {type(x).__name__}")
    return x

def assert_type(x, expected_type):
    """
    Assert that x is of the expected type.
    """
    if not isinstance(x, expected_type):
        raise TypeError(f"Expected {expected_type.__name__}, got {type(x).__name__}")
    return x

def assert_none(x):
    """
    Assert that x is None.
    """
    if x is not None:
        raise TypeError(f"Expected None, got {type(x).__name__}")
    return x

def assert_not_none(x):
    """
    Assert that x is not None.
    """
    if x is None:
        raise TypeError("Expected not None")
    return x
