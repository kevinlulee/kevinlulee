import os
import kevinlulee as kx
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Union, Dict, Any


def parse_date_range(date_range_str: str) -> tuple:
    """Parse date range string like 'from 1 year ago to 5 weeks ago'"""
    if not date_range_str:
        return None, None
    
    parts = date_range_str.lower().split(' to ')
    
    def parse_relative_date(date_str: str) -> datetime:
        date_str = date_str.strip().replace('from ', '')
        match = re.match(r'(\d+)\s+(year|month|week|day)s?\s+ago', date_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            now = datetime.now()
            
            if unit == 'year':
                return now - timedelta(days=365 * amount)
            elif unit == 'month':
                return now - timedelta(days=30 * amount)
            elif unit == 'week':
                return now - timedelta(weeks=amount)
            elif unit == 'day':
                return now - timedelta(days=amount)
        return None
    
    start_date = parse_relative_date(parts[0]) if len(parts) > 0 else None
    end_date = parse_relative_date(parts[1]) if len(parts) > 1 else None
    
    return start_date, end_date


def check_size(path: Path, size_config: Dict) -> bool:
    """Check if file size meets criteria"""
    if not size_config:
        return True
    
    try:
        file_size = path.stat().st_size
        
        if 'greater_than' in size_config:
            if file_size <= size_config['greater_than']:
                return False
        
        if 'less_than' in size_config:
            if file_size >= size_config['less_than']:
                return False
        
        return True
    except:
        return False


def check_date_range(path: Path, date_range_str: str) -> bool:
    """Check if file modification date is within range"""
    if not date_range_str:
        return True
    
    start_date, end_date = parse_date_range(date_range_str)
    if not start_date and not end_date:
        return True
    
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        
        if start_date and mtime < start_date:
            return False
        if end_date and mtime > end_date:
            return False
        
        return True
    except:
        return False


def check_path_patterns(path: Path, patterns: List[str]) -> bool:
    """Check if path matches any pattern"""
    if not patterns:
        return False
    
    path_str = str(path)
    for pattern in patterns:
        if re.search(pattern, path_str):
            return True
    return False


def check_path_segments(path: Path, segments: List[str]) -> bool:
    """Check if path contains any segment"""
    if not segments:
        return False
    
    path_str = str(path)
    for segment in segments:
        if segment in path_str:
            return True
    return False


def evaluate_basename_criteria(path: Path, basename_config: Dict) -> Dict[str, bool]:
    """
    Evaluate all basename criteria and return individual results.
    Returns a dict with each criterion type and whether it matched.
    """
    basename = path.name
    ext = path.suffix.lstrip('.')
    
    results = {}
    
    # Extensions
    if 'extensions' in basename_config:
        results['extensions'] = ext.lower() in [e.lower() for e in basename_config['extensions']]
    
    # Keywords
    if 'keywords' in basename_config:
        results['keywords'] = any(kw.lower() in basename.lower() for kw in basename_config['keywords'])
    
    # Patterns (plural)
    if 'patterns' in basename_config:
        results['patterns'] = any(re.search(pat, basename) for pat in basename_config['patterns'])
    
    # Pattern (singular)
    if 'pattern' in basename_config:
        results['pattern'] = bool(re.search(basename_config['pattern'], basename))
    
    # Exact
    if 'exact' in basename_config:
        results['exact'] = basename in basename_config['exact']
    
    return results


def check_basename_include(path: Path, basename_config: Dict) -> bool:
    """
    Check if basename passes include rules (ANY criterion must match).
    Returns True if any criterion matches, False otherwise.
    """
    if not basename_config:
        return True
    
    results = evaluate_basename_criteria(path, basename_config)
    
    if not results:
        return True
    
    # Any criterion matching is sufficient
    return any(results.values())


def check_basename_includes(path: Path, basename_config: Dict) -> bool:
    """
    Check if basename passes includes rules (ALL criteria must match).
    Returns True only if all criteria match, False otherwise.
    """
    if not basename_config:
        return False
    
    results = evaluate_basename_criteria(path, basename_config)
    
    if not results:
        return False
    
    # All criteria must match
    return all(results.values())


def check_basename_exclude(path: Path, basename_config: Dict) -> bool:
    """
    Check if basename should be excluded (ANY criterion matches).
    Returns True if any criterion matches (should exclude), False otherwise.
    """
    if not basename_config:
        return False
    
    results = evaluate_basename_criteria(path, basename_config)
    
    if not results:
        return False
    
    # Any criterion matching means exclude
    return any(results.values())


def check_basename_excludes(path: Path, basename_config: Dict) -> bool:
    """
    Check if basename should be excluded (ALL criteria must match).
    Returns True only if all criteria match (should exclude), False otherwise.
    """
    if not basename_config:
        return False
    
    results = evaluate_basename_criteria(path, basename_config)
    
    if not results:
        return False
    
    # All criteria must match to exclude
    return all(results.values())


def should_collect(path: Path, config: Dict) -> bool:
    """Determine if path should be collected based on config"""
    
    # Check collection type
    collection_type = config.get('collection_type', 'files')
    if collection_type == 'dirs' and not path.is_dir():
        return False
    # if collection_type == 'files' and not path.is_file():
    #     return False
    
    # Size check
    if 'size' in config:
        if not check_size(path, config['size']):
            return False
    
    # Date range check
    if 'date_range' in config:
        if not check_date_range(path, config['date_range']):
            return False
    
    # Path excludes (early return on any match)
    if 'path' in config:
        path_config = config['path']
        
        # Exclude patterns (any match = exclude)
        if 'exclude' in path_config:
            exclude_config = path_config['exclude']
            
            if 'patterns' in exclude_config:
                if check_path_patterns(path, exclude_config['patterns']):
                    return False
            
            if 'segments' in exclude_config:
                if check_path_segments(path, exclude_config['segments']):
                    return False
        
        # Include patterns (must match at least one)
        if 'include' in path_config:
            include_config = path_config['include']
            has_include_rules = bool(include_config)
            
            if has_include_rules:
                passed = False
                
                if 'patterns' in include_config:
                    if check_path_patterns(path, include_config['patterns']):
                        passed = True
                
                if not passed:
                    return False
    
    # Basename excludes (plural - all must match to exclude)
    if 'basename' in config and 'excludes' in config['basename']:
        if check_basename_excludes(path, config['basename']['excludes']):
            return False
    
    # Basename exclude (singular - any match = exclude)
    if 'basename' in config and 'exclude' in config['basename']:
        if check_basename_exclude(path, config['basename']['exclude']):
            return False
    
    # Basename includes (plural - all must match to include)
    if 'basename' in config and 'includes' in config['basename']:
        if not check_basename_includes(path, config['basename']['includes']):
            return False
    
    # Basename include (singular - any match = include)
    if 'basename' in config and 'include' in config['basename']:
        if not check_basename_include(path, config['basename']['include']):
            return False
    
    return True


def path_filter(source: Union[str, List[str]], config: Dict) -> List[str]:
    """
    Collect paths from a directory or list of paths based on config.
    
    Args:
        source: Either a directory path string or a list of path strings
        config: Configuration dict with filtering rules
    
    Returns:
        List of expanded path strings that match the criteria
    """
    recursive = config.get('recursive', False)
    
    # Determine if source is a directory or list of paths
    if isinstance(source, str):
        source_path = Path(source).expanduser().resolve()
        if not source_path.exists():
            return []
        
        # Collect paths from directory
        if source_path.is_dir():
            if recursive:
                all_paths = [Path(root) / file for root, _, files in os.walk(source_path) for file in files]
                all_paths.extend([Path(root) / d for root, dirs, _ in os.walk(source_path) for d in dirs])
            else:
                all_paths = list(source_path.iterdir())
        else:
            all_paths = [source_path]
    else:
        # Source is a list of paths
        all_paths = [Path(p).expanduser().resolve() for p in source]
    
    # Filter paths based on config
    collected = []
    for path in all_paths:
        if should_collect(path, config):
            collected.append(str(path))
    
    return collected
s = """

config:
    recursive: false
    collection_type: files
    size: 
        greater_than: 5

    date_range: from 1 year ago to 5 weeks ago

    basename:
        exclude:
            pattern:
                yeye|luli

        include:
            extensions:
                png svg html deb py jsx tsx jpeg jpg
            keywords:
                claude
                chatgpt
            patterns:
                \s\(\d+\)\.[a-z]+$
"""

def fn(x, k):
    if k.endswith('s') or k == 'exact':
        if isinstance(x, str) and ' ' in x:
            return kx.split(x)
    return x

# config = kx.walk(kx.yamload(s), fn)


# files = path_filter(['~/yeye.js'], config)
# print(files)
