import re
import os

from collections import defaultdict
from typing import *
from dataclasses import dataclass


from .base import *
from .date_utils import *
from .assertion import *
from .ao import *
from .string_utils import *
from .serialize_ops import normalize_data, serialize_data
from .file_utils import *
from .text_tools import *
from .validation import *
from .constants import *
from .array import *
from .templater import *
from .module_utils import *
from .bash import *
from .ripgrep import *
from .file_ops import *

# from .components.string_builders import *
from typing import *
from .git import GitRepo
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt
from .functions import *
import kevinlulee.yb as yb
import kevinlulee.ascii as ascii
import kevinlulee.introspect as introspect
import kevinlulee.lorem as lorem
import kevinlulee.rng as rng
import kevinlulee.env as env
from .extended import *
from .ddo import LiveDict, LiveArray
from .text import StringBuilder
from .extensions import *

get_caller = introspect.get_caller

pretty_print = prettyprint


def fparse(input, *args, **kwargs):
    if callable(input):
        return input(*args, **kwargs)
    else:
        return input


def newline_padding(s, padding):
    if not padding:
        return s

    a, b = padding if is_array(padding) else (padding, padding)
    return "\n" * (a) + s + "\n" * (b)


def path_in(paths, src_path):
    src_path = os.path.expanduser(src_path)
    for path in paths:
        path = os.path.expanduser(path)
        if path in src_path:
            return path


def announce(*args, **kwargs):
    print(*args, **kwargs)
def throw_on(x):
    def foo(el):
        if el == x:
            raise Exception(f"throw on {x}")
        return el
    return foo
