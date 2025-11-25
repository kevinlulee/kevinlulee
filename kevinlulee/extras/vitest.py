import os
import kevinlulee as kx
from kevinlulee.extras.line_edit import LineEdit

def format(s):
    ed = LineEdit(s)
    regs = ed.captures(start=r"Here are the accessible roles:", end=r"❯ node_modules/\.pnpm")
    for r in regs:
        r.delete()
    return str(ed)


def vitest(cwd):
    return format(kx.bash_nvim('pnpm', 'run', 'test:once:verbose', cwd=cwd))



if __name__ == '__main__':
    kx.clip(vitest(cwd = '~/projects/webdev/fs-view/frontend'))
