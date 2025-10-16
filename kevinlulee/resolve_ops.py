import os
from kevinlulee.consts.file_types import FILETYPES, EXTENSIONS, EXT_TO_FILETYPE , DOTFILE_TO_FILETYPE

def resolve_filetype(x):
    if not x:
        return

    if x in FILETYPES:
        return x

    if x in EXTENSIONS:
        return EXT_TO_FILETYPE[x]

    basename = os.path.basename(x)
    if basename in DOTFILE_TO_FILETYPE:
        return DOTFILE_TO_FILETYPE[basename]

    ext = os.path.splitext(x)[1][1:].lower()
    if ext and ext in EXT_TO_FILETYPE:
        return EXT_TO_FILETYPE[ext]


