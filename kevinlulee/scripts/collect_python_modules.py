import importlib.util
import sys

import kevinlulee as kx
from pathlib import Path


def get_module_info(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return {"name": module_name, "found": False}

    print(spec)
    info = {
        "name": module_name,
        "found": True,
        "origin": spec.origin,
        "is_package": spec.submodule_search_locations is not None,
    }

    if spec.origin:
        print(spec.parent)
        if spec.origin == "built-in":
            info["type"] = "built-in"

        elif 'site-packages' in spec.origin:
            info['type'] = "pip"
    else:
        info["type"] = "built-in"

    return info


# Usage
# print(get_module_info('sys'))       # builtin
# kx.pprint(get_module_info("requests"))  # pip (if installed)
# kx.pprint(get_module_info("kevinlulee.ao"))  # pip (if installed)
# kx.pprint(get_module_info("maelstrom.utils"))  # pip (if installed)
# import sys
# print(sys.path)


# import pkg_resources
#
# installed_packages = pkg_resources.working_set
# installed_modules = sorted([pkg.key for pkg in installed_packages])
#
# kx.clip(installed_modules)



import os
import site
import pathlib
import pkg_resources

# site_packages = site.getsitepackages()
# egg_link_files = []
#
# print(site_packages)
# for dir in site_packages:
#     p = pathlib.Path(dir)
#     egg_link_files += [f.stem.lower() for f in p.glob('*.egg-link')]
#
# eggs = set(egg_link_files)
# all_installed = {pkg.key for pkg in pkg_resources.working_set}
# non_editable = sorted(all_installed - eggs)
#
# print(get_module_info('usefulscripts'))        # stdlib
#
# import site
# print(site.getsitepackages())     # Lists global site-packages
# print(site.getusersitepackages()) # Lists user-specific site-packages
#


import os
import sys
import pathlib
import pkg_resources

# Gather all site-packages directories from sys.path
# site_packages_dirs = [p for p in sys.path if 'site-packages' in p]
# egg_links = set()
#
# for dir in site_packages_dirs:
#     p = pathlib.Path(dir)
#     if p.exists():
#         print(p)
#         egg_links.update(f.stem.lower() for f in p.glob('*.egg-link'))
#
# # All installed packages
# # all_installed = {pkg.key for pkg in pkg_resources.working_set}
# # non_editable = sorted(all_installed - egg_links)
#
# print(egg_links)
#

import pkg_resources
import json



# kx.clip(get_installed_packages_json())
# /home/kdog3682/.local/lib/python3.11/site-packages/usefulscripts-0.1.0.dist-info

# kx.clip(sys.builtin_module_names)


from codefmt.python import pythonfmt
def generate_builtins():
    names = get_builtins()
    return pythonfmt.decl('PYTHON_BUILTINS', names)


kx.clip(sorted(list(sys.modules)))


