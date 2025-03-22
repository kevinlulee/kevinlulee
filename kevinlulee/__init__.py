from .file_utils   import readfile, writefile, File, get_most_recent_file, clip
from .string_utils import group, matchstr, mget, get_indent
from .text_tools   import templater, toggle_comment
from .bash         import ripgrep, bash, fdfind
from .git          import GitRepo



def join_text(contents):
    o = ''
    for content in contents:
        s = content.strip()
        if '\n' in s:
            if o.endswith('\n\n'):
                o += f'{s}\n\n'
            else:
                o += f'\n{s}\n\n'
        else:
            o += f'{s}\n'
    return o
