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


def unzip(file, dest):
    import zipfile

    file = os.path.expanduser(file)
    ensure_directory_exists(dest)
    dest = os.path.expanduser(dest)

    with zipfile.ZipFile(file, "r") as zf:
        zf.extractall(dest)
