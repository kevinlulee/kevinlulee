"""
LineEdit - A line-oriented text manipulation library

API SUMMARY
-----------
le = LineEdit(text)           # Create editor from string
le.get_line(3)                # Get line by number (1-indexed, negative ok)
le.get_line(r"pattern")       # Get first line matching regex
le.findall(r"pattern")        # Get all lines matching regex
le.capture(start, end)        # Capture region between patterns
le.captures(start, end)       # Capture all such regions
str(le)                       # Render final text

Line methods:
  line.text                   # Get line content
  line.match(r"pat")          # Check if line matches pattern
  line.has_text()             # Check if line has non-whitespace
  line.set(text)              # Replace line content
  line.delete()               # Mark line for deletion
  line.insert_before(text)    # Insert text before this line
  line.insert_after(text)     # Insert text after this line
  line.prev() / line.next()   # Navigate to adjacent lines
  line.seek_above(r"pat")     # Find first matching line above
  line.seek_below(r"pat")     # Find first matching line below

Region methods:
  region.text                 # Get region content
  region.delete()             # Delete entire region
  bool(region)                # False if NullRegion
"""

import re

__all__ = [
    "LineEdit",
]


class NullLine:
    """Sentinel returned when no line is found."""
    __slots__ = ("_parent",)

    def __init__(self, parent):
        self._parent = parent

    def prev(self):
        return self

    def next(self):
        return self

    def seek_above(self, pattern: str):
        return self

    def seek_below(self, pattern: str):
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

    def __bool__(self):
        return False

    def __repr__(self):
        return "<NullLine>"


class Line:
    """Represents a single line in the editor."""
    __slots__ = ("_parent", "_idx", "_deleted")

    def __init__(self, parent, idx: int):
        self._parent = parent
        self._idx = idx
        self._deleted = False

    @property
    def text(self) -> str:
        return self._parent._lines[self._idx]

    @property
    def lnum(self) -> int:
        """1-indexed line number."""
        return self._idx + 1

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

    def _seek(self, pattern: str, direction: int):
        """Internal seek in given direction (-1=above, +1=below)."""
        j = self._idx + direction
        objs = self._parent._objs
        n = len(objs)
        while 0 <= j < n:
            candidate = objs[j]
            if not candidate._deleted and candidate.match(pattern):
                return candidate
            j += direction
        return self._parent._null

    def seek_above(self, pattern: str):
        """Find first line above matching pattern."""
        return self._seek(pattern, -1)

    def seek_below(self, pattern: str):
        """Find first line below matching pattern."""
        return self._seek(pattern, +1)

    def prev(self):
        """Get previous non-deleted line."""
        j = self._idx - 1
        while j >= 0:
            candidate = self._parent._objs[j]
            if not candidate._deleted:
                return candidate
            j -= 1
        return self._parent._null

    def next(self):
        """Get next non-deleted line."""
        j = self._idx + 1
        n = len(self._parent._objs)
        while j < n:
            candidate = self._parent._objs[j]
            if not candidate._deleted:
                return candidate
            j += 1
        return self._parent._null

    def set(self, text: str):
        """Replace this line's content."""
        segs = self._normalize_segments(text)
        self._parent._lines[self._idx] = segs[0]
        if len(segs) > 1:
            tail = segs[1:]
            bucket = self._parent._inserts_after.setdefault(self._idx, [])
            bucket.extend(tail)

    def insert_before(self, text: str):
        """Insert text before this line."""
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_before.setdefault(self._idx, [])
        bucket.extend(segs)

    def insert_after(self, text: str):
        """Insert text after this line."""
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_after.setdefault(self._idx, [])
        bucket.extend(segs)

    def __bool__(self):
        return True

    def __repr__(self):
        state = "deleted" if self._deleted else "alive"
        return f"<Line {self._idx} {state}: {self.text!r}>"


class NullRegion:
    """Sentinel returned when no region is captured."""
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


class Region:
    """A contiguous range of lines."""
    __slots__ = ("_parent", "_start", "_end")

    def __init__(self, parent, start_idx: int, end_idx: int):
        self._parent = parent
        self._start = start_idx
        self._end = end_idx

    def delete(self):
        """Delete all lines in this region."""
        for i in range(self._start, self._end + 1):
            self._parent._objs[i]._deleted = True

    @property
    def text(self) -> str:
        return "".join(self._parent._lines[self._start : self._end + 1])

    @property
    def start_line(self):
        """First line of region."""
        return self._parent._objs[self._start]

    @property
    def end_line(self):
        """Last line of region."""
        return self._parent._objs[self._end]

    def __bool__(self):
        return True

    def __repr__(self):
        return f"<Region lines {self._start}-{self._end}>"


class LineEdit:
    """Line-oriented text editor."""
    __slots__ = (
        "_original",
        "_lines",
        "_objs",
        "_null",
        "_inserts_before",
        "_inserts_after",
    )

    def __init__(self, s: str):
        s = s.strip()
        self._original = s
        self._lines = s.splitlines(keepends=True)
        if len(self._lines) == 0:
            self._lines = [""]
        self._objs = [Line(self, i) for i in range(len(self._lines))]
        self._null = NullLine(self)
        self._inserts_before = {}
        self._inserts_after = {}

    def get_line(self, key):
        """
        Get a line by number or pattern.
        
        Args:
            key: int (1-indexed, negative ok) or str (regex pattern)
        
        Returns:
            Line or NullLine
        """
        if isinstance(key, int):
            n = len(self._objs)
            if key == 0:
                return self._null
            if key > 0:
                idx = key - 1
            else:
                idx = n + key
            if 0 <= idx < n and not self._objs[idx]._deleted:
                return self._objs[idx]
            return self._null
        else:
            for obj in self._objs:
                if not obj._deleted and obj.match(key):
                    return obj
            return self._null

    def findall(self, pattern: str):
        """Find all lines matching pattern."""
        out = []
        for obj in self._objs:
            if obj._deleted:
                continue
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
        Capture a region from start pattern to end pattern.
        
        Args:
            start: Regex for region start
            end: Regex for region end
            start_from: None, int index, or Line
            greedy_end: Extend to last consecutive end match
            skip_blank_after_end: Allow blank lines between end matches
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
            return NullRegion(self)

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

        return Region(self, start_idx, end_idx)

    def captures(
        self,
        start: str,
        end: str,
        *,
        start_from=None,
        greedy_end: bool = True,
        skip_blank_after_end: bool = True,
    ):
        """Capture all non-overlapping regions matching start/end."""
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

    def __len__(self):
        return sum(1 for o in self._objs if not o._deleted)

    def __iter__(self):
        for obj in self._objs:
            if not obj._deleted:
                yield obj

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


