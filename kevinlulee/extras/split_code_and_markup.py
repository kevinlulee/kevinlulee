from dataclasses import dataclass
from typing import Literal


@dataclass
class CodeBlock:
    kind: Literal["code"] = "code"
    language: str | None = None
    content: str = ""


@dataclass
class MarkupBlock:
    kind: Literal["markup"] = "markup"
    content: str = ""


ContentBlock = CodeBlock | MarkupBlock


def parse_blocks(text: str) -> list[ContentBlock]:
    blocks = []
    lines = text.split('\n')
    
    state = "markup"
    current_lines = []
    current_lang = None
    
    for line in lines:
        if state == "markup":
            if line.startswith('```'):
                if current_lines:
                    content = '\n'.join(current_lines).strip()
                    if content:
                        blocks.append(MarkupBlock(content=content))
                    current_lines = []
                
                rest = line[3:]
                if rest.endswith('```'):
                    # Inline fence: ``` stuff ```
                    blocks.append(CodeBlock(
                        language=None,
                        content=rest[:-3].strip()
                    ))
                else:
                    # Start of multiline fence
                    state = "code"
                    current_lang = rest.strip() if rest.strip() else None
            else:
                current_lines.append(line)
        
        elif state == "code":
            if line == '```':
                blocks.append(CodeBlock(
                    language=current_lang,
                    content='\n'.join(current_lines)
                ))
                current_lines = []
                current_lang = None
                state = "markup"
            else:
                current_lines.append(line)
    
    # Handle remaining content
    if current_lines:
        content = '\n'.join(current_lines).strip()
        if content:
            if state == "markup":
                blocks.append(MarkupBlock(content=content))
            else:
                # Unclosed fence, treat as code anyway
                blocks.append(CodeBlock(language=current_lang, content=content))
    
    return blocks


def reconstruct(blocks: list[ContentBlock]) -> str:
    parts = []
    for block in blocks:
        if block.kind == "markup":
            parts.append(block.content)
        elif block.kind == "code":
            lang = block.language or ""
            parts.append(f"```{lang}\n{block.content}\n```")
    return "\n\n".join(parts)


if __name__ == "__main__":
    test1 = 'hi\n\n```python\nprint("hello")\n```\nhoho\n```\nplain code\n```\n\ntext'
    print("Test 1:")
    for block in parse_blocks(test1):
        print(f"  {block}")
    print()

    test2 = 'hi\n\n``` asdf ```'
    print("Test 2 (inline fence):")
    for block in parse_blocks(test2):
        print(f"  {block}")
    print()

    test3 = 'hello\n  ```python\ncode\n```\nworld'
    print("Test 3 (indented fence):")
    for block in parse_blocks(test3):
        print(f"  {block}")
    print()

    test4 = '''intro text
```python
def foo():
    pass
```

middle text
```
no language
```

end text'''
    print("Test 4 (multiple fences):")
    for block in parse_blocks(test4):
        print(f"  {block}")
    print()

    test5 = '```\njust code\n```'
    print("Test 5 (no language multiline):")
    for block in parse_blocks(test5):
        print(f"  {block}")
