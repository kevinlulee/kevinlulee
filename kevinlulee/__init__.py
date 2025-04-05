from .file_utils import (
    readfile,
    writefile,
    FileContext,
    get_most_recent_file,
    clip,
    find_git_directory,
    fnamemodify, get_extension,
)

from .string_utils import (
    group,
    matchstr,
    mget,
    get_indent,
    camel_case,
    pascal_case,
    dash_case,
    trimdent,
    split,
)

from .text_tools import (
    templater,
    toggle_comment,
    join_text,
    dash_split,
    extract_frontmatter,
    bracket_wrap,
    tabs_to_spaces,
)

from .bash import ripgrep, bash, fdfind, typst, python3
from .git import GitRepo
# from .configurable import myenv
from .base import *
from .validation import *
from .ao import dotaccess, mapfilter, find_index, modular_increment
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt


def representative(self, *args, **kwargs):
    if not kwargs:
        kwargs = self.__dict__
    return pythonfmt.call(nameof(self), *args, **kwargs)


import yaml

def yamload(x):
    if not x:
        return {}

    if callable(x):
        while hasattr(x, '__wrapped__'):
            x = x.__wrapped__
        x = getattr(x, '__doc__')

    if not x:
        return {}

    s = trimdent(x)
    m = yaml.safe_load(s)

    if type(m) == str:
        return {}

    return m


