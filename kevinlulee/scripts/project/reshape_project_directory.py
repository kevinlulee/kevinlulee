"""
first_use: "/home/kdog3682/projects/hammymathclass/
desc: |
    need to reshape the pytypst directory
    this involves a lot of file movements ... and a lot of 

"""

import kevinlulee as kx



template = """

pytypst2.typing
    candidate-replacement-files:
        /home/kdog3682/ajksdhfasjkldfasdf.py
        /home/kdog3682/ajksdhfasjkldfasdf.py
        /home/kdog3682/ajksdhfasjkldfasdf.py
"""



def move(dir):
    files = [
        "manimlib.mobject.mobject",
        "manimlib.typing",
        "manimlib.utils.bezier",
        "manimlib.constants",
        "manimlib.utils.space_ops",
        "manimlib.utils.simple_functions",
        "manimlib.utils.iterables",
    ]

    files = kx.each(files, kx.get_file_from_modname)
    assert all(kx.is_file(file) for file in files)

    for file in files:
        kx.cp(file, dir, debug = True)

move()



DIR = '/home/kdog3682/projects/hammymathclass/'
ROOT = '/home/kdog3682/projects/hammymathclass/python'
kevscript("create_project", TEMPLATE, root = ROOT)
"/home/kdog3682/projects/python/kevinlulee/kevinlulee/scripts/create_project.py"
