"""
secondary file_operations
"""

import os
import re
from collections import Counter

from kevinlulee.extras.fancy_file_tree import fancy_file_tree
from kevinlulee.file_utils import (
    assert_file,
    is_file,
    has_valid_existing_parent,
)




def get_most_common_file_extension(dir, recursive=False):
    current_dir = os.path.expanduser(dir)
    extensions = []

    def add(file):
        _, extension = os.path.splitext(file)
        if extension:  # Only add if there's an extension
            extensions.append(extension.lower())

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


import subprocess, shutil, datetime


def get_directory_size(path: str, follow_symlinks: bool = False) -> int:
    path = os.path.expanduser(path)
    LFLAG = "-L" if follow_symlinks else "-H"
    has_du_b = (
        subprocess.run(
            ["du", "-b", "/dev/null"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )
    if has_du_b:
        out = subprocess.run(
            ["du", "-sb", LFLAG, path],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return int(out.split()[0])
    else:
        out = subprocess.run(
            ["du", "-sk", LFLAG, path],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return int(out.split()[0]) * 1024


def get_directory_last_touched(
    path: str, follow_symlinks: bool = False
) -> float:
    path = os.path.expanduser(path)
    LFLAG = "-L" if follow_symlinks else "-H"
    gfind = shutil.which("gfind")
    if gfind:
        # Single-process, very fast
        out = subprocess.run(
            [
                gfind,
                LFLAG,
                path,
                "-type",
                "f",
                "-printf",
                "%T@\\n",
                "-o",
                "-type",
                "d",
                "-printf",
                "%T@\\n",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        mx = int(float(max(out))) if out else 0
        return datetime.datetime.fromtimestamp(mx)

    # Portable path: find + stat (GNU or BSD)
    is_gnu_stat = (
        subprocess.run(
            ["stat", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )
    find_cmd = [
        "find",
        LFLAG,
        path,
        "(",
        "-type",
        "f",
        "-o",
        "-type",
        "d",
        ")",
        "-print0",
    ]
    if is_gnu_stat:
        p1 = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(
            ["xargs", "-0", "-n", "1024", "stat", "-c", "%Y"],
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
        )
    else:
        p1 = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(
            ["xargs", "-0", "-n", "1024", "stat", "-f", "%m"],
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
        )

    p1.stdout.close()  # allow p1 to receive SIGPIPE if p2 exits
    out_bytes = p2.communicate()[0]
    lines = out_bytes.decode().split()
    mx = max(map(int, lines)) if lines else 0
    return mx


# print(get_directory_last_touched('~/2023'))


def zip_view(src_path) -> str:
    src_path = os.path.expanduser(src_path)
    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(item.orig_filename)

        return fancy_file_tree(store)
