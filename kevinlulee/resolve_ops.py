import os
filetypes = [
    "python",
    "javascript",
    "typescript",
    "html",
    "typst",
    "css",
    "yaml",
    "yaml",
    "text",
    "log",
    "vue",
    "json",
    "markdown",
    "c",
    "cpp",
    "java",
    "shell",
    "zip",
    "ruby"
]
def resolve_filetype(x):
    if not x:
        return 
    if x in filetypes:
        return x 

    ext = os.path.splitext(x)[1].lower()
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




