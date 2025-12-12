from __future__ import annotations
import kevinlulee as kx


import re
from dataclasses import dataclass
from typing import Literal
import kevinlulee as kx


@dataclass
class ContentBlock:
    lang: Literal["code", "markup", "python"]
    text: str

def split_python_code_and_markup(input_text: str) -> list[ContentBlock]:
    """
    first used to split mixed python code and markup for
    long division worksheet.
    """
    
    patterns = [
        '^(?:if|elif|else|for|while|with|try|except|finally|def|class|async def).*?:',
        '^\w+(?:\.\w+|\[.*?\])*(?:\(| *=)',
        '^(?:import \w+|from \w+ import)',
        '^(?:assert|raise)',
    ]
    patterns = kx.map(patterns, re.compile)

    def classify(s):
        for pattern in patterns:
            if pattern.match(s):
                return 'python'

        return 'markup'
        
    # chunks = kx.split(input_text, )
    chunks = re.split('(?=\n[a-zA-Z])', input_text)
    classified_segments = []
    for chunk in chunks:
        type = classify(chunk.strip())
        classified_segments.append((type, chunk))
        
    merged: list[ContentBlock] = []
    for seg_type, seg_text in classified_segments:
        if merged and merged[-1].lang == seg_type:
            merged[-1].text += seg_text
        else:
            merged.append(ContentBlock(lang=seg_type, text=seg_text))
    
    for el in merged:
        el.text = el.text.strip()
    return merged

# Sample call
sample_input = """
def foobar():
    pass

prose

callable()

a = 1

class Foo:
    pass

some more prose here
this is also prose

more prose

if a == 1:
    pass
else:
    pass

foobar(
    'hi'
)


def foo():
    a = 1
    a = 1
    a = 1
    a = 1
    a = 1
    def foo():
        return

def foo():
    pass

asdf

all of this is text
all of this is text

a = [
    1, 2, 3
]
hummy
b = {

}
yummy

dict(
    a = 1
)
"""

if __name__ == '__main__':
    blocks = split_python_code_and_markup(sample_input)
    for block in blocks:
        print(block.lang)
        print(block.text)
        print("--------------------------------")
