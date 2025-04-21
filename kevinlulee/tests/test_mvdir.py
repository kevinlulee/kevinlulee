import pytest


import os
import shutil
import tempfile
import pytest
from pathlib import Path

from kevinlulee.file_utils import mvdir


@pytest.fixture
def setup_directories():
    # Create temporary source and destination directories
    with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as dest_dir:
        # Create test files in source directory
        source_path = Path(source_dir)
        (source_path / "file1.txt").write_text("This is file 1")
        (source_path / "file2.txt").write_text("This is file 2")
        
        # Create a subdirectory with files
        subdir = source_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile1.txt").write_text("This is subfile 1")
        
        yield source_dir, dest_dir

def test_mvdir_basic(setup_directories):
    source_dir, dest_dir = setup_directories
    
    # Move files
    result = mvdir(dest_dir, source_dir)
    
    # Check if function returned True
    assert result is True
    
    # Check if files were moved correctly
    dest_path = Path(dest_dir)
    assert (dest_path / "file1.txt").exists()
    assert (dest_path / "file2.txt").exists()
    assert (dest_path / "subdir").exists()
    assert (dest_path / "subdir" / "subfile1.txt").exists()
    
    # Check content of files
    assert (dest_path / "file1.txt").read_text() == "This is file 1"
    assert (dest_path / "file2.txt").read_text() == "This is file 2"
    assert (dest_path / "subdir" / "subfile1.txt").read_text() == "This is subfile 1"

def test_mvdir_nonexistent_source():
    with pytest.raises(FileNotFoundError):
        mvdir("/tmp/dest", "/nonexistent/source")

def test_mvdir_with_existing_files(setup_directories):
    source_dir, dest_dir = setup_directories
    
    # Create a file in destination with the same name
    dest_path = Path(dest_dir)
    (dest_path / "file1.txt").write_text("Existing file")
    
    # Move without force
    mvdir(dest_dir, source_dir, force=False)
    
    # The existing file should not be overwritten
    assert (dest_path / "file1.txt").read_text() == "Existing file"
    
    # Move with force
    mvdir(dest_dir, source_dir, force=True)
    
    # The existing file should be overwritten
    assert (dest_path / "file1.txt").read_text() == "This is file 1"

def test_mvdir_nested_structure():
    with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as dest_dir:
        source_path = Path(source_dir)
        
        # Create a complex nested structure
        (source_path / "file1.txt").write_text("Root file")
        
        dir1 = source_path / "dir1"
        dir1.mkdir()
        (dir1 / "file1.1.txt").write_text("Dir1 file")
        
        dir2 = dir1 / "dir2"
        dir2.mkdir()
        (dir2 / "file1.2.1.txt").write_text("Dir2 file")
        
        # Move the files
        mvdir(dest_dir, source_dir)
        
        # Verify
        dest_path = Path(dest_dir)
        assert (dest_path / "file1.txt").exists()
        assert (dest_path / "dir1" / "file1.1.txt").exists()
        assert (dest_path / "dir1" / "dir2" / "file1.2.1.txt").exists()
