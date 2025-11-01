import os
import subprocess
import sys
from pathlib import Path

GRAMMARS = [
    # {"lang": "bash",        "url": "https://github.com/tree-sitter/tree-sitter-bash"},
    # {"lang": "c",           "url": "https://github.com/tree-sitter/tree-sitter-c"},
    # {"lang": "cpp",         "url": "https://github.com/tree-sitter/tree-sitter-cpp"},
    # {"lang": "css",         "url": "https://github.com/tree-sitter/tree-sitter-css"},
    # {"lang": "go",          "url": "https://github.com/tree-sitter/tree-sitter-go"},
    # {"lang": "java",        "url": "https://github.com/tree-sitter/tree-sitter-java"},
    # {"lang": "javascript",  "url": "https://github.com/tree-sitter/tree-sitter-javascript"},
    # {"lang": "json",        "url": "https://github.com/tree-sitter/tree-sitter-json"},
    # {"lang": "ruby",        "url": "https://github.com/tree-sitter/tree-sitter-ruby"},
    # {"lang": "rust",        "url": "https://github.com/tree-sitter/tree-sitter-rust"},
    # {"lang": "typescript",  "url": "https://github.com/tree-sitter/tree-sitter-typescript"},
    # {"lang": "markdown",    "url": "https://github.com/tree-sitter-grammars/tree-sitter-markdown"},
    # {"lang": "yaml",        "url": "https://github.com/ikatyang/tree-sitter-yaml"},
    # {"lang": "toml",        "url": "https://github.com/ikatyang/tree-sitter-toml"},
    # {"lang": "dockerfile",  "url": "https://github.com/camdencheek/tree-sitter-dockerfile"},
    # {"lang": "make",        "url": "https://github.com/alemuller/tree-sitter-make"},
    # {"lang": "hcl",         "url": "https://github.com/tree-sitter-grammars/tree-sitter-hcl"},
    # {"lang": "lua",         "url": "https://github.com/tree-sitter-grammars/tree-sitter-lua"},
    {
        "lang": "python",
        "url": "https://github.com/tree-sitter/tree-sitter-python",
    },
    {"lang": "html", "url": "https://github.com/tree-sitter/tree-sitter-html"},
    {
        "lang": "typescript",
        "url": "https://github.com/tree-sitter/tree-sitter-typescript",
    },
]


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result




def install_treesitter_package(language, github_url, work_dir=None):
    """
    Download and install a tree-sitter package from GitHub.

    Args:
        language: Language name (e.g., 'tsx', 'html')
        github_url: GitHub repo URL
        work_dir: Working directory (default: ~/github)
    """
    if work_dir is None:
        work_dir = Path.home() / "github"
    else:
        work_dir = Path(work_dir).expanduser().resolve()

    repo_name = f"tree-sitter-{language}"
    repo_path = work_dir / repo_name

    print(f"\n{'='*60}")
    print(f"Installing tree-sitter-{language}")
    print(f"{'='*60}\n")

    try:
        import importlib

        module = importlib.import_module(f"tree_sitter_{language}")
        print(f"✓ tree-sitter-{language} already installed and working!")
        return True
    except ImportError:
        print(
            f"tree-sitter-{language} not found, proceeding with installation..."
        )

    if not repo_path.exists():
        work_dir.mkdir(parents=True, exist_ok=True)
        print(f"Cloning {github_url}...")
        run_command(f"git clone {github_url} {repo_name}", cwd=work_dir)

    grammar_file = repo_path / "grammar.js"
    package_json_path = repo_path / "package.json"
    src_dir = repo_path / "src"

    # Fix package.json if needed
    if grammar_file.exists() and package_json_path.exists():
        print("Checking package.json...")
        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        # Check if tree-sitter section exists
        if "tree-sitter" not in package_data:
            print("Adding tree-sitter section to package.json...")
            package_data["tree-sitter"] = [
                {"scope": f"source.{language}", "file-types": [language]}
            ]

            with open(package_json_path, "w") as f:
                json.dump(package_data, f, indent=2)

            print("✓ Updated package.json")

    if grammar_file.exists() and not (src_dir / "parser.c").exists():
        print("Generating parser...")
        run_command("tree-sitter generate", cwd=repo_path)

    print("Building...")
    run_command("tree-sitter build", cwd=repo_path)

    print("Installing Python bindings...")
    run_command(
        f"{sys.executable} -m pip install . --break-system-packages",
        cwd=repo_path,
    )

    try:
        import importlib

        module = importlib.import_module(f"tree_sitter_{language}")
        print(f"✓ tree-sitter-{language} installed!")
        return True
    except ImportError:
        print(f"tree-sitter-{language} was unable to be installed")


def main():
    for o in GRAMMARS:
        try:
            install_treesitter_package(o["lang"], o["url"])
        except Exception as e:
            print(f"✗ Failed to install tree-sitter-{o['lang']}: {e}")


if __name__ == '__main__':
    main()
    # typescript doesnt work
