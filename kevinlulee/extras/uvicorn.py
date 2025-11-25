from __future__ import annotations
import kevinlulee as kx


from pathlib import Path
import subprocess
import sys
import os
import signal
from typing import Optional


def run_uvicorn(
    file_path: str,
    app_name: str = "app",
    host: str = "127.0.0.1",
    port: int = 8000,
    kill: bool = False,
    pidfile_name: Optional[str] = ".uvicorn.pid",
) -> subprocess.Popen:
    """
    Start (or kill) a uvicorn process for a Python file.

    - file_path: path to the Python file that exposes an ASGI app (e.g. /path/to/main.py)
    - app_name: attribute name of the ASGI app inside that file (default "app")
    - host, port: server bind
    - kill: if True, attempt to read pidfile and terminate previous process before starting
    - pidfile_name: optional filename for PID file (defaults to <file>.uvicorn.pid)

    Returns the subprocess.Popen object for the started uvicorn.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_path} does not exist")

    cwd = str(path.parent)
    module = path.stem  # myfile.py -> module "myfile"
    target = f"{module}:{app_name}"
    pidfile = Path('~/scratch').expanduser() / pidfile_name

    # If requested, try to kill an existing process recorded in pidfile
    if pidfile.exists():
        if kill:
            try:
                old_pid = int(pidfile.read_text())
                os.kill(old_pid, signal.SIGTERM)
                # give the process a bit to exit; if you want, you can poll here
                pidfile.unlink(missing_ok=True)
                print(f"Killed previous uvicorn process (pid {old_pid})")
            except Exception as e:
                print(f"Could not kill previous process from pidfile: {e}")

        else:
            print("pidfile exists. terminating")

        return

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        target,
        "--reload",
        "--host",
        host,
        "--port",
        str(port),
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.DEVNULL,  # change to None if you want console logs
        stderr=subprocess.STDOUT,
    )

    # Store pid so later runs can kill it
    pidfile.write_text(str(proc.pid))
    print(
        f"Started Uvicorn for {file_path} as {target} on {host}:{port} (pid {proc.pid})"
    )
    return proc


if __name__ == "__main__":
    file_path = "/home/kdog3682/projects/webdev/fs-view/backend/server.py"
    run_uvicorn(file_path, kill=True)

