
def exists(x):
    if isinstance(x, (list, tuple, dict)):
        return len(x) > 0
    if isinstance(x, str):
        return len(x.strip()) > 0
    if x == 0:
        return True

    return bool(x)

def empty(x):
    return not exists(x)

def is_string(value):
    return isinstance(value, str)

def is_number(value):
    return isinstance(value, (int, float, complex)) and not isinstance(value, bool)

def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)

def is_boolean(value):
    return isinstance(value, bool)

def is_array(value):
    return isinstance(value, list)

def is_dict(value):
    return isinstance(value, dict)

def is_none(value):
    return value is None

def is_function(value):
    return callable(value)

