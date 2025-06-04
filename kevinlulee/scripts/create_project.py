import textwrap
import pytext



import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
from github_api import GithubController
from pprint import pprint

from kevinlulee.ao import merge_dicts_recursively
from kevinlulee.base import stop
from kevinlulee.file_utils import cpfile, fancy_filetree, mkfile, readfile, resolve_filetype, writefile, mkdir
from kevinlulee.module_utils import get_file_from_modname
from kevinlulee.string_utils import matchstr
from kevinlulee.text_tools import join_text
import kevinlulee as kx



from traversal.lop import Visitor, visit, accumulate_text



class FileTreeVisitor(Visitor):
    def __init__(self, normalize=False, as_project = True, snake_case = False, root_directory = None):
        self.normalize = normalize
        self.as_project = as_project
        self.snake_case = snake_case
        self.root_directory = root_directory
        self.cwd = []

    def get_attribute_key(self, node):
        s = node.text.strip()
        m = matchstr(s, "^([\w-]+):$")
        return m

    def get_attribute(self, node):
        s = node.text.strip()
        m = matchstr(s, "^([\w-]+): +(.+)")
        return m or (None, None)

    def visit_root(self, node):
        if len(node.children) == 1:
            return {
                'tree': self.visit_branch(node.first_child),
                'frontmatter': {}
            }

        frontmatter = {}
        stop_index = 0
        for i, el in enumerate(node.children):
            if el.is_leaf():
                m = self.visit_attr(el)
                if m:
                    frontmatter.update(m)
                else:
                    stop_index = i
                    break
            else:
                stop_index = i
                break

        tree = self.visit_branch(node.children[i])
        return {
            'frontmatter': frontmatter,
            'tree': tree
        }
    def visit_branch(self, node):
        text = node.text.strip()
        name = text
        is_file = kx.has_extension(name)
        if node.uid == 1:
            if self.root_directory:
                name = os.path.join(self.root_directory, name)
            elif self.as_project and 'projects' not in name:
                name = '~/projects/' + name

        m = self.get_attribute_key(node)

        children = node.children or []
        props = {}
        other_children = []

        desc_key = 'desc'
        multiliners = ['desc']

        if m:
            multiline = m in multiliners
            if multiline:
                desc = str(accumulate_text(children))
                props.update({m: desc})
            else:
                m = snake_case(m) if self.snake_case else m
                props.update({m: merge(self.visit_each(children))})
            return props

        elif is_file:
            # a file
            self.cwd.append(name)

            for i, child in enumerate(children):
                val = self.visit(child)
                if isinstance(val, dict) and 'path' not in val:
                    props.update(val)
                else:
                    remaining = children[i:]
                    props.update({desc_key: str(accumulate_text(remaining))})
                    break
        else:
            # a directory
            self.cwd.append(name)
            for child in children:
                val = self.visit(child)
                if isinstance(val, dict) and 'path' not in val:
                    props.update(val)
                else:
                    other_children.append(child)

        entry_type = 'file' if is_file else 'dir'
        entry = self._make_entry(name, entry_type, props)

        # if not is_file:
        # child_entries = [self.visit(child) for child in other_children if child.text and child.text.strip()]
        entry['children'] = kx.filtered(self.visit_each(other_children))

        self.cwd.pop()
        return entry

    def visit_attr(self, node):
        s = node.text.strip()
        m = matchstr(s, "^([\w-]+): +(.+)")
        if m:
            return {m[0]: m[1]}

    def visit_leaf(self, node):
        m = self.visit_attr(node)
        if m:
            return m

        s = node.text.strip()
        name = s
        is_file = kx.has_extension(name)
        return self._make_entry(name, 'file' if is_file else 'dir', {})


    def _make_entry(self, name, kind, attributes):
        extra = [name] if kind == 'file' else []
        if self.normalize:
            walker = kx.coerce_argument
            # if attributes: print(walk(attributes, walker))
            return {
                'path': '/'.join(self.cwd + extra),
                'type': kind,
                'attributes': kx.walk(attributes, walker),
            }
        else:
            return {name: attributes or None}

    def visit(self, node):
        if isinstance(node, (tuple, list)):
            return self.visit_each(node)
        elif node.uid == 0:
            return self.visit_root(node)
        elif node.children:
            return self.visit_branch(node)
        else:
            return self.visit_leaf(node)



# nvim.fs.clip(visit(readnote(query = 'filetree'), FileTreeVisitor, normalize = True))
s = """
            canvas
                pen.py
                    the drawing pen
                element
                    canvas_element.py
                        every canvas element has a frame
                        which represents its bounding box
                        the base element which others inherit from
"""
s = """
asdf: 1
    
foo

    hotkey: c

    canvas.py
    typing.py
    constants.py
    repr.py

    cobject
        cobject.py
        geometry.py
"""
def visit_filetree(s, **kwargs):
  return visit(s, FileTreeVisitor, normalize = True, snake_case = True, **kwargs)
# print(readnote('simple rice'))

# prettyprint(visit_filetree(s))

def append_python_path(path):
    template = f'set -x PYTHONPATH {path} $PYTHONPATH'
    kx.appendfile("/home/kdog3682/dotfiles/links/fish/config.fish", template)

def is_python(path):
    filetype = resolve_filetype(path)
    return filetype == 'python'

def process_project_structure(data: dict, debug = False, create_repo = False, do_hotkeys = False, do_tests = False, root = False) -> None:
# aicmp: rewrite as class
# aicmp: rewrite the mkfile and all that stuff to use fs = FileSystem(debug = debug) ... makes it a lot easier to read
    project_languages = set()
    frontmatter = data['frontmatter']
    tree = data['tree']
    root_path = tree["path"]
    root = root or frontmatter.get('root')
    if root:
        root_path = os.path.join(root, root_path)
    root_path = os.path.expanduser(root_path)
    root_name = os.path.basename(root_path)

    descriptions = {}
    hotkeys = {
        'files': {}, 'directories': {}
    }

    known_languages = [
        "python",
        "typst",
        "typescript",
    ]

    def process_node(node: Dict[str, Any]) -> None:
        path = os.path.expanduser(node["path"])
        name = os.path.basename(path)
        node_type = node.get('type')
        level = node.get('level')
        attributes = node.get("attributes", {})
        force = attributes.get("force", False)
        skip = attributes.get("skip", False)

        if skip:
            return

        desc = attributes.get("desc", False)
        if desc:
            descriptions[path] = desc
        children = node.get("children", [])

        blueprint = attributes.get("blueprint", False)
        hotkey = attributes.get("hotkey", False)
        if hotkey:
            if node_type == 'dir':
                hotkeys["directories"][hotkey] = path
            else:
                hotkeys["files"][hotkey] = path

        if blueprint:
            blueprint_path = os.path.join(root_path, 'blueprints', name + ".md")
            mkfile(blueprint_path, debug=debug)

        source = attributes.get("source", {})

        # Check for language
        dirname = os.path.basename(path)
        if dirname in known_languages:
            project_languages.add(dirname)

        # Check for tests directory
        if dirname == "tests":
            raise ValueError("Tests directory will be auto-generated")

        # Process based on node type
        if node_type == "dir":
            for child in children:
                process_node(child)

            files = [child for child in children if child['type'] == 'file']
            if len(files) > 0 and all(is_python(child['path']) for child in files):
                print(path)
                mkfile(os.path.join(path, '__init__.py'), debug = debug)


        elif node_type == "file":
            copy = source.get('copy')
            if copy:
                cpfile(get_file_from_modname(copy), path, debug = debug, soft = not force)
            else:
                mkfile(path, debug = debug, soft = not force)


    # Process the entire structure
    process_node(tree)

    # Setup .gitignore in root if it doesn't exist
    project_root = kx.find_git_directory(root_path)
    if not project_root:
        gitignore_path = os.path.join(root_path, ".gitignore")
        p = kx.find_git_directory(root_path)
        cpfile("~/dotfiles/templates/.gitignore", gitignore_path, soft = True, debug=debug)
        python_path = frontmatter.get('python_path')
        if python_path:
            append_python_path(root_path)

        if do_tests:
            lang_spec = {
                'python': {
                    'templates': [
                        "~/dotfiles/templates/pytest.ini"
                    ]
                }
            }
            tests_dir = os.path.join(root_path, "tests")
            if not os.path.exists(tests_dir):
                mkdir(tests_dir, debug = debug)

                # Create language-specific test directories
                for language in project_languages:
                    spec = lang_spec.get(language)
                    if not spec:
                        continue

                    language_test_dir = os.path.join(tests_dir, language) if len(project_languages) > 1 else tests_dir
                    mkdir(language_test_dir, debug = debug)
                        
                    templates = spec.get('templates')
                    for template_path in templates:
                        cpfile(template_path, root_path, debug = debug)


    # make the readme file
    p = os.path.join(root_path, "README.md")
    filetree = fancy_filetree(files)
    sb = pytext.StringBuilder()
    sb.add_text(filetree)
    for k,v in descriptions.items():
        sb.add_text(f'**{k}**')
        sb.add_text(v)

    writefile(p, readme_content, debug = debug)

    # Create GitHub repository
    if do_hotkeys and hotkeys:
        bookmarker = kx.run_module_func('nvim.plugins.v1.file_marks.Bookmarks')

        for hotkey in hotkeys:
            if self.debug:
                print(hotkey)
            else:
                bookmarker.bookmark_file(hotkey.keys, hotkey.path)

    if create_repo and not debug:
        GithubController().create_repo(root_name, root_path)



def create_project(text, debug = False, root = None):
    s = kx.remove_commented_lines(kx.trimdent(text or readnote('filetree')))
    filetree = visit_filetree(s, root_directory = root)
    return process_project_structure(filetree, debug = debug)


def confirmation_wrapper():
        main(text, debug = True)

        try:
            import nvim
            if nvim.confirm('proceed with creation'):
                print('starting creation')
                main(text, debug = False)
        except Exception as e:
            pass


"""
the frontmatter needs to be fixed.
currently, it doesnt work because by having the frontmatter present, the node.ids are messedf up. this means the root isnt recognized.
hamburger, seen below, should be node.id 1 not 3.


match the files.
this requires seeing all of the files
that were directly created

and then perhaps fuzzy finding for the best options
this will use fuzzywuzzy.

one step at a time
enjoy the process

forgive yourself
and move forward


handle the source too.

pushing each other into bad places.

forgive ...


"""

s = """
abc: 1
asdfasdf: 2

hamburger
    boomba.py
"""

s = """

hamburger
    boomba.py
"""
if __name__ == "__main__":
    ROOT = '/home/kdog3682/projects/hammymathclass/python'
    create_project(s, debug = True, root = ROOT)
    # process_project_structure()


"""
this function is a little bit too big.
please rewrite it as a class

additionally, please track every file by appending the file path to a files list.
at the
"""

