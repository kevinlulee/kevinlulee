import os
def resolve_filetype(filepath):
    if not filepath:
        return 
    ext = os.path.splitext(filepath)[1].lower()
    return {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.typ': 'typst',
        '.css': 'css',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.typ': 'typst',
        '.txt': 'text',
        '.log': 'log',
        '.vue': 'vue',
        '.json': 'json',
        '.md': 'markdown',
        '.c': 'c',
        '.cpp': 'cpp',
        '.java': 'java',
        '.sh': 'shell',
        '.zip': 'zip',
        '.rb': 'ruby'
    }.get(ext, 'text')
