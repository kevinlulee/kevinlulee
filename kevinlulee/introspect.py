from kevinlulee.ao import find_index
import inspect
from inspect import Parameter
import inspect

from typing import (
    TypedDict,
    Literal,
    Any,
    List,
    Optional,
    Callable,
    Type,
    Union,
    get_type_hints,
)
from inspect import Parameter


class ParamInfoItem(TypedDict):
    default: Any # abc(foobar = 'default')
    name: str
    annotation: Optional[str | Any]
    kind: Literal[
        "POSITIONAL_ONLY",
        "POSITIONAL_OR_KEYWORD",
        "VAR_POSITIONAL",
        "KEYWORD_ONLY",
        "VAR_KEYWORD",
    ]
    required: bool


def get_param_info(func_or_class) -> List[ParamInfoItem]:
    sig = inspect.signature(func_or_class)
    param_info = []

    for name, param in sig.parameters.items():
        required = param.default is Parameter.empty
        default = None if param.default is Parameter.empty else param.default
        annotation = (
            None if param.annotation is Parameter.empty else param.annotation
        )

        p = {
            "default": default,
            "name": name,
            "annotation": annotation,
            "kind": str(param.kind),
            "required": required,
        }
        param_info.append(p)

    return param_info


def get_caller(offset=0, skippable=[], ignore_list=[]) -> inspect.FrameInfo:
    KNOWN_IMPLICIT_CALLERS = [
        "get_caller",
    ]
    backwards = ["must"]
    DEFAULT_SKIPPABLE = [
        "log",
        "log_error",
        "__init__",
        "handler",
        "decorator",
        "wrapper",
        'modal',
    ]

    items: list = inspect.stack()
    # for item in items:
        # print(item.function)
    # find_index
    start = find_index(
        items,
        lambda x: x.function in KNOWN_IMPLICIT_CALLERS,
    )
    if start == -1:
        return
    start += 1
    length = len(items)
    skip = skippable + DEFAULT_SKIPPABLE
    while start < length:
        next: inspect.FrameInfo = items[start]
        if next.function in backwards:
            return items[start - 1]
        if (next.filename, next.function) in ignore_list:
            start += 1
            continue

        if next.function in skip:
            start += 1
            continue
        if offset:
            next = items[start + offset]
        return next


def get_required_parameters(func) -> list:
    """
        these are the param arguments which do not have default values
    """
    p = inspect.getfullargspec(func)
    delta = len(p.args) - len(p.defaults or [])
    return p.args[0:delta]

def get_parameters_and_fallbacks(func):
    p = inspect.getfullargspec(func)
    args = p.args
    if not args:
        return []
    defaults = list(p.defaults) if p.defaults else []
    defaults = [None] * (len(args) - len(defaults)) + defaults
    return dict(zip(args, defaults))
def foobar(a, b, c = 1, d = 123):
    pass

class Foo:
    def __init__(self):
        pass

    def abc(self):
        kx.pprint(get_caller(2))

def create():
    Foo().abc()
    
class Bar:
    def __init__(self):
        self.run_gogogo()
    
    def run_gogogo(self):
        create()



def get_parameters(func, ignore_self = True):
    p = list(inspect.signature(func).parameters.keys())
    if ignore_self and len(p) and p[0] == 'self':
        p.pop(0)
    return p



def object_finder(func):
    if not func:
        return
    file = inspect.getfile(func)
    if not file:
        return
    line_numbers, lnum = inspect.getsourcelines(func)
    return file, lnum
if __name__ == '__main__':
    # print(gobo(foobar))
    # print(get_parameters_and_fallbacks(foobar))

    # testing get_caller
    # Bar()
    # object_finder
    print(object_finder(globals().get('CetzObject')))
    # it doesnt work.
