from __future__ import annotations
import kevinlulee as kx


import json
import os
import shlex
from pathlib import Path


def parse_env_line(line):
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if "=" not in line:
        return None

    key, value = line.split("=", 1)
    key = key.strip()

    # Handle quotes correctly
    value_parts = shlex.split(value, posix=True)
    if len(value_parts) != 1:
        raise ValueError(f"Invalid value for {key}")

    value = value_parts[0]

    # Expand env vars and ~
    value = os.path.expandvars(value)
    value = os.path.expanduser(value)

    return key, value


def env_to_json(env_path="~/.env", json_path="~/.env.json"):
    env_path = Path(env_path).expanduser()
    json_path = Path(json_path).expanduser()

    data = {}

    with env_path.open() as f:
        for lineno, line in enumerate(f, 1):
            parsed = parse_env_line(line)
            if parsed is None:
                continue

            key, value = parsed
            data[key.upper()] = value

    # Sort keys alphabetically
    sorted_data = dict(sorted(data.items()))

    with json_path.open("w") as f:
        json.dump(sorted_data, f, indent=2)


# if __name__ == "__main__":

import json
import os
from pathlib import Path


def load_env_json(json_path="~/.env.json", overwrite=False):
    """
    Load a JSON file into os.environ.

    - Values are converted to strings (required by os.environ)
    - Nested dicts / lists are JSON-encoded
    - Existing vars are preserved unless overwrite=True
    """
    json_path = Path(json_path).expanduser()

    if not json_path.exists():
        raise FileNotFoundError(json_path)

    with json_path.open() as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    for key, value in data.items():
        key = str(key)

        if not overwrite and key in os.environ:
            print(f"skipped: <{key}> already exists in os.environ")
            continue

        if isinstance(value, (dict, list)):
            raise Exception(f"{value} must be primitive: no lists or dicts")
        else:
            os.environ[key] = str(value)


# load_env_json()
