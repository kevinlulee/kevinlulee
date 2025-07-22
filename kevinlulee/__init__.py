import re
import os

from collections import defaultdict
from typing import *

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
from .func_ops import *
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

def pretty_print(el):
    if not el:
        return 
    pprint(el)
