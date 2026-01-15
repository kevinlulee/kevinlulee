from __future__ import annotations
import kevinlulee as kx

def parse_directory_tree(tree_text: str) -> list[str]:
    """Parse directory tree string into file paths."""
    files = []
    path_stack = []

    for line in tree_text.split("\n"):
        if not line.strip():
            continue

        cleaned = re.sub(r"[│├└─\s]", "", line)
        if not cleaned:
            continue

        indent = 0
        for char in line:
            if char in "│ ":
                indent += 1
            else:
                break
        level = indent // 4

        is_dir = cleaned.endswith("/")
        name = cleaned.rstrip("/")

        path_stack = path_stack[:level]
        path_stack.append(name)

        if not is_dir:
            files.append("/".join(path_stack))

    return files
