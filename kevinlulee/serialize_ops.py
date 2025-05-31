from dataclasses import is_dataclass, asdict
from typing import Any, Dict, Optional
from kevinlulee.resolve_ops import resolve_filetype
import json


def serialize_data(data, filepath = None, indent = 2) -> str:
    if isinstance(data, (int, bool)):
        return str(data)
    elif isinstance(data, str):
        return data


    elif isinstance(data, (dict, list, tuple)):
        file_extension = resolve_filetype(filepath)
        match file_extension:
            case "yml" | "yaml":
                return yaml.dump(data, indent=indent)
            case "toml":
                import toml

                return toml.dumps(data)
            case "json":
                return json.dumps(data, indent=indent)
            case "txt":
                return json.dumps(data, indent=indent)
            case _:
                return json.dumps(data, indent=indent)
    elif is_dataclass(data) and not isinstance(data, type):
        return asdict(data)
    else:
        return str(data)
