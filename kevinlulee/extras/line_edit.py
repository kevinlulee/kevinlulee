import re

class _NullLine:
    __slots__ = ("_parent",)

    def __init__(self, parent):
        self._parent = parent

    def prev(self):
        return self

    def next(self):
        return self

    def match(self, pattern: str) -> bool:
        return False

    def has_text(self) -> bool:
        return False

    def delete(self):
        return None

    def set(self, text: str):
        return None

    def insert_before(self, text: str):
        return None

    def insert_after(self, text: str):
        return None

    @property
    def text(self) -> str:
        return ""

    def __repr__(self):
        return "<NullLine>"


class _Line:
    __slots__ = ("_parent", "_idx", "_deleted")

    def __init__(self, parent, idx: int):
        self._parent = parent
        self._idx = idx
        self._deleted = False

    @property
    def text(self) -> str:
        return self._parent._lines[self._idx]

    def _stripped(self) -> str:
        return self.text.rstrip("\r\n").strip()

    def _default_eol(self) -> str:
        seg = self._parent._lines[self._idx]
        m = re.search(r"(\r\n|\r|\n)$", seg)
        return m.group(1) if m else "\n"

    def _normalize_segments(self, text: str):
        """
        Split incoming text into line segments w/ eols.
        If the last segment lacks an EOL, append this line's default EOL
        so inserts are true *lines* (don’t glue to neighbors).
        """
        segs = text.splitlines(keepends=True)
        if not segs:
            # Treat empty text as an empty line with default EOL
            return [self._default_eol()]
        last = segs[-1]
        if not re.search(r"(\r\n|\r|\n)$", last):
            segs[-1] = last + self._default_eol()
        return segs

    def match(self, pattern: str) -> bool:
        """
        Full-match against the STRIPPED line (no leading/trailing spaces, no EOL).
        pattern == "" means 'blank line' (after stripping).
        """
        if self._deleted:
            return False
        if pattern == "":
            return self._stripped() == ""
        return re.search(pattern, self.text) is not None

    def has_text(self) -> bool:
        if self._deleted:
            return False
        return self._stripped() != ""

    def delete(self):
        self._deleted = True

    def prev(self):
        j = self._idx - 1
        while j >= 0:
            candidate = self._parent._objs[j]
            if not candidate._deleted:
                return candidate
            j -= 1
        return self._parent._null

    def next(self):
        j = self._idx + 1
        n = len(self._parent._objs)
        while j < n:
            candidate = self._parent._objs[j]
            if not candidate._deleted:
                return candidate
            j += 1
        return self._parent._null

    # -------- new editing ops --------

    def set(self, text: str):
        """
        Replace this line’s text.
        If `text` contains multiple lines:
          - the first segment replaces this line
          - the remaining segments are inserted *after* this line (in order)
        """
        segs = self._normalize_segments(text)
        self._parent._lines[self._idx] = segs[0]
        if len(segs) > 1:
            tail = segs[1:]
            bucket = self._parent._inserts_after.setdefault(self._idx, [])
            bucket.extend(tail)

    def insert_before(self, text: str):
        """
        Insert one or more lines immediately before this line.
        """
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_before.setdefault(self._idx, [])
        bucket.extend(segs)

    def insert_after(self, text: str):
        """
        Insert one or more lines immediately after this line.
        """
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_after.setdefault(self._idx, [])
        bucket.extend(segs)

    def __repr__(self):
        state = "deleted" if self._deleted else "alive"
        return f"<Line {self._idx} {state}: {self._stripped()!r}>"


class LineEdit:
    """
    Line-wise editor with stable handles.

    - `findall(pattern)` returns live line handles matching `pattern`.
      * pattern == "" matches blank (stripped) lines
      * otherwise uses `re.fullmatch` against the stripped text
    - Line ops: prev(), next(), match(), has_text(), delete(), set(text),
      insert_before(text), insert_after(text), .text

    Insertions are queued (not index-shifting); output is materialized on `str()`.
    """
    __slots__ = ("_original", "_lines", "_objs", "_null",
                 "_inserts_before", "_inserts_after")

    def __init__(self, s: str):
        self._original = s
        self._lines = s.splitlines(keepends=True)
        if len(self._lines) == 0:
            self._lines = [""]
        self._objs = [_Line(self, i) for i in range(len(self._lines))]
        self._null = _NullLine(self)
        self._inserts_before = {}  # idx -> [segments]
        self._inserts_after = {}   # idx -> [segments]

    def findall(self, pattern: str):
        out = []
        for obj in self._objs:
            if obj._deleted:
                continue
            if pattern == "":
                if obj.match(""):
                    out.append(obj)
            else:
                if obj.match(pattern):
                    out.append(obj)
        return out

    def __str__(self) -> str:
        parts = []
        for idx, seg in enumerate(self._lines):
            if idx in self._inserts_before:
                parts.extend(self._inserts_before[idx])
            if not self._objs[idx]._deleted:
                parts.append(seg)
            if idx in self._inserts_after:
                parts.extend(self._inserts_after[idx])
        return "".join(parts)

