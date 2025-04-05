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
        return next


def strcall(name, args, kwargs, max_length = 80):
    
        a = len(args)
        k = len(kwargs)

        s = name + "("
        if args:
            s += ", ".join(args)
        if kwargs:
            if args:
                s += ", "
            s += ", ".join(kwargs)

        s += ')'

        if len(s) < max_length and not "\n" in s:
            return s

        s = name + "("
        if args:
            s += "\n" + ", ".join(args)
        if kwargs:
            if args:
                s += ", "
            s += "\n" + "\n, ".join(kwargs)

        s += ')'
        return s
