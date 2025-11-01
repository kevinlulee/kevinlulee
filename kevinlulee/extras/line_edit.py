import re
import kevinlulee as kx

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
        segs = text.splitlines(keepends=True)
        if not segs:
            return [self._default_eol()]
        last = segs[-1]
        if not re.search(r"(\r\n|\r|\n)$", last):
            segs[-1] = last + self._default_eol()
        return segs

    def match(self, pattern: str) -> bool:
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

    def set(self, text: str):
        segs = self._normalize_segments(text)
        self._parent._lines[self._idx] = segs[0]
        if len(segs) > 1:
            tail = segs[1:]
            bucket = self._parent._inserts_after.setdefault(self._idx, [])
            bucket.extend(tail)

    def insert_before(self, text: str):
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_before.setdefault(self._idx, [])
        bucket.extend(segs)

    def insert_after(self, text: str):
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_after.setdefault(self._idx, [])
        bucket.extend(segs)

    def __repr__(self):
        state = "deleted" if self._deleted else "alive"
        return f"<Line {self._idx} {state}: {self._stripped()!r}>"


class _NullRegion:
    __slots__ = ("_parent",)

    def __init__(self, parent):
        self._parent = parent

    def delete(self):
        return None

    @property
    def text(self) -> str:
        return ""

    def __bool__(self):
        return False

    def __repr__(self):
        return "<NullRegion>"


class _Region:
    __slots__ = ("_parent", "_start", "_end")

    def __init__(self, parent, start_idx: int, end_idx: int):
        self._parent = parent
        self._start = start_idx
        self._end = end_idx

    def delete(self):
        for i in range(self._start, self._end + 1):
            self._parent._objs[i]._deleted = True

    @property
    def text(self) -> str:
        return "".join(self._parent._lines[self._start:self._end + 1])

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<Region {self._start}:{self._end}>"


class LineEdit:
    __slots__ = ("_original", "_lines", "_objs", "_null",
                 "_inserts_before", "_inserts_after")

    def __init__(self, s: str):
        s = s.strip()
        self._original = s
        self._lines = s.splitlines(keepends=True)
        if len(self._lines) == 0:
            self._lines = [""]
        self._objs = [_Line(self, i) for i in range(len(self._lines))]
        self._null = _NullLine(self)
        self._inserts_before = {}
        self._inserts_after = {}

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

    def _is_blank_idx(self, idx: int) -> bool:
        if idx < 0 or idx >= len(self._objs):
            return False
        if self._objs[idx]._deleted:
            return False
        seg = self._lines[idx]
        return seg.rstrip("\r\n").strip() == ""

    def _first_start_from(self, start_pat: str, from_idx: int) -> int:
        n = len(self._objs)
        i = from_idx
        while i < n:
            o = self._objs[i]
            if not o._deleted and re.search(start_pat, o.text) is not None:
                return i
            i += 1
        return -1

    def capture(
        self,
        start: str,
        end: str,
        *,
        start_from=None,
        greedy_end: bool = True,
        skip_blank_after_end: bool = True,
    ):
        """
        Capture region beginning at the first line >= start_from that matches `start`,
        and ending at the (optionally greedy) match(es) of `end`.
        If no end is found, extends to EOF.
        start_from may be None, an int index, or a _Line.
        """
        n = len(self._objs)

        if start_from is None:
            from_idx = 0
        elif isinstance(start_from, int):
            from_idx = max(0, min(start_from, n))
        else:
            from_idx = start_from._idx

        start_idx = self._first_start_from(start, from_idx)
        if start_idx == -1:
            return _NullRegion(self)

        end_idx = -1
        j = start_idx
        while j < n:
            obj = self._objs[j]
            if not obj._deleted and re.search(end, obj.text) is not None:
                end_idx = j

                if greedy_end:
                    k = j + 1
                    last_good = j
                    while k < n:
                        if self._objs[k]._deleted:
                            k += 1
                            continue
                        text_matches = re.search(end, self._objs[k].text) is not None
                        if text_matches:
                            last_good = k
                            k += 1
                            continue
                        if skip_blank_after_end and self._is_blank_idx(k):
                            k += 1
                            continue
                        break
                    end_idx = last_good
                break
            j += 1

        if end_idx == -1:
            end_idx = n - 1

        return _Region(self, start_idx, end_idx)

    def captures(
        self,
        start: str,
        end: str,
        *,
        start_from=None,
        greedy_end: bool = True,
        skip_blank_after_end: bool = True,
    ):
        """
        Iterate capture() left-to-right, using each region's end line + 1
        as the next search start line.
        Returns a list of _Region objects (may be empty).
        """
        regions = []
        n = len(self._objs)

        if start_from is None:
            from_idx = 0
        elif isinstance(start_from, int):
            from_idx = max(0, min(start_from, n))
        else:
            from_idx = start_from._idx

        while from_idx < n:
            r = self.capture(
                start,
                end,
                start_from=from_idx,
                greedy_end=greedy_end,
                skip_blank_after_end=skip_blank_after_end,
            )
            if not r:
                break
            regions.append(r)
            from_idx = r._end + 1
        return regions

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


# ---------- single example ----------

sample_text = (
    "header line\n"
    "header line\n"
    "header line\n"
    "abc123 start of block A\n"
    "some content A1\n"
    "❯ node_modules/.pnpm\n"
    "❯ node_modules/.pnpm\n"
    "\n"
    "\n"
    "\n"
    "❯ node_modules/.pnpm\n"
    "❯ node_modules/.pnpm\n"
    "\n"
    "abcXYZ start of block B\n"
    "content B1\n"
    "❯ node_modules/.pnpm\n"
    "tail line\n"
)


