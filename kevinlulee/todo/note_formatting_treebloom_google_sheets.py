
'''
"/home/kdog3682/projects/hammymathclass/typst/adapter.typ"
"/home/kdog3682/projects/hammymathclass/python/manimdoc/examples/gridpen.py"
"/home/kdog3682/projects/hammymathclass/python/manimdoc/adapter.py"
---

'''
from __future__ import annotations
from pprint import pprint
from kevinlulee import *
import kevinlulee as kx

import re

def parse_from_doc_string():
    import nvim
    import vim
    from treebloom import TreeBloom

    text = nvim.state.buffer.text
    filetype = nvim.state.buffer.filetype
    bloom = TreeBloom(text, filetype)
    # bloom = TreeBloom(nvim.state.file)
    m = bloom.query(bloom.root, '''
        (module
          (expression_statement
            (string
             (string_content) @value
            )))
    ''')
    value = m[0]['value']

    # lua.
    # from nvim.buffer import
    items = dash_split(value.text)
    main = items[-1]
    paths = extract_file_paths(main)
    pprint(main)
# def quick_register_file(file):
# parse_from_doc_string()



def my_toml(s):
    r = '^\[(\S+?)\]'
    items = split(s, r, flags = re.M)
    return dict(partition(items))


# vim.funcs.chdir('~/projects/hammymathclass/materials/')
# print(os.listdir())
# if __name__ == '__main__':
#     print(fancy_filetree('~/projects/hammymathclass/'))
from nvim.buffers import Buffers


# Buffers()
from nvim.utils.buffer_ops import get_today_buffers

nvim.fs.clip(get_today_buffers(Buffers()))
