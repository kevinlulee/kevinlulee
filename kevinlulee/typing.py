from typing import Union, Callable, List, Any, Optional
import re

Selector = Union[
    Callable[[Any], Any],  # Function that takes input and returns output
    str,                   # String selector
    Callable,              # Callback reference
    List[Any]              # Array/list
]
from typing import Union, Sequence, Any, Callable, Optional, Iterable
Selector = Optional[Union[str, re.Pattern, Sequence[Any], Callable[[Any], bool], List]]
