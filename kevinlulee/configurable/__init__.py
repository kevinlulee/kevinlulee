import os
from kevinlulee.ao import dotaccess, smallify
from kevinlulee.validation import is_array, is_string
from kevinlulee.file_utils import readfile
DATA = readfile('~/.env.yml')

def myenv(*args):
    def pathfix(s):
        if is_string(s) and s.startswith('~'):
            return os.path.expanduser(s)
        
    return smallify([pathfix(dotaccess(DATA, key)) for key in args])
