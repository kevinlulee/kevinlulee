from __future__ import annotations
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path


class BinaryInstaller:
    def __init__(self, temp_dir="~/scratch/temp"):
        self.temp_dir = Path(temp_dir).expanduser()
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def install(
        self,
        name: str,
        url: str | None = None,
        repo: str | None = None,
        asset: str | None = None,
        install_dir="/usr/local/bin",
    ):
        if shutil.which(name):
            print(f"{name} already installed, skipping.")
            return

        if url is None:
            if repo is None or asset is None:
                raise ValueError("Must provide either url or both repo and asset")
            url = f"https://github.com/{repo}/releases/latest/download/{asset}"

        temp_path = self.temp_dir / name
        install_path = Path(install_dir) / name

        print(f"Downloading {name}...")
        urllib.request.urlretrieve(url, temp_path)

        print("Verifying file type...")
        result = subprocess.run(
            ["file", str(temp_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        if "ELF" not in result.stdout:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError("Downloaded file is not a Linux executable")

        print("Making executable...")
        os.chmod(temp_path, 0o755)

        print(f"Installing to {install_path} ...")
        subprocess.run(
            ["sudo", "mv", str(temp_path), str(install_path)],
            check=True,
        )

        print("Verifying installation ...")
        subprocess.run([name, "--version"], check=True)

        print(f"{name} installed successfully 🎉")


if __name__ == '__main__':
    installer = BinaryInstaller()
    installer.install("websocat", repo="vi/websocat", asset="websocat.x86_64-unknown-linux-musl")
