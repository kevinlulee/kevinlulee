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
from typing import Any, Unpack
from pathlib import Path
import shutil

from kevinlulee.constants import DLDIR
from kevinlulee.introspect import get_caller
from kevinlulee.ao import smallify, partition, xtest
from kevinlulee.base import yes, no
from kevinlulee.resolve_ops import resolve_filetype
from kevinlulee.serialize_ops import serialize_data
import kevinlulee.yb as yb
from kevinlulee.date_utils import strftime, resolve_timedelta
from kevinlulee.string_utils import mget, prefix_join, remove_ending_slash, split, split_once, remove_starting_slash

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




from kevinlulee.consts.file_types import FILETYPE_TO_EXT, EXTENSIONS

def get_extension_from_filetype(lang):
    return EXT_REFERENCE_MAP[lang]
def has_extension(el):
        if not el or not isinstance(el, str):
            return False
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
    dot_files = [
        '.ignore',
        '.bashrc',
        '.vimrc',
        '.vim',
        '.env',
    ]
    bn = os.path.basename(file_path)
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
            try:
                return json.load(f)
            except Exception as e:
                return None
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


def get_most_recently_downloaded_file():
    return get_most_recent_file(DLDIR)

def get_most_recent_file_groups(dir, pattern = '.', minutes=3):
    files = getfiles(dir, pattern)
    files = reverse(sorted(files, key=os.path.getmtime))
    store = []

    last_date = None

    for file in files:
        file_date = os.path.getmtime(file)

        if last_date == None:
            store.append(file)
        else:
            delta = abs(file_date - last_date)
            limit = resolve_timedelta(minutes=minutes)
            if delta < limit:
                store.append(file)
            else:
                break
        last_date = file_date

    return reverse(store)

def get_most_recently_downloaded_files():
    return get_most_recent_file_groups(DLDIR)

def clip(s, ext = 'txt'):
    if not s:
        return 

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


def fnamemodify(file, dir = None, name = None, ext = None):

    _dir = os.path.dirname(file)
    _ext = get_extension(file)
    _name = os.path.basename(file)
    _name = _name[0:-len(_ext) - 1]
    if has_extension(name):
        _ext = get_extension(name)


    if dir: _dir = dir(_dir) if callable(dir) else dir
    if ext: _ext = ext(_ext) if callable(ext) else ext
    if name: _name = name(_name) if callable(name) else remove_starting_slash(name)
    ext_value = '.' + _ext if _ext else ''
    if name and get_extension(name) and ext is None:
        ext_value = ''
    return os.path.join(_dir, f"{_name}{ext_value}")


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
    formatter = comment_styles.get(filetype, hash_comment)
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
    gitignore_path = os.path.join(root_dir, '.gitignore')
    gitignore_content = readfile(gitignore_path)
    if not gitignore_content:
        return no
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

def ensure_directory_exists(path):
    
    path = os.path.expanduser(path)  # Expands ~ to the user's home directory
    
    if get_extension(path):
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


def mvdir(source_path, target_path, root_dir = None):

    # Normalize paths and make them absolute
    source_path = os.path.join(root_dir, os.path.expanduser(source_path))
    target_path = os.path.join(root_dir, os.path.expanduser(target_path))
    source_path = os.path.expanduser(os.path.normpath(source_path))
    target_path = os.path.expanduser(os.path.normpath(target_path))

    # Check if source exists
    if not os.path.exists(source_path):
        print(f"Source path does not exist: {source_path}")
        return False

    try:
        # Create target directory if it doesn't exist
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Move the directory or file
        shutil.move(source_path, target_path)
        print(f"Successfully moved {source_path} to {target_path}")
        return True
    except Exception as e:
        print(f"Error moving directory: {e}")
        return False

def cp(src, dst, recursive=True, preserve_metadata=False, debug=False, verbose=False):
    """
    Copy files or directories, similar to bash 'cp' command.
    
    Args:
        src (str): Source file or directory path
        dst (str): Destination file or directory path
        recursive (bool): If True, copy directories recursively (like cp -r)
        preserve_metadata (bool): If True, preserve file metadata (like cp -p)
        dry_run (bool): If True, only show what would be done without actually copying
        verbose (bool): If True, print operations being performed
    
    Returns:
        None
    
    Raises:
        FileNotFoundError: If source doesn't exist
        IsADirectoryError: If source is directory without recursive=True
        shutil.Error: For other copy-related errors
    """
    # Expand paths (handle ~ and make absolute)
    src = os.path.abspath(os.path.expanduser(src))
    dst = os.path.abspath(os.path.expanduser(dst))
    
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source path '{src}' does not exist")
    
    if os.path.isdir(src):
        if recursive:
            action = "copytree" if not debug else "would copytree"
            copy_func = "copy2" if preserve_metadata else "copy"
            
            if verbose or debug:
                print(f"{action}: '{src}' -> '{dst}' (recursive, {copy_func})")
                
            if not debug:
                try:
                    if preserve_metadata:
                        shutil.copytree(src, dst, copy_function=shutil.copy2)
                    else:
                        shutil.copytree(src, dst)
                except shutil.Error as e:
                    raise shutil.Error(f"Error copying directory {src} to {dst}: {e}")
        else:
            raise IsADirectoryError(f"'{src}' is a directory (not copied). Use recursive=True to copy directories.")
    else:
        action = "copy" if not debug else "would copy"
        copy_func = "copy2" if preserve_metadata else "copy"
        
        if verbose or debug:
            print(f"{action}: '{src}' -> '{dst}' ({copy_func})")
            
        if not debug:
            try:
                if preserve_metadata:
                    shutil.copy2(src, dst)
                else:
                    shutil.copy(src, dst)
            except shutil.Error as e:
                raise shutil.Error(f"Error copying file {src} to {dst}: {e}")


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
    if exists:
        assert is_dir(a), f"the provided path: '{a}' is not a valid directory path."
    else:
        assert not is_dir(a), "the provided path: '{a}' must not exist."




def mvfile(a, b):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    assert_file(a)
    shutil.move(a, b)

def mvdir(a, b):
    a = os.path.expanduser(str(a))
    b = os.path.expanduser(str(b))
    assert_directory(a)
    shutil.move(a, b)

def rmfile(a):
    a = os.path.expanduser(str(a))
    os.unlink(a)
    
