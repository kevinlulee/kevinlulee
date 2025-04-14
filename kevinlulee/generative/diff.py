import difflib

code1 = """
sdfsdf
sdfsdf
sdfsdf
sdfsdf
sdfsdf
"""

code2 = """def add(x, y):
    return x + y
"""

diff = difflib.unified_diff(
    code1.splitlines(),
    code2.splitlines(),
    fromfile='code1.py',
    tofile='code2.py',
    lineterm=''
)

print('\n'.join(diff))

