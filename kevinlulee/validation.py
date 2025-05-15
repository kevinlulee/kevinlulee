import re

NUMBER_STRING_PATTERN = re.compile('^\d+(?:\.\d+)?$')

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


def is_class_constructor(obj):
    if isinstance(obj, type):
        return True

