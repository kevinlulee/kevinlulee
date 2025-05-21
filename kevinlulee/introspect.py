import inspect
from inspect import Parameter

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
    annotation: Optional[Any]
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
    required_args = p.args[0:delta]
    return required_args

# print(get_required_args(get_param_info))
