import os
import kevinlulee as kx
import re
from pathlib import Path



def get_filtered_files(directory, size_limit=50, delete_duplicates=True):
    """
    Get files from a directory that either:
    1. Have a number in parentheses (e.g., foo (1).MD)
    2. Are smaller than the specified size limit (default: 50 bytes)
    
    If a numbered file exists and its original (without number) exists with the same size,
    the numbered file is deleted.
    
    Args:
        directory: Path to the directory to search
        size_limit: Maximum file size in bytes (default: 50)
        delete_duplicates: If True, delete numbered files when original exists with same size
    
    Returns:
        dict with three lists: 'numbered_files', 'small_files', and 'deleted_files'
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Pattern to match files with numbers in parentheses
    # Matches: foo (1).txt, bar (123).md, etc.
    pattern = re.compile(r'^(.+?)\s*\((\d+)\)(.*)$')
    
    numbered_files = []
    small_files = []
    deleted_files = []
    
    # First pass: collect all files
    for item in directory.iterdir():
        if item.is_file():
            # Check if filename matches pattern
            match = pattern.match(item.name)
            if match:
                numbered_files.append(item)
            
            # Check file size
            if item.stat().st_size < size_limit:
                small_files.append(item)
    
    # Second pass: process numbered files to check for duplicates
    if numbered_files and delete_duplicates:
        files_to_keep = []
        for numbered_file in numbered_files:
            match = pattern.match(numbered_file.name)
            if match:
                # Reconstruct original filename
                prefix = match.group(1).rstrip()
                suffix = match.group(3)
                original_name = prefix + suffix
                original_path = numbered_file.parent / original_name
                
                # Check if original exists and has same size
                should_delete = False
                if original_path.exists() and original_path.is_file():
                    if original_path.stat().st_size == numbered_file.stat().st_size:
                        should_delete = True
                
                if should_delete:
                    try:
                        numbered_file.unlink()
                        deleted_files.append(numbered_file.name)
                    except Exception as e:
                        print(f"Could not delete {numbered_file.name}: {e}")
                        files_to_keep.append(numbered_file)
                else:
                    files_to_keep.append(numbered_file)
            else:
                files_to_keep.append(numbered_file)
        
        numbered_files = files_to_keep
    
    return {
        'numbered_files': sorted(numbered_files),
        'small_files': sorted(small_files),
        'deleted_files': deleted_files
    }


def cleanup(target_dir):

    results = get_filtered_files(target_dir, size_limit=50)
    
    if results['deleted_files']:
        print("Deleted duplicate numbered files:")
        for name in results['deleted_files']:
            print(f"  {name}")
        print()
    
    if results['numbered_files']:
        print("Remaining files with numbers in parentheses:")
        for f in results['numbered_files']:
            print(f"  {f.name} ({f.stat().st_size} bytes)")
        print()
    
    if results['small_files']:
        print(f"Files smaller than 50 bytes:")
        for f in results['small_files']:
            print(f"  {f.name} ({f.stat().st_size} bytes)")


    kx.pretty_print(delete_files_by_extension(target_dir))


def delete_files_by_extension(target_dir, exts = ['py', 'js', 'ts', 'tsx', 'deb']):
    paths = kx.get_paths(target_dir, exts=exts, depth = 1)
    # return kx.pretty_print(paths)
    # return 
    for path in paths:
        kx.os.unlink(path)

    return paths


if __name__ == '__main__':
    print(delete_files_by_extension(kx.DLDIR, exts = ['py']))
