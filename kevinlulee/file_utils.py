import os
import re
import os
import shutil
from pathlib import Path
import shutil
import os
import json
import yaml
import toml
from typing import Any
from pathlib import Path
import shutil

from kevinlulee.ao import smallify, partition
from kevinlulee.string_utils import mget, split, split_once


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



extensions = list(set(EXT_REFERENCE_MAP.values()))


def has_extension(el):
        return get_extension(el) in extensions
def is_extf(extensions):
    def check(el):
        return has_extension(el)
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
        print('[DEBUG] writefile')
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
        if os.path.basename(parent_dir) == 'python':
            return current_dir
        
        if parent_dir == current_dir:
            print('b')
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


import os
import shutil

def symlink(source, destination, force = False):
    """
    Creates a symbolic link from source to destination.

    Args:
        source (str): The path to the source file or directory.
        destination (str): The path where the symbolic link should be created.
        force (bool, optional): If True, remove the destination path if it
                                already exists before creating the symlink.
                                Defaults to False.

    Raises:
        AssertionError: If source does not exist.
        AssertionError: If destination exists and force is False.
        OSError: If there is an issue removing the existing destination
                 or creating the symbolic link.
    """
    source = os.path.expanduser(source)
    destination = os.path.expanduser(destination)

    # Ensure the source path exists
    if not os.path.lexists(source): # Use lexists to handle source being a symlink itself
        raise AssertionError(f"Source path '{source}' does not exist.")

    if force:
        # If destination exists, remove it first
        if os.path.lexists(destination): # Use lexists to check without following links
            try:
                if os.path.islink(destination):
                    os.unlink(destination)
                    print(f"Removed existing symlink: '{destination}'")
                elif os.path.isdir(destination):
                    shutil.rmtree(destination)
                    print(f"Removed existing directory: '{destination}'")
                else:
                    os.remove(destination)
                    print(f"Removed existing file: '{destination}'")
            except OSError as e:
                print(f"Error removing existing destination '{destination}': {e}")
                raise # Re-raise the exception after printing
    else:
        # If not forcing, assert that the destination does not exist
        if os.path.lexists(destination):
             raise AssertionError(f"Destination path '{destination}' already exists. Use force=True to overwrite.")

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


def cpfile(source, dest, debug=False, soft = False):
    dest = os.path.abspath(os.path.expanduser(dest))
    if soft and os.path.exists(dest):
        return 
    
    source = os.path.abspath(os.path.expanduser(source))
    assert os.path.isfile(source), f"the provided source: {source} is not a file"

    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(source))

    if debug:
        print(f"[DEBUG] Would copy:\n  from: {source}\n    to: {dest}")
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
        return print(f'[DEBUG] writefile "{expanded_file_path}"')
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
    path = os.path.expanduser(path)
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


def mvdir(destination, source, force=False):
    """
    Move directory contents from source to destination.
    
    Args:
        destination (str): Path to destination directory
        source (str): Path to source directory
        force (bool, optional): If True, overwrite existing files at destination. Defaults to False.
    
    Returns:
        bool: True if operation was successful, False otherwise
    """
    dest_path = Path(destination)
    src_path = Path(source)
    
    # Check if source exists
    if not src_path.exists() or not src_path.is_dir():
        raise FileNotFoundError(f"Source directory '{source}' does not exist or is not a directory")
    
    # Create destination if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Move files from source to destination
    for item in src_path.glob('*'):
        dest_item = dest_path / item.name
        
        if dest_item.exists() and not force:
            print(dest_item, 'exists ... skipping')
            continue
        
        if item.is_file():
            shutil.copy2(item, dest_item)
        elif item.is_dir():
            if dest_item.exists() and dest_item.is_dir():
                mvdir(str(dest_item), str(item), force)
            else:
                shutil.copytree(item, dest_item, dirs_exist_ok=force)
    
    return True


def readnote(*queries):
    s = readfile('/home/kdog3682/documents/notes/notes.txt')
    r = '^\d\d\d\d-\d\d-\d\d'
    base = split(s, r, flags = re.M)
    # aggregate it up
    if queries:
        store = []
        for item in reversed(base):
            a, b = split_once(item, '\n')
            if a in queries:
                store.append(b)
                if len(store) == len(queries):
                    return smallify(store)
    else:
        return base[-1]


def mkfile(path, debug = False, soft = False):
    path = os.path.expanduser(path)
    if soft and os.path.exists(path):
        return 
    
    if debug:
        return print('[DEBUG]', 'mkfile', path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        pass

def mkdir(path, debug = False):
    
    if debug:
        return print('[DEBUG]', 'mkdir', path)
    os.makedirs(os.path.expanduser(path), exist_ok=True)


import os
import pathspec

def create_gitignore_matcher(rootdir):
    """
    Create a function that checks if a file should be ignored based on gitignore rules.
    
    Args:
        gitignore_path (str): Path to the .gitignore file
        
    Returns:
        function: A function that takes a file path and returns True if it should be ignored
    """
    # Define root directory
    root_dir = os.path.expanduser(rootdir)
    
    # Read gitignore file
    try:
        with open(os.path.join(root_dir, '.gitignore'), 'r') as f:
            gitignore_content = f.read()
    except FileNotFoundError:
        print(f"Warning: {gitignore_path} not found. No files will be ignored.")
        # Return a function that ignores nothing if gitignore doesn't exist
        return lambda path: False
    
    # Create a spec from gitignore content
    spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_content.splitlines())
    
    def is_ignored(file_path):
        """
        Check if a file should be ignored according to gitignore rules.
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if the file should be ignored, False otherwise
        """
        # Make path relative to root directory
        if os.path.isabs(file_path):
            # If path is absolute, make it relative to root_dir
            try:
                rel_path = os.path.relpath(file_path, root_dir)
            except ValueError:
                # If file is on a different drive (Windows), it's outside our project
                return False
        else:
            # If path is already relative, use it directly
            rel_path = file_path
            
        # Normalize path separators to forward slashes as git expects
        rel_path = rel_path.replace(os.path.sep, '/')
        
        # Check if the file matches any ignore pattern
        return spec.match_file(rel_path)
    
    return is_ignored

def fancy_filetree(root_dir):
    """
    Generates a string representation of the file tree for a given directory,
    expanding the directory path using os.path.expanduser().

    Args:
        root_dir (str): The path to the root directory (will be expanded).

    Returns:
        str: A string representing the fancy file tree. Returns an error message
             if the provided path is not a valid directory after expansion.
    """
    # Expand the root directory path
    expanded_root = os.path.expanduser(root_dir)
    
    # Check if the expanded path is a valid directory
    if not os.path.isdir(expanded_root):
        return ''
    
    # Initialize the result string with the root directory
    result = os.path.basename(expanded_root) + "/\n"
    ignore = create_gitignore_matcher(expanded_root)
    
    # Recursively build the tree
    def build_tree(directory, prefix=""):
        entries = sorted(os.listdir(directory))
        count = len(entries)
        
        tree_str = ""
        for i, entry in enumerate(entries):
            full_path = os.path.join(directory, entry)
            if ignore(full_path):
                continue
            is_last = i == count - 1
            
            # Select the appropriate connector
            connector = "└── " if is_last else "├── "
            
            # Determine if entry is a directory
            if os.path.isdir(full_path):
                tree_str += f"{prefix}{connector}{entry}/\n"
                # Determine the new prefix for the next level
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree_str += build_tree(full_path, next_prefix)
            else:
                tree_str += f"{prefix}{connector}{entry}\n"
        
        return tree_str
    
    # Start building the tree from the root
    result += build_tree(expanded_root)
    return result



def datawrite(name, content):
    dir = '~/dotfiles/data'
    path = name if re.match('[~/]', name) else os.path.join(dir, name)
    writefile(path, content)

def unexpand(path):
    home = os.path.expanduser("~/")
    return path.replace(home, "")

def find_parent_path(input_path, callback):
    """
    Traverses up the directory tree from input_path until callback returns a Path or home directory is reached.

    Args:
        input_path: Starting path as string or Path
        callback: Function that takes a Path and returns either a Path object or None

    Returns:
        Path object returned by callback or None if traversal ends without a match
    """

    path = Path(input_path).expanduser()
    home = Path.home()
    count = 0
    max_iterations = 10

    if path.is_file():
        path = path.parent

    while path != home and count < max_iterations:
        result = callback(path)
        if isinstance(result, Path):
            return result

        if result == True:
            return path

        if result == False:
            return
        # Move up to parent directory
        parent = path.parent
        if parent == path:  # Reached root directory
            break
        path = parent
        count += 1

    return None


if __name__ == '__main__':
    print('hi from file_utils.py')
