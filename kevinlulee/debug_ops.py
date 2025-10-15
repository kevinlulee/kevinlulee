import os
import shutil
import random
from pathlib import Path

from kevinlulee.file_utils import assert_directory


def sample_files(source_dir, num_files=5):
    """
    Randomly copy num_files from source_dir to a new directory named '{source_dir}-sample'.
    
    Args:
        source_dir: Path to the source directory
        num_files: Number of files to sample (default: 5)
    
    Returns:
        Path to the created sample directory
    """

    source_path = Path(source_dir).expanduser()
    assert_directory(source_path)
    
    # Get all files in the directory (non-recursive)
    all_files = [f for f in source_path.iterdir() if f.is_file()]
    
    if not all_files:
        raise ValueError(f"No files found in '{source_dir}'")
    
    # Sample files (or all if fewer than num_files)
    files_to_copy = random.sample(all_files, min(num_files, len(all_files)))
    
    # Create sample directory
    sample_dir = source_path.parent / f"{source_path.name}-sample"
    sample_dir.mkdir(exist_ok=True)
    
    # Copy files
    for file_path in files_to_copy:
        dest_path = sample_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        print(f"Copied: {file_path.name}")
    
    print(f"\nSampled {len(files_to_copy)} files to: {sample_dir}")
    return sample_dir



import os
from pathlib import Path


def generate_python_files(output_dir="~/scratch/sample_python_dir", num_files=3):
    """Generate a directory of small Python files."""
    
    # Create output directory
    dst = Path(output_dir).expanduser()
    dst.mkdir(exist_ok=True, parents = True)
    
    # Generate files
    for i in range(1, num_files + 1):
        filename = f"script_{i:03d}.py"
        filepath = dst / filename
        
        content = f'''
def main():
    print(f"Running script {i}")
    result = {i} * 2
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
'''
        filepath.write_text(content)
        print(f"Created: {filepath}")
    
    print(f"\nDone! Created {num_files} files in '{output_dir}/'")


if __name__ == "__main__":
    generate_python_files()
