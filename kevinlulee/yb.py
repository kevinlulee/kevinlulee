from kevinlulee.ao import partition
import os
from kevinlulee.base import coerce_argument
from kevinlulee.string_utils import split
import re


def load(s):
    items = split(s, "^-{3,}", flags=re.M)

    def fix(v):
        return coerce_argument(v)

    def runner(chunk):
        items = split(chunk, "^(\w+(?:-\w+)*):", flags=re.M)
        parts = partition(items)
        return {k: fix(v) for k, v in parts}

    return [runner(item) for item in items]


def parse(data):
    s = "\n---\n"
    for k, v in data.items():
        spaces = "\n\n" if '\n' in v else " "
        s += f"{k}:{spaces}{v}\n"

    return s


def append_file(path, data):
    path = os.path.expanduser(path)
    with open(path, "a") as f:
        f.write(parse(data))

    return path
