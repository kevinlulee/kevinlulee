import re
from dataclasses import dataclass
from typing import List

# Fenced code blocks (``` or ~~~), allowing up to 3 spaces of indent per CommonMark.
FENCED_RE = re.compile(
    r"""
    ^(?P<indent>[ \t]{0,3})            # optional indent (0-3 spaces)
    (?P<fence>`{3,}|~{3,})[ \t]*       # opening fence of same char, len>=3
    (?P<info>[^\n]*)\n                 # info string (language + extras)
    (?P<body>.*?)
    ^(?P=indent)(?P=fence)[ \t]*$      # matching closing fence at same indent
    """,
    re.DOTALL | re.MULTILINE | re.VERBOSE,
)

@dataclass(frozen=True)
class ContentBlock:
    lang: str   # e.g., "python", "yaml", "text"
    content: str  # trimmed content of this block

import yaml
import json
from typing import List, Any

def parse_markdown_blocks(
    md: str,
    *,
    unknown_lang: str = "text",
    include_empty_text_blocks: bool = False,
) -> List[ContentBlock]:
    """
    Parse Markdown into an ordered list of trimmed ContentBlock(lang, content).

    Rules:
      - Detects fenced code blocks (``` or ~~~)
      - Language = first token of the info string (case-insensitive).
      - Missing/empty language -> `unknown_lang` (default: "text").
      - Non-code regions between fences become blocks with lang="text".
      - All block contents are fully trimmed with .strip().
      - Empty text blocks are dropped unless include_empty_text_blocks=True.
      - If lang is yml/yaml, content is parsed with yaml.safe_load().
      - If lang is json, content is parsed with json.loads().
    """
    blocks: List[ContentBlock] = []
    pos = 0

    for m in FENCED_RE.finditer(md):
        start, end = m.span()

        # Preceding prose -> lang="text"
        if start > pos:
            prose = md[pos:start].strip()
            if prose or include_empty_text_blocks:
                blocks.append(ContentBlock(lang="text", content=prose))
        pos = end

        # Language from info line
        lang = m.group('info') or 'raw'
        if lang == 'yml': lang = 'yaml'

        # Code body trimmed
        body = (m.group("body") or "").strip()
        if not body:
            continue
        
        # Parse content based on language
        content: Any = body
        if lang  =='yaml':
            content = yaml.safe_load(body)
        elif lang == "json":
            content = json.loads(body)
        
        blocks.append(ContentBlock(lang=lang, content=content))

    # Trailing prose
    if pos < len(md):
        tail = md[pos:].strip()
        if tail or include_empty_text_blocks:
            blocks.append(ContentBlock(lang="text", content=tail))

    return blocks


sample = """# Title

Some intro text.

```python
def add(a, b):
    return a + b
```

text

```yaml
name: app
version: "1.0"
```

More prose here.

```
no language here
```

"""

if __name__ == '__main__':
    blocks = parse_markdown_blocks(sample)
    for block in blocks:
        print(block.content, block.lang)
        print('__')
