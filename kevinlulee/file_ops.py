"""
secondary file_operations
"""

import subprocess, shutil, datetime
import subprocess
import os
import re
from collections import Counter

from kevinlulee.extras.fancy_file_tree import fancy_file_tree
from kevinlulee.file_utils import (
    assert_file,
    is_file,
    has_valid_existing_parent,
)

def zipread(src_path, dst_path=None) -> list[str]:
    """
    items will be extracted into the same directory as the src if dst_path
    is not provided

    a list of paths (the extracted files) will be returned
    """
    src_path = os.path.expanduser(src_path)
    dst_path = (
        os.path.expanduser(dst_path) if dst_path else os.path.dirname(src_path)
    )

    assert has_valid_existing_parent(
        dst_path
    ), f"{dst_path} no ancestor in dst_path exists"
    assert_file(src_path)

    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(os.path.join(dst_path, item.filename))

        zf.extractall(dst_path)

        return store


def get_directory_size(path):
    result = subprocess.run(
        ['du', '-sb', path],  # -s for summary, -b for bytes
        capture_output=True,
        text=True
    )
    size = int(result.stdout.split()[0])
    return size

def zip_view(src_path) -> str:
    src_path = os.path.expanduser(src_path)
    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(item.orig_filename)

        return fancy_file_tree(store)


def get_most_common_file_extension(dir, recursive=False):
    current_dir = os.path.expanduser(dir)
    extensions = []
    
    def add(entry):
        _, extension = os.path.splitext(entry.name)
        if extension:  # Only add if there's an extension
            extensions.append(extension.lower())
    
    if recursive:
        for root, dirs, files in os.walk(current_dir):
            with os.scandir(root) as entries:
                for entry in entries:
                    if entry.is_file():
                        add(entry)
    else:
        with os.scandir(current_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    add(entry)
    
    if not extensions:
        return None
    
    extension_counts = Counter(extensions)
    most_common = extension_counts.most_common(1)
    return most_common[0][0][1:] if most_common else None


# kx.pretty_print(get_most_common_file_extension('~/projects/python/kevinlulee', recursive=True))
