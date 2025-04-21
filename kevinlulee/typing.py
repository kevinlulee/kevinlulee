from typing import Union, Callable, List, Any, Optional

Selector = Union[
    Callable[[Any], Any],  # Function that takes input and returns output
    str,                   # String selector
    Callable,              # Callback reference
    List[Any]              # Array/list
]
