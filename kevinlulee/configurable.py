from .ao import dotaccess, smallify
from .file_utils import readfile

data = readfile('~/.env.yml')


def myenv(*keys):
    return smallify([dotaccess(data, key) for key in keys])
