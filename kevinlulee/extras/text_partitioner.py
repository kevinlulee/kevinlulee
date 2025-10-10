from dataclasses import dataclass
from typing import List, Literal, Optional

SegmentType = Literal["dash", "fence", "text"]

@dataclass
class Segment:
    type: SegmentType
    content: str  # always stripped

@dataclass
class BlockSpec:
    type: SegmentType
    token: str  # leading delimiter string (e.g., '---', '```')

DEFAULT_SPECS: List[BlockSpec] = [
    BlockSpec("dash", "---"),
    BlockSpec("fence", "```"),
]


def is_dash_line(l: str) -> bool:
    return l.strip() == "---"

def is_fence_line(l: str) -> bool:
    s = l.strip()
    return s.startswith("```")

class TextPartitioner:
    def __init__(self, text: str, include_delimiters: bool = False, specs: Optional[List[BlockSpec]] = None):
        self.text = text
        self.include_delimiters = include_delimiters
        self.specs = specs or DEFAULT_SPECS
        self._segments: List[Segment] = []

    def _which_block(self, line: str) -> Optional[BlockSpec]:
        s = line.strip()
        for spec in self.specs:
            if s.startswith(spec.token):
                return spec
        return None

    def partition(self) -> List[Segment]:
        if self._segments:
            return self._segments

        lines = self.text.splitlines(keepends=True)
        i = 0
        out: List[Segment] = []

        while i < len(lines):
            spec = self._which_block(lines[i])

            if spec:
                buf = [lines[i]]
                i += 1
                while i < len(lines):
                    buf.append(lines[i])
                    if lines[i].strip().startswith(spec.token):
                        i += 1
                        break
                    i += 1

                if self.include_delimiters:
                    content = "".join(buf).strip()
                else:
                    inner = buf[1:]
                    if inner and inner[-1].strip().startswith(spec.token):
                        inner = inner[:-1]
                    content = "".join(inner).strip()

                if content:
                    out.append(Segment(spec.type, content))
                continue

            text_buf = [lines[i]]
            i += 1
            while i < len(lines) and self._which_block(lines[i]) is None:
                text_buf.append(lines[i])
                i += 1
            txt = "".join(text_buf).strip()
            if txt:
                out.append(Segment("text", txt))

        self._segments = out
        return out

    @property
    def segments(self) -> List[Segment]:
        return self._segments or self.partition()

    def to_dicts(self) -> List[dict]:
        return [{"type": seg.type, "content": seg.content} for seg in self.segments]

    def get_by_type(self, t: SegmentType) -> List[Segment]:
        return [seg for seg in self.segments if seg.type == t]
