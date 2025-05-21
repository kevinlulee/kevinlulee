
import textwrap



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
from kevinlulee.text_tools import join_text
import kevinlulee as kx

def append_python_path(path):
    template = f'set -x PYTHONPATH {path} $PYTHONPATH'
    kx.appendfile("/home/kdog3682/dotfiles/links/fish/config.fish", template)

def is_python(path):
    filetype = resolve_filetype(path)
    return filetype == 'python'
def process_project_structure(data: dict, debug = False) -> None:
# aicmp: rewrite as class
# aicmp: rewrite the mkfile and all that stuff to use fs = FileSystem(debug = debug) ... makes it a lot easier to read
    project_languages = set()
    frontmatter = data['frontmatter']
    tree = data['tree']
    root_path = os.path.expanduser(tree["path"])
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
    gitignore_path = os.path.join(root_path, ".gitignore")
    cpfile("~/dotfiles/templates/.gitignore", gitignore_path, soft = True, debug=debug)
    python_path = frontmatter.get('python_path')
    if python_path:
        append_python_path(root_path)

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
    readme_content = ''
    readme_content += fancy_filetree(root_path)
    readme_content += "\n\n"
    for k,v in descriptions.items():
        readme_content += k
        readme_content += "\n"
        readme_content += join_text(textwrap.wrap(v, width=50))
        readme_content += "\n\n"

    writefile(p, readme_content, debug = debug)
    # Create GitHub repository
    if hotkeys:
        print('skipping hotkeys', hotkeys)
        # prev = readfile("/home/kdog3682/dotfiles/nvim/lua/kdog3682/config/keymaps/hotpaths.json")
        # data = merge_dicts_recursively(prev, hotkeys)
        #
        # writefile("/home/kdog3682/dotfiles/nvim/lua/kdog3682/config/keymaps/hotpaths.json", data, debug = debug)

    if not debug:
        GithubController().create_repo(root_name, root_path)



def main(text, debug = False):
    from traversal.lop import visit_filetree

    s = kx.trimdent(text or readnote('filetree'))
    filetree = visit_filetree(s)
    process_project_structure(filetree, debug = debug)


def create_project(text = None):
        main(text, debug = True)

        try:
            import nvim
            if nvim.confirm('proceed with creation'):
                print('starting creation')
                main(text, debug = False)
        except Exception as e:
            pass

def init_manimlib(name):
    root_path = '~/projects/python/' + name
    from kevinlulee.git import GitRepo
    gitignore_path = os.path.join(root_path, ".gitignore")
    cpfile("~/dotfiles/templates/.gitignore", gitignore_path, soft = True)

    repo = GitRepo(root_path)
    # repo.cmd('init')
    # repo.cmd('add', '.')
    print(repo.create_branch('main'))
    # message = 'fork of 3b1b/manim'
    repo.commit("first")


s = """
abc: 1
asdfasdf: 2

hamburger
    boomba
"""
if __name__ == "__main__":
    create_project(s)


