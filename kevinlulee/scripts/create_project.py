
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
from kevinlulee.file_utils import cpfile, fancy_filetree, mkfile, readfile, writefile, mkdir
from kevinlulee.module_utils import get_file_from_modname
from kevinlulee.text_tools import join_text


def process_project_structure(data: dict, debug = False) -> None:
# aicmp: rewrite as class
    project_languages = set()
    root_path = os.path.expanduser(data["path"])
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
        attributes = node.get("attributes", {})
        desc = attributes.get("desc", False)
        if desc:
            descriptions[path] = desc
        children = node.get("children", [])

        force = attributes.get("force", False)
        skip = attributes.get("skip", False)
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

        if skip:
            return

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

        elif node_type == "file":
            copy = source.get('copy')
            if copy:
                cpfile(get_file_from_modname(copy), path, debug = debug, soft = not force)
            else:
                mkfile(path, debug = debug, soft = not force)

    # Process the entire structure
    process_node(data)

    # Setup .gitignore in root if it doesn't exist
    gitignore_path = os.path.join(root_path, ".gitignore")
    cpfile("~/dotfiles/templates/.gitignore", gitignore_path, soft = True, debug=debug)

    # Setup tests directory


# aicmp: modify this spec so that
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
            language_test_dir = os.path.join(tests_dir, language)
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
    if not debug:
        GithubController().create_repo(root_name, root_path)


    # do hotkeys
    update_hotkeys(hotkeys)

def update_hotkeys(hotkeys):
    if not hotkeys:
        return 

    prev = readfile("/home/kdog3682/dotfiles/nvim/lua/kdog3682/config/keymaps/hotpaths.json")
    data = merge_dicts_recursively(prev, hotkeys)

    writefile("/home/kdog3682/dotfiles/nvim/lua/kdog3682/config/keymaps/hotpaths.json", data)

def main(debug = False):
    from kevinlulee.file_utils import readnote
    from traversal.lop import visit_filetree

    filetree = visit_filetree(readnote('filetree'))
    process_project_structure(filetree, debug = debug)


if __name__ == "__main__":
    main(debug = True)
