"""
secondary file_operations
"""

import os
from collections import Counter


def get_most_common_file_extension(dir, recursive=False):
    current_dir = os.path.expanduser(dir)
    extensions = []

    def add(file):
        _, extension = os.path.splitext(file)
        if extension:  # Only add if there's an extension
            extensions.append(
                extension.lower()
            )

    if recursive:
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                add(file)
    else:
        for file in os.listdir(current_dir):
            add(file)

    if not extensions:
        return None

    extension_counts = Counter(extensions)
    most_common = extension_counts.most_common(1)
    return most_common[0][0][1:] if most_common else None


def zipread(src_path, dst_path = None) -> list[str]:
    '''
    items will be extracted into the same directory as the src
    a list of paths (the extracted files) will be returned
    '''
    src_path = os.path.expanduser(src_path)
    dst_path = os.path.expanduser(dst_path) if dst_path else os.path.dirname(src_path)

    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(os.path.join(dst_path, item.filename))

        zf.extractall(dst_path)

        return store
