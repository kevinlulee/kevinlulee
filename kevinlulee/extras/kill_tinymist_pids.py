from __future__ import annotations
import kevinlulee as kx

# data = """
# tcp LISTEN 0 1024 127.0.0.1:45503 0.0.0.0:* users:(("tinymist",pid=7322,fd=14))
# tcp LISTEN 0 1024 127.0.0.1:44679 0.0.0.0:* users:(("tinymist",pid=10870,fd=14))
# """
# sample data
import re

def extract_pids(netstat_output: str) -> list[int]:
    """
    Parse netstat/ss output and return unique PIDs found.
    """
    pids = set()
    for match in re.findall(r"pid=(\d+)", netstat_output):
        pids.add(int(match))
    return sorted(pids)


import re
import os
import signal
from typing import Iterable


def extract_pids(
    text: str,
    process_name: str | None = None,
) -> list[int]:
    """
    Extract unique PIDs from ss/netstat output.
    Optionally filter by process name.
    """
    pids = set()

    pattern = re.compile(
        r'\("(?P<name>[^"]+)",pid=(?P<pid>\d+),'
    )

    for match in pattern.finditer(text):
        name = match.group("name")
        pid = int(match.group("pid"))

        if process_name is None or name == process_name:
            pids.add(pid)

    return sorted(pids)


def kill_pids(
    pids: Iterable[int],
    *,
    force: bool = False,
    dry_run: bool = True,
):
    """
    Kill PIDs safely.
    - dry_run=True prints what would happen
    - force=True uses SIGKILL instead of SIGTERM
    """
    sig = signal.SIGKILL if force else signal.SIGTERM

    for pid in pids:
        if dry_run:
            print(f"[dry-run] would send {sig.name} to pid {pid}")
        else:
            try:
                os.kill(pid, sig)
                print(f"sent {sig.name} to pid {pid}")
            except ProcessLookupError:
                print(f"pid {pid} no longer exists")
            except PermissionError:
                print(f"no permission to kill pid {pid}")


def kill_tinymist_pids(dry_run = True):
    netstat_output = kx.bash_nvim('ss', '-tulnip')
    kill_pids(extract_pids(netstat_output), dry_run=dry_run)

if __name__ == "__main__":
    kill_tinymist_pids()

# 2025-12-29 aicmp: mmodify so that we can filter by users. default is ['tinymist']
