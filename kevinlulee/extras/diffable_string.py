from __future__ import annotations
import kevinlulee as kx

import re
import difflib
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class LineDiff:
    """Represents a change in one or more lines."""
    line_range: Tuple[int, int]  # (start_line, end_line) 1-indexed, inclusive
    old_text: str
    new_text: str
    
    def to_str(self) -> str:
        """Format the diff for display."""
        if self.line_range[0] == self.line_range[1]:
            # Single line change
            line_num = self.line_range[0]
            result = f"{line_num}: '{self.old_text}' -> '{self.new_text}'"
        else:
            # Multi-line change
            start, end = self.line_range
            old_lines = self.old_text.split('\n')
            result = f"{start}-{end}: '{old_lines[0]}' -> '{self.new_text}'\n"
            for line in old_lines[1:]:
                result += f"     '{line}'\n"
            result = result.rstrip('\n')
        return result


class DiffableString:
    """A string wrapper that tracks changes and provides diff views."""
    
    def __init__(self, text: str):
        self._original = text
        self._current = text
    
    def sub(self, pattern, repl, count=0, flags=0):
        self._current = re.sub(pattern, repl, self._current, count=count, flags=flags)
        return self
    
    def view_diff(self) -> List[LineDiff]:
        """Generate a list of LineDiff objects showing what changed."""
        old_lines = self._original.split('\n')
        new_lines = self._current.split('\n')
        
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        diffs = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Lines were changed
                old_text = '\n'.join(old_lines[i1:i2])
                new_text = '\n'.join(new_lines[j1:j2])
                diffs.append(LineDiff(
                    line_range=(i1 + 1, i2),  # Convert to 1-indexed
                    old_text=old_text,
                    new_text=new_text
                ))
            elif tag == 'delete':
                # Lines were deleted
                old_text = '\n'.join(old_lines[i1:i2])
                diffs.append(LineDiff(
                    line_range=(i1 + 1, i2),
                    old_text=old_text,
                    new_text=''
                ))
            elif tag == 'insert':
                # Lines were inserted
                new_text = '\n'.join(new_lines[j1:j2])
                diffs.append(LineDiff(
                    line_range=(i1 + 1, i1 + 1),  # Insert position
                    old_text='',
                    new_text=new_text
                ))
        
        return "\n".join([diff.to_str() for diff in diffs])
    
    def reset(self):
        """Reset to the original text."""
        self._current = self._original
        return self
