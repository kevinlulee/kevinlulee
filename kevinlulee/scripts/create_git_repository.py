import os

def write_git_ignore(directory):
    gitignore_path = os.path.join(os.path.expanduser(directory), '.gitignore')
    if os.path.exists(gitignore_path):
        return

    huge_gitignore = """\
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*egg-info/
env/
venv/
ENV/
env.bak/
venv.bak/

# OS Generated Files
.DS_Store
Thumbs.db
ehthumbs.db
Desktop.ini

# Logs and temporary files
*.log
*.tmp
*.swp
"""
    with open(gitignore_path, 'w') as f:
        f.write(huge_gitignore)

