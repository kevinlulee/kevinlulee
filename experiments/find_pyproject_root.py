import os
import sys
import importlib.util
import subprocess
from pathlib import Path


def find_module_info(file_path):
    """
    Find the current working directory and module name of a Python file.
    
    Args:
        file_path (str, optional): Path to the Python file. Defaults to the current file.
    
    Returns:
        tuple: (cwd, module_name, git_root)
            - cwd: The directory containing the Python file
            - module_name: The inferred module name
            - git_root: The root directory of the Git repository (if applicable)
    """
    # Use current file if no file_path provided
    file_path = os.path.abspath(file_path)
    
    # Get the directory containing the file
    cwd = os.path.dirname(file_path)
    
    # Try to find Git root directory
    git_root = None
    try:
        git_root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'], 
            cwd=cwd,
            stderr=subprocess.PIPE,
            universal_newlines=True
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Determine module name based on directory structure
    module_name = None
    
    # Check if we have __init__.py files going up the directory tree
    current_dir = Path(cwd)
    module_parts = []
    
    # Go up the directory tree until we find no __init__.py
    while (current_dir / "__init__.py").exists():
        module_parts.insert(0, current_dir.name)
        parent_dir = current_dir.parent
        
        # Stop if we've reached the git root or filesystem root
        if git_root and str(current_dir) == git_root:
            break
        if str(current_dir) == str(parent_dir):  # We've reached the filesystem root
            break
            
        current_dir = parent_dir
    
    # If we found a valid module structure
    if module_parts:
        module_name = '.'.join(module_parts)
    else:
        # Fall back to using the directory name
        module_name = os.path.basename(cwd)
    
    return cwd, module_name, git_root


if __name__ == "__main__":
    # Example usage
    cwd, module_name, git_root = find_module_info('/home/kdog3682/projects/python/kevinlulee/experiments/find_pyproject_root.py')
    print(f"Current Working Directory: {cwd}")
    print(f"Module Name: {module_name}")
    print(f"Git Root: {git_root}")
    
