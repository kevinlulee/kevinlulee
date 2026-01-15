"""
LineEdit - A line-oriented text manipulation library

API SUMMARY
-----------
le = LineEdit(text)           # Create editor from string
le[3]                         # Get line by index (0-indexed, negative ok)
le.find(r"pattern")           # Get first line matching regex
le.findall(r"pattern")        # Get all lines matching regex
le.split(r"pattern")          # Split into regions by delimiter
str(le)                       # Render final text

Line methods:
  line.text                   # Get line content
  line.idx                    # Get 0-indexed position
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
  region[0]                   # Get line by index within region
  region.text                 # Get region content
  region.start / region.end   # First/last line of region
  region.delete()             # Delete entire region
  region.find(r"pat")         # Find first matching line in region
  region.findall(r"pat")      # Find all matching lines in region
  region.prepend(text)        # Insert text before region
  region.append(text)         # Insert text after region
  bool(region)                # False if NullRegion
"""

import re

__all__ = ["LineEdit"]


class NullLine:
    __slots__ = ("_parent",)

    def __init__(self, parent):
        self._parent = parent

    def prev(self): return self
    def next(self): return self
    def seek_above(self, pattern: str): return self
    def seek_below(self, pattern: str): return self
    def match(self, pattern: str) -> bool: return False
    def has_text(self) -> bool: return False
    def delete(self): return None
    def set(self, text: str): return None
    def insert_before(self, text: str): return None
    def insert_after(self, text: str): return None
    @property
    def text(self) -> str: return ""
    @property
    def idx(self) -> int: return -1
    def __bool__(self): return False
    def __repr__(self): return "<NullLine>"


class Line:
    __slots__ = ("_parent", "_idx", "_deleted")

    def __init__(self, parent, idx: int):
        self._parent = parent
        self._idx = idx
        self._deleted = False

    @property
    def text(self) -> str:
        return self._parent._lines[self._idx]

    @property
    def idx(self) -> int:
        return self._idx

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
        return self._seek(pattern, -1)

    def seek_below(self, pattern: str):
        return self._seek(pattern, +1)

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
            bucket = self._parent._inserts_after.setdefault(self._idx, [])
            bucket.extend(segs[1:])

    def insert_before(self, text: str):
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_before.setdefault(self._idx, [])
        bucket.extend(segs)

    def insert_after(self, text: str):
        segs = self._normalize_segments(text)
        bucket = self._parent._inserts_after.setdefault(self._idx, [])
        bucket.extend(segs)

    def __bool__(self): return True
    def __repr__(self):
        state = "deleted" if self._deleted else "alive"
        return f"<Line {self._idx} {state}: {self.text!r}>"


class NullRegion:
    __slots__ = ("_parent",)

    def __init__(self, parent):
        self._parent = parent

    def delete(self): return None
    def find(self, pattern: str): return self._parent._null
    def findall(self, pattern: str): return []
    @property
    def text(self) -> str: return ""
    @property
    def start(self): return self._parent._null
    @property
    def end(self): return self._parent._null
    def __bool__(self): return False
    def __iter__(self): return iter([])
    def __getitem__(self, key): return self._parent._null
    def __len__(self): return 0
    def __repr__(self): return "<NullRegion>"


class Region:
    __slots__ = ("_parent", "_start", "_end", "_indices")

    def __init__(self, parent, start_idx: int, end_idx: int):
        self._parent = parent
        self._start = start_idx
        self._end = end_idx
        self._indices = None

    def _get_indices(self):
        if self._indices is None:
            self._indices = [
                i for i in range(self._start, self._end + 1)
                if not self._parent._objs[i]._deleted
            ]
        return self._indices

    def __getitem__(self, key: int):
        indices = self._get_indices()
        n = len(indices)
        if key < 0:
            key = n + key
        if 0 <= key < n:
            return self._parent._objs[indices[key]]
        return self._parent._null

    def __len__(self):
        return len(self._get_indices())

    def delete(self):
        for i in range(self._start, self._end + 1):
            self._parent._objs[i]._deleted = True

    @property
    def text(self) -> str:
        return "".join(self._parent._lines[self._start : self._end + 1])

    @property
    def start(self):
        return self._parent._objs[self._start]

    @property
    def end(self):
        return self._parent._objs[self._end]

    def __iter__(self):
        for i in range(self._start, self._end + 1):
            obj = self._parent._objs[i]
            if not obj._deleted:
                yield obj

    def find(self, pattern: str):
        for line in self:
            if line.match(pattern):
                return line
        return self._parent._null

    def findall(self, pattern: str):
        return [line for line in self if line.match(pattern)]

    def prepend(self, text: str):
        """Insert text before the first line of the region."""
        self._parent._objs[self._start].insert_before(text)

    def append(self, text: str):
        """Insert text after the last line of the region."""
        last = self._parent._objs[self._end]
        last.insert_after(text)

    def __bool__(self): return True
    def __repr__(self): return f"<Region lines {self._start}-{self._end}>"


class LineEdit:
    __slots__ = (
        "_original", "_lines", "_objs", "_null",
        "_inserts_before", "_inserts_after",
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

    def __getitem__(self, key: int):
        n = len(self._objs)
        if key < 0:
            key = n + key
        if 0 <= key < n and not self._objs[key]._deleted:
            return self._objs[key]
        return self._null

    def get_line(self, idx: int):
        """Get line by 0-indexed position."""
        return self[idx]

    def find(self, pattern: str):
        for obj in self._objs:
            if not obj._deleted and obj.match(pattern):
                return obj
        return self._null

    def findall(self, pattern: str):
        return [obj for obj in self._objs if not obj._deleted and obj.match(pattern)]

    def split(self, pattern: str):
        """Split into regions by delimiter pattern. Returns regions BETWEEN delimiters."""
        delimiters = [obj._idx for obj in self._objs if not obj._deleted and obj.match(pattern)]
        
        if not delimiters:
            return [Region(self, 0, len(self._objs) - 1)]
        
        regions = []
        for i, delim_idx in enumerate(delimiters):
            if i + 1 < len(delimiters):
                # Region between this delimiter and next
                start = delim_idx + 1
                end = delimiters[i + 1] - 1
                if start <= end:
                    regions.append(Region(self, start, end))
            else:
                # Region after last delimiter to EOF
                start = delim_idx + 1
                end = len(self._objs) - 1
                if start <= end:
                    regions.append(Region(self, start, end))
        
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
