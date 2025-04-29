from kevinlulee import writefile, typst
import os

from kevinlulee.date_utils import strftime




s = f'''

#set text(size: 3em)
hi there #rect([{strftime(mode = 'usa')}])


'''

s = f'''

#set text(size: 3em)
hi there #rect([{strftime(mode = 'usa')}])


'''

def quick_typst_file(s, compilepath = '~/scratch/tempfile.typ', pdf = False):
    outpath = '~/projects/typst/mathbook/pymathbook/server/static/tempfile.'
    outpath += 'pdf' if pdf == True else 'svg'

    writefile(compilepath, s)
    typst(compilepath, outpath)
    

