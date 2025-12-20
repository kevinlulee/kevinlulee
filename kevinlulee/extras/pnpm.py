from __future__ import annotations
import kevinlulee as kx

import subprocess
from pathlib import Path


def run_install(project_dir: str) -> bool:
    project_path = Path(project_dir)
    node_modules = project_path / "node_modules"

    if node_modules.exists():
        print("Dependencies already installed, skipping npm install")
        return True

    print("Running npm install...")

    result = subprocess.run(
        ["pnpm", "install"], cwd=project_path, capture_output=True, text=True
    )

    if result.returncode == 0:
        print("npm install completed successfully")
        return True

    print("npm install failed")
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    return False


import subprocess
from pathlib import Path


def run_build(project_dir: str) -> bool:
    p = Path(project_dir)

    if (p / "pnpm-lock.yaml").exists():
        cmd = ["pnpm", "run", "build"]
    else:
        cmd = ["npm", "run", "build"]

    result = subprocess.run(cmd, cwd=p, capture_output=True, text=True)

    if result.returncode == 0:
        print("Build succeeded")
        print(result.stdout)
        return True

    print("Build failed")
    print(result.stderr)
    return False


if __name__ == '__main__':
    
    dst = "/home/kdog3682/projects/chrome_extensions/simple_react_example/dist/src/options/"

    a = run_install(dst)
    if a:
        run_build(dst)
