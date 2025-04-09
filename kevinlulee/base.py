import inspect


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



def sayhi(name="Bob", *names, prefix="howdy"):
    return f"{prefix} from {name}"


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






