from __future__ import annotations
import kevinlulee as kx


import subprocess
import json
import re
from typing import Any, Optional

def curl(url: str, data: Optional[Any] = None) -> Any:
    """
    Perform a curl request (GET if data is None, POST if data provided),
    parse stdout as JSON and return the resulting Python object.

    Raises:
      RuntimeError: if curl exits non-zero.
      ValueError: if stdout cannot be parsed as JSON.
    """
    # build command; -sS silences progress but still shows errors on stderr
    if data is None:
        cmd = ["curl", "-sS", url]
    else:
        if isinstance(data, (dict, list)):
            body = json.dumps(data)
            cmd = ["curl", "-sS", "-X", "POST", "-H", "Content-Type: application/json", "--data", body, url]
        else:
            cmd = ["curl", "-sS", "-X", "POST", "--data", str(data), url]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        stderr = result.stderr.strip() or "<no stderr>"
        raise RuntimeError(f"curl failed with exit code {result.returncode}: {stderr}")

    stdout = result.stdout.strip()

    return json.loads(stdout)

# Example call (POST with JSON body)
if __name__ == "__main__":
    resp = curl("http://127.0.0.1:8000/echo/helloasdasd")
    print(resp)

