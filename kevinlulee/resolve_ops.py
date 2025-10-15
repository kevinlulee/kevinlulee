import os
from kevinlulee.consts.file_types import FILETYPES, EXTENSIONS, EXT_TO_FILETYPE 

def resolve_filetype(x):
    if not x:
        return 

    if x in FILETYPES:
        return x 

    if x in EXTENSIONS:
        return EXT_TO_FILETYPE[x]

    ext = os.path.splitext(x)[1][1:].lower()
    return EXT_TO_FILETYPE[ext]
