import os
from typing import Iterable, List, Tuple, Union

from kevinlulee.file_utils import create_gitignore_matcher



# ---------- Tree node ----------
class FileTreeNode:
    def __init__(self, name: str, is_file: bool = False):
        self.name = name
        self.is_file = is_file
        self.children = {}  # name -> FileTreeNode

    def add_child(self, name: str, is_file: bool = False):
        if name not in self.children:
            self.children[name] = FileTreeNode(name, is_file)
        return self.children[name]


# ---------- Utilities ----------
def _to_posix(path: str) -> str:
    return path.replace("\\", "/")

def _split_parts(path: str) -> List[str]:
    # Normalize, then remove leading slashes so abs/rel can be compared uniformly
    norm = _to_posix(path).lstrip("/").strip()
    if not norm:
        return []
    return [p for p in norm.split("/") if p]

def get_common_root_from_filepaths(paths: Iterable[str]) -> str:
    """
    Return a '/'-joined common directory prefix across the given paths.
    Works for absolute or relative inputs. Returns '' if none.
    """
    paths = list(paths)
    if not paths:
        return ""

    parts_lists = [_split_parts(p) for p in paths if p is not None]
    if not parts_lists:
        return ""

    common = parts_lists[0][:]
    for parts in parts_lists[1:]:
        i = 0
        lim = min(len(common), len(parts))
        while i < lim and common[i] == parts[i]:
            i += 1
        common = common[:i]
        if not common:
            break

    return "/".join(common)


# ---------- Build from list ----------
def build_file_tree(file_paths: Iterable[str]) -> Tuple[FileTreeNode, str]:
    """
    Build an in-memory tree from a list of file paths.
    Returns (root_node, common_root_string).
    """
    file_paths = list(file_paths)
    root = FileTreeNode("root")

    common_root = get_common_root_from_filepaths(file_paths)

    for raw in file_paths:
        # Remove the common dir prefix (if any) so the printed tree starts at divergence.
        p = _to_posix(raw)
        if common_root:
            # Ensure we only strip when it matches a directory boundary.
            # Example: common_root='frontend/src', path='frontend/src/App.tsx'
            # We remove the prefix + '/' if present.
            if p.startswith(common_root + "/"):
                p = p[len(common_root) + 1 :]
            elif p == common_root:
                # Edge case if a directory path slipped in; skip it
                continue
        # Make relative and split
        parts = _split_parts(p)
        if not parts:
            continue

        cur = root
        for i, part in enumerate(parts):
            is_file = i == len(parts) - 1
            cur = cur.add_child(part, is_file=is_file)

    return root, common_root


# ---------- Renderers ----------
def _sorted_children_items(node: FileTreeNode):
    # Sort: directories first, then files, each alphabetically
    return sorted(
        node.children.items(),
        key=lambda kv: (kv[1].is_file, kv[0])
    )

def print_tree(node: FileTreeNode, prefix: str = "", is_last: bool = True) -> List[str]:
    """
    Return a list of lines representing the tree starting at `node`.
    The synthetic 'root' node itself is not printed. Its children are.
    """
    lines: List[str] = []

    if node.name != "root":
        connector = "└── " if is_last else "├── "
        display = node.name + ("/" if (not node.is_file and node.children) else "")
        lines.append(f"{prefix}{connector}{display}")
        new_prefix = prefix + ("    " if is_last else "│   ")
    else:
        new_prefix = prefix

    items = _sorted_children_items(node)
    for i, (_, child) in enumerate(items):
        child_is_last = i == (len(items) - 1)
        lines.extend(print_tree(child, new_prefix, child_is_last))

    return lines

def get_tree_string(root: FileTreeNode) -> str:
    lines = print_tree(root)
    return "\n".join(lines)


# ---------- Public API ----------
def _fancy_filetree_from_list(custom_files: Iterable[str]) -> str:
    """
    Pretty tree for a provided list of file paths (abs or rel).
    If a common directory root exists, it is shown as a header.
    """
    tree, common = build_file_tree(custom_files)
    body = get_tree_string(tree)

    if not body:
        return (common + "/") if common else ""

    # If there's a common header, prepend it on its own line.
    if common:
        return common + "/\n" + body

    # No common header; by default `print_tree` starts with a connector.
    # That's fine, but if you prefer no leading connector on the very first line,
    # uncomment the next two lines:
    # if body.startswith(("├── ", "└── ")):
    #     body = body[4:]
    return body


def fancy_file_tree(root_dir_or_list: Union[str, Iterable[str]], truncate: bool = False, max_leaves = 20) -> str:
    """
    If given a directory path (string), walk the filesystem and produce a tree,
    honoring .gitignore via create_gitignore_matcher. If given a list/tuple of
    paths, render them using fancy_filetree_from_list.
    """
    # Support list/tuple inputs transparently
    if isinstance(root_dir_or_list, (list, tuple)):
        return _fancy_filetree_from_list(root_dir_or_list)

    root_dir = os.path.expanduser(root_dir_or_list)
    if not os.path.isdir(root_dir):
        return ""

    ignore = create_gitignore_matcher(root_dir)
    header = os.path.basename(os.path.normpath(root_dir)) + "/"

    leaf_count = 0
    def build_fs_tree(directory: str, node: FileTreeNode):
        nonlocal leaf_count
        entries = sorted(os.listdir(directory))
        count = 0
        for name in entries:
            if truncate and leaf_count > max_leaves:
                continue
            full = os.path.join(directory, name)
            if ignore(full):
                continue
            if os.path.isdir(full):
                child = node.add_child(name, is_file=False)
                build_fs_tree(full, child)
            else:
                if truncate and count > 3:
                    continue
                else:
                    node.add_child(name, is_file=True)
                    count += 1

            leaf_count += 1

    # Build an in-memory tree from disk
    root = FileTreeNode("root")
    build_fs_tree(root_dir, root)

    body = get_tree_string(root)
    if not body:
        return header

    return header + "\n" + body


if __name__ == '__main__':
    print(fancy_file_tree('~/projects/python/maelstrom'))
