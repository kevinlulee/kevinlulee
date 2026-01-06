"""
this file is for analyzing '/home/kdog3682/data/all_file_saves.log'.
the output is pretty interesting.

it shows associations between files.
"""

from __future__ import annotations
import kevinlulee as kx


from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field
import re
from pathlib import Path


SKIP_PATTERNS = {"temp", "playground", "scratch"}


@dataclass
class FileAssociation:
    file_a: str
    file_b: str
    co_occurrence_count: int
    avg_time_delta_seconds: float
    a_before_b_count: int
    b_before_a_count: int

    @property
    def leader(self) -> str:
        return self.file_a if self.a_before_b_count >= self.b_before_a_count else self.file_b

    @property
    def follower(self) -> str:
        return self.file_b if self.leader == self.file_a else self.file_a


@dataclass
class FileNode:
    path: str
    children: list[str] = field(default_factory=list)
    parent: str | None = None
    save_count: int = 0


def should_skip_file(filepath: str) -> bool:
    """Check if file should be skipped based on basename patterns."""
    basename = Path(filepath).stem.lower()
    return any(pattern in basename for pattern in SKIP_PATTERNS)


def get_extension(filepath: str) -> str:
    """Get file extension (lowercase, without dot)."""
    return Path(filepath).suffix.lower().lstrip(".")


def parse_save_log(raw_data: str) -> list[tuple[datetime, str]]:
    """Parse the raw log data into (timestamp, filepath) tuples."""
    entries = []
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (.+)"
    
    for line in raw_data.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            ts = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            filepath = match.group(2).strip()
            
            if should_skip_file(filepath):
                continue
                
            entries.append((ts, filepath))
    
    return sorted(entries, key=lambda x: x[0])


def find_file_associations(
    entries: list[tuple[datetime, str]],
    window_seconds: float = 60.0,
    min_co_occurrences: int = 3
) -> list[FileAssociation]:
    """
    Find files that are frequently saved within a time window of each other.
    Only associates files with matching extensions.
    """
    pair_data = defaultdict(lambda: {"count": 0, "deltas": [], "a_first": 0, "b_first": 0})
    
    for i, (ts_a, file_a) in enumerate(entries):
        ext_a = get_extension(file_a)
        
        for j in range(i + 1, len(entries)):
            ts_b, file_b = entries[j]
            delta = (ts_b - ts_a).total_seconds()
            
            if delta > window_seconds:
                break
            
            if file_a == file_b:
                continue
            
            ext_b = get_extension(file_b)
            if ext_a != ext_b:
                continue
            
            key = tuple(sorted([file_a, file_b]))
            pair_data[key]["count"] += 1
            pair_data[key]["deltas"].append(delta)
            
            if key[0] == file_a:
                pair_data[key]["a_first"] += 1
            else:
                pair_data[key]["b_first"] += 1
    
    associations = []
    for (file_a, file_b), data in pair_data.items():
        if data["count"] >= min_co_occurrences:
            associations.append(FileAssociation(
                file_a=file_a,
                file_b=file_b,
                co_occurrence_count=data["count"],
                avg_time_delta_seconds=sum(data["deltas"]) / len(data["deltas"]),
                a_before_b_count=data["a_first"],
                b_before_a_count=data["b_first"]
            ))
    
    return sorted(associations, key=lambda x: -x.co_occurrence_count)


def build_hierarchy(associations: list[FileAssociation], strength_threshold: float = 0.6) -> dict[str, FileNode]:
    """Build a hierarchy of files based on save order patterns."""
    nodes: dict[str, FileNode] = {}
    
    for assoc in associations:
        for f in [assoc.file_a, assoc.file_b]:
            if f not in nodes:
                nodes[f] = FileNode(path=f)
    
    for assoc in associations:
        total = assoc.a_before_b_count + assoc.b_before_a_count
        if total == 0:
            continue
        
        a_ratio = assoc.a_before_b_count / total
        
        if a_ratio >= strength_threshold:
            parent, child = assoc.file_a, assoc.file_b
        elif a_ratio <= (1 - strength_threshold):
            parent, child = assoc.file_b, assoc.file_a
        else:
            continue
        
        child_node = nodes[child]
        if child_node.parent is None:
            child_node.parent = parent
            nodes[parent].children.append(child)
    
    return nodes


def get_file_clusters(associations: list[FileAssociation], min_strength: int = 2) -> list[set[str]]:
    """Group files into clusters based on associations."""
    adj = defaultdict(set)
    
    for assoc in associations:
        if assoc.co_occurrence_count >= min_strength:
            adj[assoc.file_a].add(assoc.file_b)
            adj[assoc.file_b].add(assoc.file_a)
    
    visited = set()
    clusters = []
    
    def dfs(node, cluster):
        if node in visited:
            return
        visited.add(node)
        cluster.add(node)
        for neighbor in adj[node]:
            dfs(neighbor, cluster)
    
    for file in adj:
        if file not in visited:
            cluster = set()
            dfs(file, cluster)
            if cluster:
                clusters.append(cluster)
    
    return sorted(clusters, key=len, reverse=True)


def analyze_file_saves(
    raw_data: str,
    window_seconds: float = 60.0,
    min_co_occurrences: int = 3
) -> dict:
    """
    Main analysis function.
    
    Returns dict with:
        - associations: List of FileAssociation objects (grouped by extension)
        - hierarchy: Dict of filepath -> FileNode
        - clusters: List of sets of related files
        - file_save_counts: Dict of filepath -> total saves
        - by_extension: Dict of extension -> associations for that type
    """
    entries = parse_save_log(kx.text_getter(raw_data))
    
    save_counts = defaultdict(int)
    for _, filepath in entries:
        save_counts[filepath] += 1
    
    associations = find_file_associations(entries, window_seconds, min_co_occurrences)
    hierarchy = build_hierarchy(associations)
    clusters = get_file_clusters(associations)
    
    # Group associations by extension
    by_extension = defaultdict(list)
    for assoc in associations:
        ext = get_extension(assoc.file_a)
        by_extension[ext].append(assoc)
    
    for path, node in hierarchy.items():
        node.save_count = save_counts[path]
    
    return {
        "associations": associations,
        "hierarchy": hierarchy,
        "clusters": clusters,
        "file_save_counts": dict(save_counts),
        "by_extension": dict(by_extension),
        "total_entries": len(entries)
    }


def print_analysis(result: dict):
    """Pretty print the analysis results."""
        
    # logger = Logger()
    # print = logger.log
    print(f"Total save events: {result['total_entries']}")
    # logger.get_logs()
    print(f"Unique files: {len(result['file_save_counts'])}")
    print(f"File clusters found: {len(result['clusters'])}")
    print(f"Extensions found: {', '.join(result['by_extension'].keys())}")
    print()
    
    for ext, assocs in result["by_extension"].items():
        print("=" * 60)
        print(f"ASSOCIATIONS FOR .{ext} FILES")
        print("=" * 60)
        for assoc in assocs[:10]:
            short_a = Path(assoc.file_a).name
            short_b = Path(assoc.file_b).name
            leader_indicator = "→" if assoc.leader == assoc.file_a else "←"
            print(f"{short_a} {leader_indicator} {short_b}")
            print(f"  co-saves: {assoc.co_occurrence_count}, avg delta: {assoc.avg_time_delta_seconds:.1f}s")
            print(f"  order: {short_a} first {assoc.a_before_b_count}x, {short_b} first {assoc.b_before_a_count}x")
            print()
    
    print("=" * 60)
    print("FILE CLUSTERS (by extension)")
    print("=" * 60)
    for i, cluster in enumerate(result["clusters"], 1):
        if not cluster:
            continue
        sample_file = next(iter(cluster))
        ext = get_extension(sample_file)
        print(f"\nCluster {i} - .{ext} ({len(cluster)} files):")
        for f in sorted(cluster):
            short = Path(f).name
            saves = result["file_save_counts"].get(f, 0)
            node = result["hierarchy"].get(f)
            parent_info = f" (parent: {Path(node.parent).name})" if node and node.parent else ""
            print(f"  - {short} [{saves} saves]{parent_info}")
    
    print("\n" + "=" * 60)
    print("HIERARCHY ROOTS (files that lead others)")
    print("=" * 60)
    for path, node in result["hierarchy"].items():
        if node.parent is None and node.children:
            short = Path(path).name
            ext = get_extension(path)
            print(f"\n[.{ext}] {short} [{node.save_count} saves]")
            for child in node.children:
                child_short = Path(child).name
                child_node = result["hierarchy"][child]
                print(f"  └─ {child_short} [{child_node.save_count} saves]")


s = """

2025-12-04 16:37:40 | ~/projects/python/maelstrom/lib/nvim/plugins/v1/visual.py
2025-12-04 16:38:19 | ~/projects/python/maelstrom/lib/nvim/plugins/v1/visual.py
2025-12-04 17:15:48 | ~/projects/python/aicmp/request.py
2025-12-04 17:15:48 | ~/projects/python/maelstrom/lib/nvim/playground.py
2025-12-04 17:16:59 | ~/projects/python/aicmp/request.py
2025-12-04 17:17:25 | ~/projects/python/aicmp/request.py
2025-12-04 17:18:12 | ~/projects/python/aicmp/request.py
"""

print_analysis(analyze_file_saves("/home/kdog3682/data/all_file_saves.log"))
