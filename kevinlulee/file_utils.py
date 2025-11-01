from __future__ import annotations
import inspect
import os
import webbrowser
import os
import shutil
import re
import os
import shutil
from pathlib import Path
import shutil
import os
import json
import yaml
import toml
from typing import Any, Unpack, TypedDict
from pathlib import Path
import shutil

from kevinlulee.constants import DLDIR
from kevinlulee.introspect import get_caller
from kevinlulee.ao import smallify, partition, xtest
from kevinlulee.base import yes, no
from kevinlulee.resolve_ops import resolve_filetype
from kevinlulee.serialize_ops import serialize_data
from kevinlulee.text_tools import join_text
import kevinlulee.yb as yb
from kevinlulee.date_utils import make_time_window_predicate, strftime, resolve_timedelta, to_seconds
from kevinlulee.string_utils import matchstr, mget, prefix_join, remove_ending_slash, split, split_once, remove_starting_slash

def yb_parse(kwargs):
            assert isinstance(kwargs, dict), "yb data must be in the form of a dict"
            bar = '---'
            pairs = list(kwargs.items())
            if 'date' not in kwargs:
                pairs.insert(0, ('date', strftime()))

            s = bar + "\n" 
            for k,v in pairs:
                s+= f'{k}: {v}\n'
        
            return s


import os
from typing import Any

def looks_like_path(value: Any) -> bool:
    """
    Heuristic: True if the input looks like a filesystem path by checking for:
      - forward/back slashes,
      - a leading '~',
      - a dot in the last segment (e.g., 'file.txt', '.env'),
      - or exactly '.' / '..'.
    """
    if isinstance(value, bytes):
        s = value.decode("utf-8")
    elif isinstance(value, (str, os.PathLike)):
        s = os.fspath(value)
    else:
        return False

    s = s.strip()
    if not s:
        return False

    if s in (".", ".."):
        return True

    if s.startswith("~"):
        return True

    if ("/" in s) or ("\\" in s):
        return True

    # Check for a dot in the last path segment (handles both separators)
    last_seg = s.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return "." in last_seg


from kevinlulee.consts.file_types import FILETYPE_TO_EXT, EXTENSIONS

def get_extension_from_filetype(lang):
    return EXT_REFERENCE_MAP[lang]
def has_extension(el):
        if not el or not isinstance(el, str):
            return False
        return bool(get_extension(el))
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
    dot_files = [
        '.ignore',
        '.bashrc',
        '.vimrc',
        '.vim',
        '.env',
    ]
    file_path = str(file_path)
    bn = os.path.basename(file_path)
    if bn == 'fish_history':
        return 'yml'
        return bn
    if bn in dot_files:
        return bn[1:]
    if not '.' in file_path:
        if file_path.startswith('.'):
            return EXT_REFERENCE_MAP.get(file_path, None)
        return ''
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    return ext if ext in EXTENSIONS else None


def readfile(path: str, raw = False) -> Any:
    """Reads a file and returns its content.
    Supports JSON, YAML, TOML, and raw text/binary formats.

    Args:
        path: The path to the file.

    Returns:
        The content of the file, deserialized if applicable.
        Returns None if the file does not exist.
    """
    path = str(path)
    expanded_path = os.path.expanduser(path)

    if not os.path.isfile(expanded_path):
        return None

    extension = get_extension(expanded_path)

    mode = "rb" if extension in ("img", "jpg", "jpeg", "png", "gif", "svg") else "r"
    with open(expanded_path, mode) as f:
        if raw:
            return f.read()
        if extension == "md":
            return f.read()
        if extension == "json":
            return json.load(f)
        if extension == "yb":
            import yb
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

import os
import glob
from typing import Iterable, Union

def get_most_recent_file(path_or_files: Union[str, os.PathLike, Iterable[Union[str, os.PathLike]]],
                         pattern: str = "*"):
    """
    If given a directory (str or PathLike), returns the most recently modified file
    in that directory matching `pattern`.

    If given an iterable of file paths, returns the most recently modified file
    among those paths. (In this mode, `pattern` is ignored.)

    Returns None if no candidate files are found.
    """
    if isinstance(path_or_files, (str, os.PathLike)):
        directory = os.path.expanduser(os.fspath(path_or_files))
        candidates = [p for p in glob.glob(os.path.join(directory, pattern)) if os.path.isfile(p)]
    else:
        candidates = []
        for p in path_or_files:
            full = os.path.expanduser(os.fspath(p))
            if os.path.isfile(full):
                candidates.append(full)

    if not candidates:
        return None

    return max(candidates, key=os.path.getmtime)


def get_most_recently_downloaded_file():
    return get_most_recent_file(DLDIR)

def get_most_recent_file_groups(dir, pattern = '.', minutes=3):
    files = get_paths(dir, include = pattern)
    files = list(reversed(sorted(files, key=os.path.getmtime)))
    store = []

    last_date = None

    for file in files:
        file_date = os.path.getmtime(file)

        if last_date == None:
            store.append(file)
        else:
            delta = abs(file_date - last_date)
            limit = to_seconds(minutes=minutes)
            if delta < limit:
                store.append(file)
            else:
                break
        last_date = file_date

    return list(reversed(store))

def get_most_recently_downloaded_files():
    return get_most_recent_file_groups(DLDIR)

def clip(s, ext = 'txt'):
    if not s:
        return 

    if isinstance(s, str) and s.startswith('<'):
        ext = 'html'
    file = os.path.expanduser('~/.kdog3682/scratch/clip.' + ext)
    writefile(file, s, ensure_ascii=False)
    webbrowser.open(file)
    return file



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

    assert os.path.isdir(src), "src must be a directory"
    assert not os.path.isfile(src), "dst must not be a file"

    os.makedirs(dest, exist_ok=True)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

        print('copied', s)

def resolve_dotted_path(path, reference):

    path = os.path.expanduser(path)
    if path.startswith("/"):
        return os.path.expanduser(path)

    reference = os.path.expanduser(reference)
    if os.path.isfile(reference):
        reference = os.path.dirname(reference)
    assert os.path.isdir(reference), "to resolve the dotted path, the reference must be a directory"
    return os.path.abspath(os.path.join(reference, path))




def cpfile(source, dest, debug=False, soft = False, mkdir = False, verbose = False):
    dest = os.path.abspath(os.path.expanduser(dest))
    if soft and os.path.exists(dest):
        return 
    
    source = os.path.abspath(os.path.expanduser(source))
    assert os.path.isfile(source), f"the provided source: {source} is not a file"

    if os.path.isdir(dest) or mkdir:
        dest = os.path.join(dest, os.path.basename(source))

    if debug:
        print(f"[DEBUG] Would copy:\n  from: {source}\n    to: {dest}")
        return

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(source, dest)
    if verbose:
        print(f"copy:\n  from: {source}\n    to: {dest}")
    return dest



def comment(text, filepath, as_documentation = False):
    if text is None:
        return ''
    def hash_comment(t):
        return '\n'.join(f'# {line}' for line in t.splitlines())

    def slash_comment(t):
        delim = '///' if as_documentation else '//'
        return '\n'.join(f'{delim} {line}' for line in t.splitlines())

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

    filetype = resolve_filetype(filepath)
    formatter = comment_styles.get(filetype, slash_comment)
    return formatter(text)



def writefile(filepath: str, data: Any, debug = False, verbose = False, strict = True, ensure_ascii = False) -> str:

    if strict: assert data, "Data must be existant. Empty strings or None are not allowed."
    assert get_extension(filepath), f"Filepath must have an extension: {filepath}"

    path = os.path.expanduser(filepath)
    value = serialize_data(data, path, ensure_ascii = ensure_ascii)

    if debug: 
        return debug_print(path, value, debug)

    ensure_directory_exists(path)
    with open(path, "w") as file:
        file.write(value)

    if verbose:
        print('@writefile:', path)

    return path

def appendfile(path, data, debug = False, verbose = False):
    if path.endswith('yml.txt'):
        return yb.append_file(path, data)

    path = os.path.expanduser(path)
    as_append = False
    def getter(path, data):
        as_array = isinstance(data, (list, tuple))
        prev = readfile(path) or ([] if as_array else {})
        prev.extend(data) if as_array else prev.update(data)
        return prev

    def get(path, data):
        nonlocal as_append
        e = get_extension(path)

        if e == "json":
            prev = getter(path, data)
            return json.dumps(prev, indent=2, ensure_ascii=False)

        elif e == "yml":
            import yaml
            prev = getter(path, data)
            return yaml.dumps(prev)

        elif e == 'yb': 
            as_append = True
            prev = getter(path, data)
            return yb_parse(prev)
        else:
            as_append = True
            return "\n"+  data if is_file(path) else data

    cdata = get(path, data)
    if debug: 
        return debug_print(path, cdata, debug)

    ensure_directory_exists(path)

    mode = 'a' if  as_append else 'w'
    with open(path, mode) as f:
        f.write(cdata)

    return path


def find_file_recursively(dir, pattern=".", flags = re.I):
    validate = FilepathValidator(pattern=pattern, flags = flags)
    dir = os.path.expanduser(dir)

    for root, dirs, files in os.walk(dir):
        dirs[:] = [dir for dir in dirs if validate.directory(dir)]

        for file in files:
            path = os.path.join(root, file)
            if validate.file(path):
                return path

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
    return x and isinstance(x, str) and os.path.isfile(os.path.expanduser(x))

def is_dir(x):
    return x and isinstance(x, str) and os.path.isdir(os.path.expanduser(x))

def mkfile(path, debug = False, soft = False):
    path = os.path.expanduser(path)
    if soft and os.path.exists(path):
        return 
    
    if debug:
        return print('[DEBUG]', 'mkfile', path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        pass

def mkdir(path, debug = False, force = True):
    
    if debug:
        return print('[DEBUG]', 'mkdir', path)

    root = Path(path).expanduser()
    if force and root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


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
    gitignore_path = os.path.join(root_dir, '.gitignore')
    gitignore_content = readfile(gitignore_path)
    if not gitignore_content:
        return should_ignore_path
    # Create a spec from gitignore content
    more = ['.git/']
    spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_content.splitlines() + more)
    
    def is_ignored(file_path):
        """
        Check if a file should be ignored according to gitignore rules.
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if the file should be ignored, False otherwise
        """
        if should_ignore_path(file_path):
            return True

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




def datawrite(name, content):
    dir = '~/dotfiles/data'
    path = name if re.match('[~/]', name) else os.path.join(dir, name)
    writefile(path, content)

def unexpand(path):
    home = os.path.expanduser("~/")
    return path.replace(home, "~/")

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

def absdir(dir):
    dir = os.path.expanduser(dir)
    return [os.path.join(dir, path) for path in os.listdir(dir)]

import os

def looks_like_file(path):
    return is_file(path) or get_extension(path) or is_dotfile(path)
import os

def is_dotfile(path: str) -> bool:
    """Check if a given path is a dotfile (hidden file starting with '.')"""
    name = os.path.basename(os.path.expanduser(path))
    return name.startswith(".") and len(name) > 1

def relpath(path, reference):
    ref_path = os.path.expanduser(reference)
    ref_dir = os.path.dirname(ref_path) if looks_like_file(ref_path) else ref_path
    return os.path.relpath(path, ref_dir)
def is_same_path(a, b):
    return os.path.expanduser(a) == os.path.expanduser(b)
def ensure_directory_exists(path):
    
    path = os.path.expanduser(path)  # Expands ~ to the user's home directory
    
    if looks_like_file(path):
        path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def ensure_directory(path):
    path = os.path.expanduser(path)  # Expands ~ to the user's home directory
    
    if os.path.isfile(path):
        path = os.path.dirname(path)
    return path

import os
import shutil
from pathlib import Path

def cp(source_file, destination_directory, name=None):
    source_path = os.path.expanduser(os.path.expandvars(source_file))
    source_path = os.path.abspath(source_path)
    
    dest_dir = os.path.expanduser(os.path.expandvars(destination_directory))
    dest_dir = os.path.abspath(dest_dir)
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Determine the destination filename
    if name is None:
        # Use the original filename if no name is provided
        dest_filename = os.path.basename(source_path)
    else:
        # Use the provided name
        dest_filename = name
    
    # Construct the full destination path
    destination_path = os.path.join(dest_dir, dest_filename)
    
    # Copy the file
    shutil.copy2(source_path, destination_path)
    
    return destination_path

def add_extension_if_not_present(file_name: str, extension: str) -> str:
    
    if not extension or get_extension(file_name):
        return file_name

    return file_name + '.' + extension
skippable_dirs = [
        "__pycache__",
        "node_modules",
        ".git",
    ]
class FilepathValidator:
    ignore_dirs = [
        "__pycache__",
        "node_modules",
        ".git",
    ]

    def __init__(self, pattern=".", flags = 0):
        self.regex = re.compile(pattern, flags=flags)

    def directory(self, name):
        if name in self.ignore_dirs or os.path.basename in self.ignore_dirs:
            return
        return True

    def file(self, file):
        if not re.search(self.regex, file):
            return
        return True
def getfiles(dir, pattern=".", recursive=False, tree=False, sort=False) -> list[str]:
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



class PathValidator:
    def __init__(self, base_pattern=None):
        self.exclusion_rules = []
        self.inclusion_rules = []
        self.distancy_cutoff = 0
        self.recency_cutoff = 0

    def add_rule(self, **kwargs):
     """
     Add validation rules of different types
     """
     for rule_type, rule in kwargs.items():
         match rule_type:
             case "exclude":
                 self.exclusion_rules.append(rule)
             case "include":
                 self.inclusion_rules.append(rule)
             case "recent":
                 self.recency_cutoff = resolve_timedelta(**rule)
             case "distant":
                 self.distancy_cutoff = resolve_timedelta(**rule)

    def add_inclusion_rule(self, **kwargs: Unpack[ValidationRuleSpec]):
        # 2025-05-18 aicmp: implement
        # exts means the file's ext matches. after means the file's os.path.getmtime is after
        for rule_type, rule in kwargs.items():
            match rule_type:
                case "exts":
                    pass
                case "ext":
                    pass
                case "filetype":
                    pass
                case "after":
                     self.recency_cutoff = resolve_timedelta(**rule)
                case "before":
                    pass

    def add_exclusion_rule(self, **kwargs: Unpack[ValidationRuleSpec]):
        stem = kwargs.get('stem')
        if stem:
            self.exclusion_rules.append(lambda x: xtest(Path(x).stem, stem))
        

    def validate(self, filepath):
        """
        Validate a file path against all rules.
        Returns True if the filepath passes all validations.
        """
        for rule in self.exclusion_rules:
            if self.matches_rule(filepath, rule):
                return False

        if self.inclusion_rules:
            includes_match = False
            for rule in self.inclusion_rules:
                if self.matches_rule(filepath, rule):
                    includes_match = True
                    break
            if not includes_match:
                return False

        if self.recency_cutoff and not self.validate_recency(filepath):
            return False

        if self.distancy_cutoff and not self.validate_distancy(filepath):
            return False

        return True

    def matches_rule(self, filepath, rule):
        if callable(rule):
            return rule(filepath)
        if isinstance(rule, list):
            return filepath in rule
        elif isinstance(rule, str):
            return re.search(rule, filepath) is not None
        return False

    def validate_recency(self, filepath):
        mtime = os.path.getmtime(filepath)
        return mtime <= self.recency_cutoff

    def validate_distancy(self, filepath):
        mtime = os.path.getmtime(filepath)
        return mtime >= self.distancy_custoff



def resolve_directory(path):
    if get_extension(path):
        return os.path.dirname(path)
    return path

def remove_extension(file):
    if 'yml.txt' in file:
        return file.replace('.yml.txt', '')
    ext = get_extension(file)
    if not ext:
        return file
    return file.replace('.' + ext, '')

def get_filename(file):
    return remove_extension(os.path.basename(file))

def text_getter(s) -> str:
    return (readfile(s) if is_file(s) else s).strip()


def delete_file(file):
    path = os.path.expanduser(str(file))
    os.unlink(path)
    return path
def is_python_file(path):
    filetype = resolve_filetype(path)
    return filetype == 'python'

def looks_like_directory(path_str):
    """
    Check if a string looks like a directory path.
    
    Returns True if:
    - The path is an existing directory
    - The path has multiple '/' and no file extension
    
    Args:
        path_str (str): The path string to check
        
    Returns:
        bool: True if the string looks like a directory, False otherwise
    """
    # Check if it's an actual existing directory
    path_str = os.path.expanduser(path_str)
    if os.path.isdir(path_str):
        return True

    if get_extension(path_str):
        return False
    
    # Check if it has multiple '/' and no extension
    if path_str.count('/') > 0:
        # Get the last part of the path (potential filename)
        last_part = path_str.split('/')[-1]
        
        # If last part is empty (path ends with /) or has no extension
        if not last_part or '.' not in last_part:
            return True
    
    return False


def liner(m):
        l = len(m)
        l = min(l, 60)
        t = '-' * l
        print(t)
        print(m)
        print()
        print()
        # print(t)
def debug_print(file, content, debug):
    
    mode = get_caller(1).function
    if debug == True:
        print(f'[DEBUG] {mode}: "{file}"')
    else:
        print(content)
        # m = '... content shown above ...'
        # liner(m)
        liner(f'[DEBUG] {mode}: "{file}" (content shown above)')
        
class cd:
    def __init__(self, path=None):
        self.path = os.path.expanduser(path or os.getcwd())

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


from pathlib import Path, PurePosixPath

def has_valid_existing_parent(dst_dir: Path) -> bool:
    """
    Return True if at least one ancestor of dst_dir already exists,
    excluding the user's home directory and the filesystem root.
    """
    home = Path('~/').expanduser()
    dst_dir = Path(dst_dir)
    for anc in dst_dir.parents:  # parent -> ... -> anchor
        if not anc.exists():
            continue
        if anc == home:
            continue  # skip ~/ as requested
        if anc == Path(anc.anchor):
            continue  # skip filesystem root
        return True
    return False



def assert_file(a):
    assert is_file(a), f"the provided path: '{a}' is not a valid file path."
def assert_directory(a, exists = True):
    if isinstance(a, Path):
        if not a.exists():
            raise FileNotFoundError(f"Source directory '{a}' does not exist")
        if not a.is_dir():
            raise NotADirectoryError(f"'{a}' is not a directory")

    if exists:
        assert is_dir(a), f"the provided path: '{a}' is not a valid directory path."
    else:
        assert not is_dir(a), "the provided path: '{a}' must not exist."




def mvfile(a, b, normalize_to_directory = False, verbose = False):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    if normalize_to_directory: b = fnamemodify(b, name = os.path.basename(a))
    assert_file(a)
    ensure_directory_exists(b)
    shutil.move(a, b)
    if verbose: print(f'moved {os.path.basename(a)} to {unexpand(os.path.dirname(b))}')
    # print([a, b])



def cpfile(a, b, normalize_to_directory = False, verbose = False, soft = True, debug = False):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    if normalize_to_directory: b = fnamemodify(b, name = os.path.basename(a))
    assert_file(a)
    if soft and is_file(b):
        return 
    if debug:
        print(f'copied {os.path.basename(a)} to {unexpand(os.path.dirname(b))}')
        return 

    ensure_directory_exists(b)
    shutil.copyfile(a, b)
    if verbose: print(f'copied {os.path.basename(a)} to {unexpand(os.path.dirname(b))}')

def trashfile(a, verbose = False):
    mvfile(a, '~/trash', normalize_to_directory = True, verbose = verbose)
def mvdir(a, b, verbose = False):
    a = remove_ending_slash(os.path.expanduser(str(a)))
    b = remove_ending_slash(os.path.expanduser(str(b)))
    if os.path.basename(b) == os.path.basename(a):
        a = os.path.dirname(a)
    assert_directory(a)
    shutil.move(a, b)
    if verbose:
        print(f'moved {a} to {b}')

def rmfile(a):
    a = os.path.expanduser(str(a))
    os.unlink(a)

def cpdir(a, b, verbose = False):
    a = remove_ending_slash(os.path.expanduser(str(a)))
    b = remove_ending_slash(os.path.expanduser(str(b)))
    ensure_directory_exists(os.path.dirname(b))
    shutil.copytree(a, b) 
    if verbose:
        print(f'copied directory "{a}" to "{b}"')

def rmdir(a):
    a = os.path.expanduser(str(a))
    shutil.rmtree(a, ignore_errors=True)  # like `rm -rf`

def rmpath(a):
    func = rmfile if  is_file(a) else rmdir
    func(a)
        
import os
from typing import Callable, Optional, Union

StrOrFn = Optional[Union[str, Callable[[str], str]]]

def fnamemodify(path: str, dir: StrOrFn = None, name: StrOrFn = None, ext: StrOrFn = None) -> str:
    """
    Rebuild a file path by optionally changing directory, base name, and/or extension.

    Args:
        path: Original file path.
        dir:  New directory (string) or a function that receives the current directory and returns one.
        name: New base name (string) or a function that receives the current base name (no extension) and returns one.
              If a *string* name includes an extension (e.g., 'report.md') and `ext` is None, that extension is used.
        ext:  New extension (with or without leading dot) *or* a function that receives the current extension
              (without leading dot) and returns one. If provided, it overrides any extension found in `name`.

    Returns:
        The modified file path as a string.

    Notes:
        - Hidden files like '.env' are treated as having no extension.
        - If `ext` is an empty string or returns an empty string, the result has no extension.
        - When `ext` is provided, any extension present in `name` (string or callable result) is stripped and replaced.
    """

    def _is_hidden_no_ext(s: str) -> bool:
        # '.env' -> True (no ext), '.gitignore' -> True, 'file.txt' -> False
        return s.startswith('.') and s.count('.') == 1

    def _split_name(s: str) -> tuple[str, str]:
        # Returns (base_without_ext, ext_without_dot); treats '.env' as ('.env','')
        if _is_hidden_no_ext(s):
            return s, ''
        base, suffix = os.path.splitext(s)
        if suffix:
            return base, suffix.lstrip('.')
        return s, ''

    def _strip_ext(s: str) -> str:
        return _split_name(s)[0]

    def _has_ext(s: str) -> bool:
        return _split_name(s)[1] != ''

    def _normalize_ext(e: str) -> str:
        # Accept 'md' or '.md' and return a dot-prefixed extension or '' if empty
        e = e or ''
        e = e.lstrip('.')
        return f'.{e}' if e else ''

    # Current components
    cur_dir  = os.path.dirname(path)
    cur_file = os.path.basename(path)
    cur_base, cur_ext = _split_name(cur_file)        # e.g., ('archive.tar', 'gz') or ('notes', '')
    
    # New directory
    if callable(dir):
        new_dir = dir(cur_dir)
    elif isinstance(dir, str):
        new_dir = dir
    else:
        new_dir = cur_dir

    # Determine new base name
    if callable(name):
        # Callable gets the base *without* extension
        new_name = name(cur_base)
    elif isinstance(name, str):
        # Keep only the last path segment and remove leading separators
        s = os.path.basename(name).lstrip('/\\')
        new_name = s
    else:
        new_name = cur_base

    # Decide final extension
    ext_is_provided = ext is not None

    if ext_is_provided:
        # If ext provided, it overrides everything; also strip any ext that slipped into new_name
        new_name = _strip_ext(new_name)
        if callable(ext):
            new_ext = ext(cur_ext)  # callable receives current extension *without* the dot
        else:
            new_ext = get_extension(ext) if looks_like_path(ext) else ext
        suffix = _normalize_ext(new_ext)
    else:
        # ext not provided: respect extension if new_name (string or callable result) already has one
        if _has_ext(new_name):
            # Use name exactly as given (including its extension)
            suffix = ''  # don't append another extension
        else:
            # Keep the original extension
            suffix = _normalize_ext(cur_ext)

    # If name was a string and included directories, we've already stripped them.
    # Also ensure we don't carry an empty filename.
    if new_name == '':
        # Fall back to current base if the provided name sanitized to empty
        new_name = cur_base

    return os.path.join(new_dir, f"{new_name}{suffix}")

# fnamemodify("/a/b/c.txt")                           # "/a/b/c.txt" (unchanged)
# fnamemodify("/a/b/c.txt", name="report")            # "/a/b/report.txt"
# fnamemodify("/a/b/c.txt", name="report.md")         # "/a/b/report.md" (name's ext respected)
# fnamemodify("/a/b/c.txt", ext="md")                 # "/a/b/c.md"
# fnamemodify("/a/b/c.tar.gz", name=lambda n: n.upper())
# # -> "/a/b/C.TAR.gz" (callable name, original ext kept)
#
# fnamemodify("/a/b/c.txt", name="draft.md", ext="rst")
# # -> "/a/b/draft.rst" (explicit ext overrides name's ext)
#
# print(fnamemodify("/a/b/.env", ext="bak"))
# fnamemodify("/a/b/.env", name=".env.local")         # "/a/b/.env.local"
#

import os
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import TypedDict, Optional


class FileInfo(TypedDict):
    modified_at: datetime
    size: int
    ext: str
    name: str
    path: str
    filetype: Optional[str]


def get_file_info(file_path: str) -> FileInfo:
    """
    Get comprehensive file information.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        FileInfo: TypedDict containing file information
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        OSError: If there's an error accessing the file
    """
    path_obj = Path(file_path)
    
    # Get file stats
    stat = path_obj.stat()
    
    # Get file extension (without the dot)
    ext = path_obj.suffix.lstrip('.')
    
    # Get MIME type
    filetype, _ = mimetypes.guess_type(str(path_obj))
    
    path = str(path_obj.absolute())
    return FileInfo(
        modified_at=stat.st_mtime,
        size=stat.st_size,
        ext=ext,
        name=path_obj.name,
        path=path,
        filetype=resolve_filetype(path)
    )



def is_public_directory(dir):
    name = os.path.basename(dir)
    if name.startswith('.'):
        return False
    return name not in skippable_dirs

# info = get_file_info("/home/kdog3682/projects/python/kevinlulee/kevinlulee/file_utils.py")
import os

import os

import os

import os
import re

def get_paths(
    dir,
    exts=None,
    start=None,
    end=None,
    depth=1,
    collect="files",      # 'files' | 'dirs' | 'both'
    include=None,         # str or compiled re, matched against basename via kx.matchstr
    exclude=None,         # str or compiled re, matched against basename via kx.matchstr
    validators = [],
) -> list[str]:
    base = os.path.expanduser(dir)
    exts = [] if exts is None else exts
    collect = collect.lower()
    want_files = collect in ("files", "both")
    want_dirs  = collect in ("dirs", "both")

    predicate = make_time_window_predicate(start, end)

    def name_allowed(path: str) -> bool:
        if include is not None and not matchstr(path, include):
            return False
        if exclude is not None and matchstr(path, exclude):
            return False
        return True

    store: list[str] = []

    def walk(current_dir: str, level: int) -> None:
        entries = list(os.scandir(current_dir))
        public_children = [e for e in entries if e.is_dir() and is_public_directory(e.name)]

        # Files at this level
        if want_files:
            for e in entries:
                if e.is_file():
                    if exts and get_extension(e.name) not in exts:
                        continue
                    if not name_allowed(e.name):
                        continue

                    if validators and not all(v(e) for v in validators):
                        continue

                    p = e.path
                    s = e.stat().st_mtime

                    if predicate(s):
                        store.append(p)

        # Determine whether current_dir is a LEAF dir (with respect to public dirs and depth limit)
        can_descend = (depth == 0) or (level < depth)
        descend_children = public_children if can_descend else []

        if want_dirs and not descend_children:
            if name_allowed(os.path.basename(remove_ending_slash(current_dir))) and predicate(current_dir):
                store.append(current_dir)

        # Recurse into eligible children
        for child in descend_children:
            walk(child.path, level + 1)

    walk(base, 0)
    return store

get_files = get_paths


# mvfile('/home/kdog3682/projects/python/kevinlulee/kevinlulee/file_utils.py', '/home/kdog3682/scratch/', normalize_to_directory=True)

def is_executable(p: Path) -> bool:
    if not p.is_file() and not p.is_symlink():
        return False
    mode = p.stat().st_mode
    return bool(mode & stat.S_IXUSR or mode & stat.S_IXGRP or mode & stat.S_IXOTH)



def dirs_up_to_root(current_path: str, root_dir: str ) -> list[str]:
    """
    Return all directories from the current file's directory up to (and including) root_dir.
    The list is ordered from nearest directory to the root.
    """
    root = Path(root_dir).expanduser().resolve()
    current = Path(current_path).expanduser().resolve()

    assert root.is_dir(), f"Root does not exist or is not a directory: {root}"
    current_dir = current if current.is_dir() else current.parent
    assert current_dir.is_dir(), f"Current path's directory does not exist: {current_dir}"

    # Ensure current_dir is inside root
    assert current_dir.is_relative_to(root), f"{current_dir} is not under root {root}"

    out: list[str] = []
    here = current_dir
    while True:
        out.append(str(here))
        if here == root:
            break
        here = here.parent
    return out

def drill_into_directory(root):
    def validate(name):
        if re.search("readme", name, flags=re.I):
            return False

        return True

    cur = root
    while True:
        names = [name for name in os.listdir(cur) if validate(name)]
        if len(names) != 1:
            return cur
        candidate = cur / names[0]
        if candidate.is_dir():
            cur = candidate
        else:
            return cur


get_project_directory = find_project_root

def readdir(dir, delimiter = ''):
    files = absdir(dir)
    text = [readfile(file) for file in files]
    return f'\n{delimiter}\n'.join(text)


def resolve_dotted_path2(s, dir):
    if s.startswith("../"):
        path, m = mget(s, "^(?:../)+")
        upwards = len(m) // 3
        parts = dir.split("/")[: -upwards - 1]
        return os.path.join(*parts, path)

    if s.startswith("./"):
        path = s[2:]
        return os.path.join(dir, path)

    return os.path.join(dir, s)

from pathlib import Path
from typing import Union

# Common patterns to ignore
IGNORE_DIRS = {
    'node_modules',
    '.git',
    '.svn',
    '.hg',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    'venv',
    '.venv',
    'env',
    '.env',
    'dist',
    'build',
    '.egg-info',
    'target',  # Rust/Java
    '.next',  # Next.js
    '.nuxt',  # Nuxt.js
    'coverage',
    '.coverage',
    '.idea',  # JetBrains IDEs
    '.vscode',  # VS Code
    '.DS_Store',  # macOS
}

IGNORE_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.dylib',
    '.egg',
    '.log',
    '.swp',
    '.tmp',
    '.bak',
    '.cache',
}


def should_ignore_path(path: Union[str, Path]) -> bool:
    
    path = Path(path)
    
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    
    if path.suffix in IGNORE_EXTENSIONS:
        return True
    
    return False



from pathlib import Path


def find_git_directory(start_path):
    """
    Search upwards from start_path to find a .git directory.
    
    Args:
        start_path: Starting path (file or directory) as string or Path object
        
    Returns:
        Path object pointing to the .git directory if found, None otherwise
    """
    current = Path(start_path).resolve()
    
    # If start_path is a file, start from its parent directory
    if current.is_file():
        current = current.parent
    
    # Search upwards through parent directories
    while True:
        git_dir = current / ".git"
        
        if git_dir.exists() and git_dir.is_dir():
            return current
        
        # Check if we've reached the root directory
        parent = current.parent
        if parent == current:
            return None
        
        current = parent


import os
import re
from pathlib import Path

def find_filenames_in_directory(root: str, pattern: str, flags: int = 0) -> list[str]:
    """
    Recursively return full paths of files under `root` whose filenames match
    the regex `pattern` (via re.search). Directories are skipped.
    """
    raise Exception('todo: certain directories should be ignored.')
    rx = re.compile(pattern, flags)
    base = Path(root).expanduser()
    results: list[str] = []
    for dirpath, _, filenames in os.walk(base, followlinks=False):
        for name in filenames:
            if rx.search(name):
                results.append(os.path.join(dirpath, name))
    results.sort()
    return results

# if __name__ == '__main__':
#     print(find_filenames_in_directory('~/projects/webdev/fs-view/', 'test\.'))

def zipread(src_path, dst_path=None) -> list[str]:
    """
    items will be extracted into the same directory as the src if dst_path
    is not provided

    a list of paths (the extracted files) will be returned
    """
    src_path = os.path.expanduser(src_path)
    dst_path = (
        os.path.expanduser(dst_path) if dst_path else os.path.dirname(src_path)
    )

    assert has_valid_existing_parent(
        dst_path
    ), f"{dst_path} no ancestor in dst_path exists"
    assert_file(src_path)

    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(os.path.join(dst_path, item.filename))

        zf.extractall(dst_path)

        return store

def get_most_common_file_extension(dir, recursive=False):
    current_dir = os.path.expanduser(dir)
    extensions = []
    
    def add(entry):
        _, extension = os.path.splitext(entry.name)
        if extension:  # Only add if there's an extension
            extensions.append(extension.lower())
    
    if recursive:
        for root, dirs, files in os.walk(current_dir):
            with os.scandir(root) as entries:
                for entry in entries:
                    if entry.is_file():
                        add(entry)
    else:
        with os.scandir(current_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    add(entry)
    
    if not extensions:
        return None
    
    from collections import Counter
    extension_counts = Counter(extensions)
    most_common = extension_counts.most_common(1)
    return most_common[0][0][1:] if most_common else None

def zip_view(src_path) -> str:
    src_path = os.path.expanduser(src_path)
    store = []
    import zipfile

    with zipfile.ZipFile(src_path, "r") as zf:
        items = zf.infolist()
        for item in items:
            store.append(item.orig_filename)

        return fancy_file_tree(store)

def get_directory_size(path):
    import subprocess
    result = subprocess.run(
        ['du', '-sb', path],  # -s for summary, -b for bytes
        capture_output=True,
        text=True
    )
    size = int(result.stdout.split()[0])
    return size


def foo():
    file = '/home/kdog3682/.local/share/fish/fish_history'
    print(get_extension(file))


if __name__ == '__main__':
    foo()

# if __name__ == '__main__':
#     print(get_most_recent_file_groups(DLDIR))
