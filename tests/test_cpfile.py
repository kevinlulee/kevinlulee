import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from kevinlulee import cpfile  # update as needed


def _compare_files(file1, file2):
    assert file1.read_text() == file2.read_text()
    stat1, stat2 = file1.stat(), file2.stat()
    assert stat1.st_size == stat2.st_size
    assert int(stat1.st_mtime) == int(stat2.st_mtime)
    assert oct(stat1.st_mode)[-3:] == oct(stat2.st_mode)[-3:]


def test_cpfile_direct_copy(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text("hello from source")

    bash_copy = tmp_path / "bash.txt"
    py_copy = tmp_path / "py.txt"

    subprocess.run(["cp", str(src), str(bash_copy)], check=True)
    cpfile(str(src), str(py_copy))

    _compare_files(bash_copy, py_copy)


def test_cpfile_directory_copy(tmp_path):
    src = tmp_path / "another.txt"
    src.write_text("copied into directory")

    bash_dir = tmp_path / "bash_dir"
    py_dir = tmp_path / "py_dir"
    bash_dir.mkdir()
    py_dir.mkdir()

    subprocess.run(["cp", str(src), str(bash_dir)], check=True)
    cpfile(str(src), str(py_dir))

    bash_copy = bash_dir / src.name
    py_copy = py_dir / src.name

    _compare_files(bash_copy, py_copy)

