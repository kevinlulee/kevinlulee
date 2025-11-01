import os
import nvim
import kevinlulee as kx
import re
from collections import Counter
from typing import Dict, List

def count_regex_in_dir(
    pattern: str,
    directory: str,
    *,
    respect_gitignore: bool = False,
    follow_symlinks: bool = False,
    hidden: bool = False,
    case_insensitive: bool = True,
    multiline: bool = False,
    ignore_file: str = "~/.ignore",
    respect_ignore_file: bool = True,
    exclude_dirs: List[str] = [],
    include_dirs: List[str] = [],
    exts: List[str] = [],
    boundary: bool = False,
) -> Dict[str, int]:
    """
    Uses the provided ripgrep() to search for lines, then counts per-match occurrences
    of `pattern` within those lines. Returns a dict {match: count}.
    """
    # run ripgrep to get matching lines across files
    lines = kx.ripgrep(
        pattern=pattern,
        dirs=[directory],
        respect_gitignore=respect_gitignore,
        follow_symlinks=follow_symlinks,
        hidden=hidden,
        case_insensitive=case_insensitive,
        multiline=multiline,
        ignore_file=ignore_file,
        respect_ignore_file=respect_ignore_file,
        show_lnum=True,                 # ensures format: file:line:content
        exclude_dirs=exclude_dirs,
        include_dirs=include_dirs,
        exts=exts,
        grouped=False,
        boundary=boundary,
    )

    # ripgrep() in your codebase returns a list; it may be strings or custom objects.
    # Accept both: coerce each item to text.
    def to_text(line):
        # If it's a structured RipgrepLine, try common attrs; otherwise str() fallback.
        for attr in ("text", "line", "content"):
            if hasattr(line, attr):
                return getattr(line, attr)
        return str(line)

    text_lines = [to_text(l) for l in lines]

    # compile the regex with flags consistent with how ripgrep was invoked
    flags = 0
    if case_insensitive:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    rx = re.compile(pattern, flags)

    counts = Counter()

    for raw in text_lines:
        # Expect "path:lineno:content". Keep the content part if present.
        # If format differs, fall back to whole line.
        parts = raw.split(":", 2)
        content = parts[2] if len(parts) == 3 else raw
        for m in rx.findall(content):
            # re.findall returns the full match OR a tuple if there are capturing groups.
            if isinstance(m, tuple):
                m = m[0] if m else ""
            if m:
                counts[m] += 1

    return dict(counts)

# --- Example call ---
# Count occurrences of `kx(?:\.\w+)+` under ~/projects/python/maelstrom using ~/.ignore by default
if __name__ == '__main__':
    example_result = count_regex_in_dir(r"kx(?:\.\w+)+", os.path.expanduser("~/projects/python/maelstrom"))
    nvim.fs.clip(example_result)
