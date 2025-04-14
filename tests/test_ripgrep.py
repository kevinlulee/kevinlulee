import pytest
from kevinlulee.ripgrep import parse_ripgrep_line, ripgrep


def create_files(base, files: dict):
    for rel_path, content in files.items():
        full_path = base / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)


def test_ripgrep_with_fake_files(tmp_path):
    create_files(
        tmp_path,
        {
            "test1.py": "def hello():\n    pass\n",
            "test2.py": "def world():\n    print('world')\n",
            "note.txt": "just a note\n",
        },
    )

    results = ripgrep(pattern="def", dirs=[str(tmp_path)])
    assert len(results) == 2
    assert all("def" in r["excerpt"] for r in results)


def test_ripgrep_respects_ignore_file(tmp_path):
    create_files(
        tmp_path,
        {
            ".ignore": "*.py\n",
            "script.py": "def ignored(): pass\n",
            "readme.md": "def shown(): pass\n",
        },
    )

    results = ripgrep(
        pattern="def",
        dirs=[str(tmp_path)],
        ignore_file=str(tmp_path / ".ignore"),
    )
    assert all(not r["path"].endswith(".py") for r in results)


def test_ripgrep_hidden_files(tmp_path):
    create_files(
        tmp_path,
        {
            ".hidden.py": "def hidden(): pass\n",
            "visible.py": "def visible(): pass\n",
        },
    )

    results_no_hidden = ripgrep(pattern="def", dirs=[str(tmp_path)])
    paths_no_hidden = [r["path"] for r in results_no_hidden]

    results_with_hidden = ripgrep(
        pattern="def", dirs=[str(tmp_path)], hidden=True
    )
    paths_with_hidden = [r["path"] for r in results_with_hidden]

    assert any(".hidden.py" in p for p in paths_with_hidden)
    assert all(".hidden.py" not in p for p in paths_no_hidden)

def test_ripgrep_exts(tmp_path):
    create_files(
        tmp_path,
        {
            ".hidden.py": "def hidden(): pass\n",
            "visible.pyl": "def visible(): pass\n",
        },
    )

    results = ripgrep(pattern="def", dirs=[str(tmp_path)], exts = ['pyl'])
    assert len(results) == 1
