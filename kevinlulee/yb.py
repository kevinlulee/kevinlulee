from kevinlulee.ao import partition
from kevinlulee.base import coerce_argument
from kevinlulee.file_utils import readfile
from kevinlulee.string_utils import split
import re


def load(s):
    items = split(s, '^-{3,}', flags = re.M)

    def fix(v):
        return coerce_argument(v)

    def runner(chunk):
        items = split(chunk, '^(\w+(?:-\w+)*):', flags = re.M)
        parts = partition(items)
        return {
            k: fix(v) for k, v in parts
        }
        
    return [runner(item) for item in items]


s = """
hi: 
asdf
asdf

bye:

asdfasdf


a: 1222
"""
# print(load(s))
