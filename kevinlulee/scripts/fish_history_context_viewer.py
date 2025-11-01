"""
First used on 2025-11-01.

The goal was to try and find treesitter entries for how to install.

https://claude.ai/chat/747cd57d-ec87-49b5-91d6-77b6dd715631 (passing the log to claude to tell him how to write a script to install treesitter packages from python)
"""

import kevinlulee as kx
from datetime import datetime, timedelta
from pathlib import Path
import yaml


def parse_fish_history():
    """Parse fish shell history file and return list of entries with timestamps."""
    history_path = Path.home() / ".local/share/fish/fish_history"
    
    if not history_path.exists():
        return []
    
    entries = []
    current_entry = {}
    
    with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('- cmd: '):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {'cmd': line[7:]}
            elif line.startswith('  when: '):
                current_entry['when'] = int(line[8:])
    
    if current_entry:
        entries.append(current_entry)
    
    return entries


def fish_history_context_viewer(term = 'tree-sitter'):
    """
    Find all fish history entries starting with 'treesitter' and collect
    all entries within 15 minutes before and after each match.
    Returns a list of human-readable strings.
    """
    entries = parse_fish_history()
    
    if not entries:
        return ["No fish history found"]
    
    # Find all treesitter entries
    treesitter_indices = []
    for i, entry in enumerate(entries):
        if entry['cmd'].startswith(term):
            treesitter_indices.append(i)
    
    if not treesitter_indices:
        return [f"No {term} commands found in history"]
    
    result = []
    time_window = timedelta(minutes=15)
    
    for idx in treesitter_indices:
        treesitter_entry = entries[idx]
        treesitter_time = datetime.fromtimestamp(treesitter_entry['when'])
        
        # Find entries within 15 minutes
        context_entries = []
        
        for i, entry in enumerate(entries):
            if 'when' not in entry:
                continue
            
            entry_time = datetime.fromtimestamp(entry['when'])
            time_diff = abs(entry_time - treesitter_time)
            
            if time_diff <= time_window:
                context_entries.append((i, entry, entry_time))
        
        # Sort by timestamp
        context_entries.sort(key=lambda x: x[2])
        
        # Build human-readable string
        lines = []
        lines.append("=" * 80)
        lines.append(f"Treesitter command at {treesitter_time.strftime('%Y-%m-%d %H:%M:%S')}:")
        lines.append(f"  → {treesitter_entry['cmd']}")
        lines.append("")
        lines.append("Context (±15 minutes):")
        lines.append("-" * 80)
        
        for i, entry, entry_time in context_entries:
            time_marker = "***" if i == idx else "   "
            relative_time = int((entry_time - treesitter_time).total_seconds() / 60)
            time_str = f"{relative_time:+3d}m" if relative_time != 0 else "  0m"
            timestamp = entry_time.strftime('%H:%M:%S')
            
            lines.append(f"{time_marker} [{timestamp}] ({time_str}) {entry['cmd']}")
        
        lines.append("")
        result.append(kx.join_text(lines))
    
    return result


if __name__ == "__main__":
    results = fish_history_context_viewer()
    output = kx.join_text(results)
    kx.clip(output)
