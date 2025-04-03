import os
from kevinlulee.string_utils import mget
import json
import yaml
import toml
from typing import Any

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


def writefile(filepath: str, data: Any) -> str:
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
    assert os.path.splitext(filepath)[1], "Filepath must have an extension."


    def serialize(data: Any) -> str:
        if isinstance(data, (int, bool)):
            raise TypeError("Only strings, arrays, and dictionaries are allowed.")
        if isinstance(data, str):
            return data

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

    expanded_file_path = os.path.expanduser(filepath)

    # Create the directory if it doesn't exist
    dir_path = os.path.dirname(expanded_file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    value = serialize(data)
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
        elif extension in ("yaml", "yml"):
            p = yaml.safe_load(f)
            if isinstance(p, str):  # wasnt able to parse the input
                return None
            return p
        elif extension == "toml":
            return toml.load(f)
        else:
            return f.read()


def find_git_directory(path):
    root = os.path.expanduser("~/")
    assert root in path, f'{path} does not contain "{root}"'

    while path != root:
        if os.path.exists(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
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
        return get_extension(self.path)

    @property
    def content(self):
        return readfile(self.path)

    @property
    def modified_at(self):
        return os.path.getmtime(self.path)

    @property
    def git_directory(self):
        return find_git_directory(self.path)

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
    import shutil
    import os
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


