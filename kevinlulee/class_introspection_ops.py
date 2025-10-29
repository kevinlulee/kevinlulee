import inspect
import re
from typing import Iterable


DEFAULT_IGNORED_METHODS = [
    'construct', '__init__', '__str__', 'setup', 'load'
]
def collect_class_property_names(cls):
    # collect property names across the MRO without hasattr/try/except
    props = set()
    for base in cls.__mro__:
        for name, val in base.__dict__.items():
            if isinstance(val, property):
                props.add(name)
    return props


def check_type_string(obj, *names):
    return any(cls.__name__ in names for cls in type(obj).__mro__)

def get_class_method_names(obj_or_cls,
                      pattern: str = r"^[a-z]",
                      ignore_methods: Iterable[str] | None = None,
                      ignore_parents: Iterable[str] | None = None,
                      ignore_inherited: bool = True,
                      ignore_static: bool = True,
                      ignore_classmethods: bool = True) -> list[str]:
    """
    Return method *names* on a class (or instance's class), filtered by regex.
    Safe: reads class __dict__ (no getattr on instance), so properties/descriptors won't run.

    - ignore_inherited=True  -> only methods defined directly on the class
    - ignore_static=True     -> exclude @staticmethod
    - ignore_classmethods=True -> exclude @classmethod
    """
    klass = obj_or_cls if inspect.isclass(obj_or_cls) else obj_or_cls.__class__
    rx = re.compile(pattern) if pattern else None
    ignore_methods = DEFAULT_IGNORED_METHODS + (ignore_methods or [])
    ignore_methods = set(ignore_methods or [])
    names, seen = [], set()

    classes = [klass] if ignore_inherited else list(klass.__mro__)

    for C in classes:
        for name, attr in C.__dict__.items():
            if rx and not rx.match(name):
                continue
            if name in ignore_methods:
                continue

            # Handle staticmethod / classmethod explicitly
            if isinstance(attr, staticmethod):
                if ignore_static:
                    continue
                func = attr.__func__
            elif isinstance(attr, classmethod):
                if ignore_classmethods:
                    continue
                func = attr.__func__
            else:
                func = attr

            # Keep only plain functions (i.e., instance methods before binding)
            if not inspect.isfunction(func):
                continue

            # Optional parent filtering when scanning MRO
            if not ignore_inherited and ignore_parents:
                qual_candidates = (func.__qualname__, f"{C.__name__}.{name}", C.__name__)
                if any(
                    any(qc == p or qc.startswith(p if p.endswith('.') else p + '.') for qc in qual_candidates)
                    for p in ignore_parents
                ):
                    continue

            if name not in seen:
                seen.add(name)
                names.append(name)

    return names
