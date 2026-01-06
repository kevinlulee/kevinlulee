from __future__ import annotations
import kevinlulee as kx

from dataclasses import dataclass
import re
from typing import List


@dataclass
class Section:
    path: str
    text: str


COMMENT_PREFIXES = (
    r"--",   # Lua
    r"#",    # Python
    r"//",   # C-like
    r";",    # ini / lisp
)

BAR_RE = re.compile(r"[=\-]{10,}")
PATH_RE = re.compile(r"[A-Za-z0-9_\-./]+?\.(lua|py|js|ts|vim|sh|c|cpp|rs|go)")


def split_into_sections(source: str) -> List[Section]:
    lines = source.splitlines()
    sections: List[Section] = []

    current_path = None
    buffer = []
    auto_index = 1

    def flush():
        nonlocal auto_index
        if buffer:
            path = current_path or f"<section-{auto_index}>"
            sections.append(Section(path=path, text="\n".join(buffer).strip()))
            auto_index += 1

    for line in lines:
        stripped = line.strip()

        is_comment = any(stripped.startswith(p) for p in COMMENT_PREFIXES)
        has_bar = bool(BAR_RE.search(stripped))
        path_match = PATH_RE.search(stripped)

        is_header = is_comment and (has_bar or path_match)

        if is_header:
            flush()
            buffer = []

            if path_match:
                current_path = path_match.group(0)
            else:
                current_path = None
            continue

        buffer.append(line)

    flush()
    return sections



lua_text = """
-- ============================================================
-- lua/nvim-frontend/init.lua
-- ============================================================
local config = require 'nvim-frontend.config'
local server = require 'nvim-frontend.server'

-- ------------------------------------------------------------
-- lua/nvim-frontend/server.lua
-- ------------------------------------------------------------
local M = {}
return M
"""

if __name__ == '__main__':
    sections = split_into_sections(lua_text)
    
    for s in sections:
        print(s.path)
        print(s.text)
        print("-----")
