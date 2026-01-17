from __future__ import annotations
import kevinlulee as kx


import re

SYMBOL_PATTERNS = {
    "python": [
        r"^(?:async\s+)?def\s+(\w+)",
        r"^class\s+(\w+)",
        # r"^(\w+)\s+=",
    ],
    "javascript": [
        r"^(?:async\s+)?function\s+(\w+)",
        r"^(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\(|=>)",
        r"^class\s+(\w+)",
    ],
    "typescript": [
        r"^(?:async\s+)?function\s+(\w+)",
        r"^(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\(|=>)",
        r"^class\s+(\w+)",
        r"^interface\s+(\w+)",
        r"^type\s+(\w+)",
    ],
    "typst": [
        r"^#let\s+([\w-]+)",
    ],
}


def extract_symbols(content: str, language: str) -> set[str]:
    symbols = set()
    patterns = SYMBOL_PATTERNS[language]
    
    for line in content.split("\n"):
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                symbols.add(match.group(1))
    
    return symbols



