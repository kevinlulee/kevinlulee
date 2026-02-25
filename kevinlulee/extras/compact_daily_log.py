from __future__ import annotations
import kevinlulee as kx
import os
import os
import json
import functools
from collections import Counter
from kevinlulee.extras.caches import daily_cache


@daily_cache
def compact_daily_log(filepath):
    
    counts = Counter()
    filepath = os.path.expanduser(filepath)
    with open(filepath, "r") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if " | " in line:
            path = line.split(" | ", 1)[1]
            i += 1
            if i < len(lines):
                try:
                    count = int(lines[i].strip())
                    counts[path] += count
                    i += 1
                except ValueError:
                    continue
        else:
            i += 1
    return [{"path": p, "count": c} for p, c in counts.most_common()]



