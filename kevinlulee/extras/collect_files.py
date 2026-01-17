from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from kevinlulee.extras.parse_date_range import parse_date_range

@dataclass
class FileFilter:
    """
    Flexible file filter with size, extension, date, and pattern matching.

    Parameters:
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        exts: Allowed extensions (without dots, case-insensitive)
        after: Only files modified after this datetime
        before: Only files modified before this datetime
        include: Regex patterns - path must match at least one
        exclude: Regex patterns - path must not match any
    """
    min_size: int = 0
    max_size: int | None = None
    exts: list[str] | None = None
    after: datetime | None = None
    before: datetime | None = None
    include: list[str] | None = None
    exclude: list[str] | None = None

    def __post_init__(self):
        self._exts_lower = [e.lower() for e in self.exts] if self.exts else None
        self._include_re = [re.compile(p) for p in self.include] if self.include else None
        self._exclude_re = [re.compile(p) for p in self.exclude] if self.exclude else None

    def matches(self, path: str | Path, stat: os.stat_result | None = None) -> bool:
        p = Path(path)
        if stat is None:
            try:
                stat = p.stat()
            except OSError:
                return False
        if stat.st_size < self.min_size:
            return False
        if self.max_size is not None and stat.st_size > self.max_size:
            return False
        if self._exts_lower:
            ext = p.suffix.lstrip('.').lower()
            if ext not in self._exts_lower:
                return False
        mtime = datetime.fromtimestamp(stat.st_mtime)
        if self.after and mtime <= self.after:
            return False
        if self.before and mtime >= self.before:
            return False
        path_str = str(p)
        if self._include_re and not any(r.search(path_str) for r in self._include_re):
            return False
        if self._exclude_re and any(r.search(path_str) for r in self._exclude_re):
            return False
        return True


DEFAULT_EXCLUDE_DIRS = {
    '__pycache__', 'node_modules', '.git', '.svn', '.hg',
    'dist', 'build', '.tox', '.nox', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', 'venv', '.venv', 'env',
    '.env', 'egg-info', '.eggs', '.idea', '.vscode'
}


def collect_files(
    paths: str | Path | list[str | Path],
    *,
    min_size: int = 0,
    max_size: int | None = None,
    exts: list[str] | None = None,
    after: datetime | None = None,
    before: datetime | None = None,
    date_range: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    recursive: bool = True,
    exclude_dirs: set[str] | None = DEFAULT_EXCLUDE_DIRS
) -> list[str]:
    """
    Collect files from paths with optional filtering.

    Parameters:
        paths: File/directory path(s) to search (supports ~ expansion)
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        exts: Allowed extensions (without dots, case-insensitive)
        after: Only files modified after this datetime
        before: Only files modified before this datetime
        date_range: Date range string (parsed via parse_date_range), overrides after/before
        include: Regex patterns - path must match at least one
        exclude: Regex patterns - path must not match any
        recursive: Search subdirectories
        exclude_dirs: Directory names to skip. Pass None to include all.

    Returns:
        List of absolute file paths as strings.
    """
    if isinstance(paths, (str, Path)):
        paths = [paths]
    
    if date_range:
        after, before = parse_date_range(date_range)
    
    filt = FileFilter(min_size, max_size, exts, after, before, include, exclude)
    exclude_dirs = exclude_dirs or set()
    results = []
    
    for p in paths:
        p = Path(p).expanduser().resolve()
        
        if p.is_file():
            try:
                stat = p.stat()
                if filt.matches(p, stat):
                    results.append(str(p))
            except OSError:
                pass
        elif p.is_dir():
            if recursive:
                for root, dirs, files in os.walk(p):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    for f in files:
                        fp = Path(root) / f
                        try:
                            stat = fp.stat()
                            if filt.matches(fp, stat):
                                results.append(str(fp))
                        except OSError:
                            continue
            else:
                for fp in p.iterdir():
                    if fp.is_file():
                        try:
                            stat = fp.stat()
                            if matches(fp, stat):
                                results.append(str(fp))
                        except OSError:
                            continue

    return results
