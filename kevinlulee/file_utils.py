import os
import shutil
import os
import json
import yaml
import toml
from typing import Any
from pathlib import Path
import shutil

from kevinlulee.string_utils import mget


EXT_REFERENCE_MAP = {
  # File type to canonical extension
  "python": "py",
  "javascript": "js",
  "typescript": "ts",
  "html": "html",
  "css": "css",
  "json": "json",
  "xml": "xml",
  "java": "java",
  "c": "c",
  "cpp": "cpp",
  "ruby": "rb",
  "go": "go",
  "php": "php",

  # Canonical extensions mapping to themselves
  "py": "py",
  "js": "js",
  "ts": "ts",
  "html": "html",
  "css": "css",
  "json": "json",
  "xml": "xml",
  "java": "java",
  "c": "c",
  "cpp": "cpp",
  "rb": "rb",
  "go": "go",
  "php": "php",
  "jpg": "jpg",
  "tif": "tif",
  "md": "md",

  # Extension aliases mapping to canonical extensions
  "pyw": "py",
  "jsx": "js",
  "tsx": "ts",
  "htm": "html",
  "jpeg": "jpg",
  "jpe": "jpg",
  "tiff": "tif",
  "mjs": "js",
  "cxx": "cpp",
  "cc": "cpp",
  "c++": "cpp",
  "markdown": "md",
  "mdown": "md",
  "typst": "typ",
  "pdf": "pdf",
  "typ": "typ",

}




def is_extf(extensions):
    def check(el):
        return get_extension(el) in extensions
    return check
def get_extension(file_path: str) -> str:
    """Extracts and formats the file extension from a given file path.
       Files like .env and .vimrc will result in no extension.
       The extension is "". This is intended.

    Args:
        file_path: The path to the file (string).

    Returns:
        The file extension in lowercase without the leading dot (string).
        Returns an empty string if no extension is found.
    """
    if not '.' in file_path:
        return EXT_REFERENCE_MAP[file_path]
    return os.path.splitext(file_path)[1].lstrip(".").lower()


def writefile(filepath: str, data: Any, debug = False) -> str:
    """Writes data to a file, serializing it based on the file extension.
    Creates the directory if it doesn't exist.

    Args:
        filepath: The path to the file to write to. The path must have an extension.
        data: The data to write to the file. Supported types include int, float, str,
              bool, dict, and list. Data will be serialized to YAML, TOML, or JSON
              format based on the file extension.

    Returns:
        The absolute path to the file that was written to.

    Raises:
        ValueError: If the file extension is not supported or data is None.
        TypeError: If the data cannot be serialized to the specified format.
        AssertionError: If the data is None or has no value or if the file path
                        does not have an extension.
    """
    assert data, "Data must be existant. Empty strings or None are not allowed."
    assert os.path.splitext(filepath)[1], f"Filepath must have an extension: {filepath}"


    def serialize(data: Any) -> str:
        if isinstance(data, (int, bool)):
            raise TypeError("Only strings, arrays, dictionaries, customs are allowed.")
        elif isinstance(data, str):
            return data

        elif isinstance(data, (dict, list, tuple)):
            file_extension = get_extension(filepath)
            match file_extension:
                case 'yb':
                    import yb
                    return yb.dumps(data)
                case "yml" | "yaml":
                    return yaml.dumps(data, indent=2)
                case "toml":
                    import toml

                    return toml.dumps(data)
                case "json":
                    return json.dumps(data, indent=2)
                case "txt":
                    return json.dumps(data, indent=2)
                case _:
                    raise ValueError(f"Unsupported file extension: {file_extension}")
        else:
            return str(data)

    expanded_file_path = os.path.expanduser(filepath)
    dir_path = os.path.dirname(expanded_file_path)

    value = serialize(data)
    if debug:
        print('-' * 20)
        print('[DEBUGGING] writefile')
        print(f'[PATH] "{expanded_file_path}"')
        print('[CONTENT]')
        print()
        print(value)
        print('-' * 20)
        print()
    else:
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(expanded_file_path, "w") as file:
            file.write(value)

    return expanded_file_path


def readfile(path: str) -> Any:
    """Reads a file and returns its content.
    Supports JSON, YAML, TOML, and raw text/binary formats.

    Args:
        path: The path to the file.

    Returns:
        The content of the file, deserialized if applicable.
        Returns None if the file does not exist.
    """
    expanded_path = os.path.expanduser(path)

    if not os.path.isfile(expanded_path):
        return None

    extension = get_extension(expanded_path)

    mode = "rb" if extension in ("img", "jpg", "jpeg", "png", "gif", "svg") else "r"
    with open(expanded_path, mode) as f:
        if extension == "json":
            return json.load(f)
        if extension == "yb":
            return yb.load(f)
        elif extension in ("yaml", "yml"):
            p = yaml.safe_load(f)
            if isinstance(p, str):  # wasnt able to parse the input
                return None
            return p
        elif extension == "toml":
            return toml.load(f)
        else:
            return f.read()

import os

def find_project_root(start_path):
    """
    Search upward from start_path for a directory containing .git or any *.egg-info.
    """
    current_dir = os.path.expanduser(start_path)

    count = 0
    while count < 15:
        count += 1
        if os.path.isdir(os.path.join(current_dir, '.git')):
            return current_dir

        entries = os.listdir(current_dir) if os.path.isdir(current_dir) else []
        if any(entry.endswith('.egg-info') for entry in entries):
            return current_dir

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break

        current_dir = parent_dir

    return None

def find_git_directory(path):
    root = os.path.expanduser("~/")
    path = os.path.expanduser(path)

    count = 0
    while count < 10:
        count += 1
        if os.path.exists(os.path.join(path, ".git")):
            return path
        new_path = os.path.dirname(path)
        if new_path in (root, path):
            return 
        path = new_path
    return None

class FileContext:
    def __init__(self, file):
        self.path = os.path.expanduser(file)

    @property
    def size(self):
        return os.path.getsize(self.path)

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def directory(self):
        return os.path.dirname(self.path)

    @property
    def name(self):
        return os.path.splitext(self.filename)[0]

    @property
    def ext(self):
        return os.path.splitext(self.filename)[1].lstrip('.')

    @property
    def content(self):
        return readfile(self.path)

    @property
    def modified_at(self):
        return os.path.getmtime(self.path)

    @property
    def git_directory(self):
        return find_git_directory(self.path)

    @property
    def project_root(self):
        return find_project_root(self.path)
def get_most_recent_file(directory, pattern="*"):
    # Get a list of files in the directory that match the pattern
    import glob
    files = glob.glob(os.path.join(os.path.expanduser(directory), pattern))
    
    if not files:
        return None
    
    most_recent = max(files, key=os.path.getmtime)
    return most_recent

def clip(s):
    file = os.path.expanduser('~/.kdog3682/scratch/clip.txt')
    writefile(file, s)
    import webbrowser
    webbrowser.open(file)


def symlink(source, destination):
    source = os.path.expanduser(source)
    destination = os.path.expanduser(destination)
    assert os.path.exists(source)
    assert not os.path.exists(destination), f"destination '{destination}' already exists"
    os.symlink(source, destination)
    print(f'Symlink created from {source} to {destination}')

def copy_directory_contents(src, dest):
    src = os.path.expanduser(src)
    dest = os.path.expanduser(dest)
    if not os.path.exists(dest):
        os.makedirs(dest)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

        print('copied', s)

def resolve_dotted_path(path, reference):

    reference = os.path.expanduser(reference)
    if os.path.isfile(reference):
        reference = os.path.dirname(reference)

    assert os.path.isdir(reference), "to resolve the dotted path, the reference must be a directory"

    if path.startswith("../"):
        path, m = mget(path, "^(?:../)+")
        upwards = len(m) // 3
        r = "(?<!^)/(?!$)"
        parts = re.split(r, reference)
        parts = parts[:-upwards]
        return os.path.join(*parts, path)

    if path.startswith("./"):
        return os.path.join(reference, path[2:])

    if path.startswith("/") or path.startswith("~"):
        return path

    return os.path.join(reference, path)


def fnamemodify(file, dir = None, name = None, ext = None):

    _dir = os.path.dirname(file)
    _ext = get_extension(file)
    _name = os.path.basename(file)
    if has_extension(name):
        _ext = get_extension(name)
    

    if dir: _dir = dir(_dir) if is_function(dir) else dir
    if ext: _ext = ext(_ext) if is_function(ext) else ext
    if name: _name = name(_name) if is_function(name) else name
    return os.path.join(_dir, f"{_name}.{_ext}")


def cpfile(source, dest, debug=False):
    source = os.path.abspath(os.path.expanduser(source))
    dest = os.path.abspath(os.path.expanduser(dest))
    assert os.path.isfile(source), f"the provided source: {source} is not a file"

    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(source))

    if debug:
        print(f"[cpfile] Would copy:\n  from: {source}\n    to: {dest}")
        return

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(source, dest)


def resolve_filetype(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.typ': 'typst',
        '.css': 'css',
        '.vue': 'vue',
        '.json': 'json',
        '.md': 'markdown',
        '.c': 'c',
        '.cpp': 'cpp',
        '.java': 'java',
        '.sh': 'shell',
        '.rb': 'ruby'
    }.get(ext, 'text')

def comment(text, filepath):
    def hash_comment(t):
        return '\n'.join(f'# {line}' for line in t.splitlines())

    def slash_comment(t):
        return '\n'.join(f'// {line}' for line in t.splitlines())

    def block_comment(t):
        return f'/* {t} */'

    def html_comment(t):
        return f'<!-- {t} -->'

    def markdown_comment(t):
        return f'> {t}'

    comment_styles = {
        'python': hash_comment,
        'shell': hash_comment,
        'ruby': hash_comment,
        'javascript': slash_comment,
        'typescript': slash_comment,
        'typst': slash_comment,
        'vue': slash_comment,
        'java': slash_comment,
        'c': slash_comment,
        'cpp': slash_comment,
        'json': slash_comment,
        'html': html_comment,
        'xml': html_comment,
        'css': block_comment,
        'markdown': markdown_comment
    }

    formatter = comment_styles.get(filetype, hash_comment)
    return formatter(text)


def writefile(filepath: str, data: Any, debug = False, verbose = True) -> str:
    """Writes data to a file, serializing it based on the file extension.
    Creates the directory if it doesn't exist.

    Args:
        filepath: The path to the file to write to. The path must have an extension.
        data: The data to write to the file. Supported types include int, float, str,
              bool, dict, and list. Data will be serialized to YAML, TOML, or JSON
              format based on the file extension.

    Returns:
        The absolute path to the file that was written to.

    Raises:
        ValueError: If the file extension is not supported or data is None.
        TypeError: If the data cannot be serialized to the specified format.
        AssertionError: If the data is None or has no value or if the file path
                        does not have an extension.
    """
    assert data, "Data must be existant. Empty strings or None are not allowed."
    assert os.path.splitext(filepath)[1], f"Filepath must have an extension: {filepath}"


    def serialize(data: Any) -> str:
        if isinstance(data, (int, bool)):
            raise TypeError("Only strings, arrays, dictionaries, customs are allowed.")
        elif isinstance(data, str):
            return data

        elif isinstance(data, (dict, list, tuple)):
            file_extension = get_extension(filepath)
            match file_extension:
                case "yml" | "yaml":
                    return yaml.dump(data, indent=2)
                case "toml":
                    import toml

                    return toml.dumps(data)
                case "json":
                    return json.dumps(data, indent=2)
                case "txt":
                    return json.dumps(data, indent=2)
                case _:
                    raise ValueError(f"Unsupported file extension: {file_extension}")
        else:
            return str(data)

    expanded_file_path = os.path.expanduser(filepath)
    dir_path = os.path.dirname(expanded_file_path)

    value = serialize(data)
    if debug:
        if verbose:
            print('-' * 20)
            print('[DEBUGGING] writefile')
            print(f'[PATH] "{expanded_file_path}"')
            print('[CONTENT]')
            print()
            print(value)
            print('-' * 20)
            print()
        else:
            return comment(expanded_file_path, resolve_filetype(expanded_file_path)) + "\n" + value
    else:
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(expanded_file_path, "w") as file:
            file.write(value)

    return expanded_file_path

def appendfile(path, data, debug = False):
    e = get_extension(path)

    def get(path, data):
        as_array = isinstance(data, (list, tuple))
        prev = readfile(path) or ([] if as_array else {})
        prev.extend(data) if as_array else prev.update(data)
        return prev

    if e == "json":
        payload = get(path, data)
        with open(path, "w") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

    elif e == "yml":
        payload = get(path, data)
        yaml.dump(path, payload)

    else:
        with open(path, "a") as f:
            if e == "yml.txt" and not is_string(data):
                dashes = hr(20) + "\n"
                if is_object(data):
                    data = dashes + myam2(data)

                if not test(data, "^\s*---"):
                    data = dashes + data

            if is_file(path):
                data = "\n" + data

            f.write(data)

class FilepathValidator:
    ignore_dirs = [
        "__pycache__",
        "node_modules",
        ".git",
    ]

    def __init__(self, pattern="."):
        self.regex = re.compile(pattern)

    def directory(self, name):
        if name in self.ignore_dirs or os.path.basename in self.ignore_dirs:
            return
        return True

    def file(self, file):
        if not re.search(self.regex, file):
            return
        return True

def getfiles(dir, pattern=".", recursive=False, sort=False) -> list[str]:
    validate = FilepathValidator(pattern=pattern)
    dir = os.path.expanduser(dir)

    store = []
    for root, dirs, files in os.walk(dir):
        dirs[:] = [dir for dir in dirs if validate.directory(dir)]

        for file in files:
            path = os.path.join(root, file)
            if validate.file(path):
                store.append(path)

        if not recursive:
            return store

    return store


def clear_directory(path):
    dir_path = Path(path).expanduser()
    if not dir_path.is_dir():
        raise ValueError(f"{path} is not a valid directory")

    for item in dir_path.iterdir():
        print('deleting', item.name)
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
 


def is_file(x):
    return x and os.path.isfile(os.path.expanduser(x))

def is_dir(x):
    return x and os.path.isdir(os.path.expanduser(x))
