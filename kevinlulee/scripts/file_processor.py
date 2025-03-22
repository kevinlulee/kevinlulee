import re
import subprocess
import os
import importlib
from typing import List, Dict, Any
from kevinlulee import File, bash, get_most_recent_file


def resolve_handler(handler_str: str):
    parts = handler_str.split(".")
    if len(parts) == 1:
        return globals().get(handler_str)

    module_name = ".".join(parts[:-1])
    function_name = parts[-1]
    module = importlib.import_module(module_name)
    return getattr(module, function_name)



def match_processor(
        file_context: File, processors: Dict[str, Any], vim: Dict[str, str]
) -> Dict[str, Any]:
    sorted_processors = sorted(
        processors.items(), key=lambda x: x[1].get("priority", -1), reverse=True
    )

    for name, processor in sorted_processors:
        match = processor.get("match", {})

        # Match by extension
        if "ext" in match and file_context.ext != match["ext"]:
            continue

        # Match by pattern
        if "pattern" in match:
            pattern = match["pattern"]
            regex_match = re.match(pattern, file_context.file)
            if not regex_match:
                continue
            captures = regex_match.groups()
        else:
            captures = []

        # Match by directory (if provided)
        if "directory" in match and not file_context.directory.endswith(
            match["directory"]
        ):
            continue

        # Match by name (if provided)
        if "name" in match and file_context.name != match["name"]:
            continue

        # Match by filename (if provided)
        if "filename" in match and file_context.filename != match["filename"]:
            continue

        def has_matching_values(dict1, dict2):
            # Iterate through the keys and values in dict1
            if not dict2:
                return False

            for key, value in dict1.items():
                # Check if the key exists in dict2 and if the values match
                if key not in dict2 or dict2[key] != value:
                    return False
            return True

        if 'vim' in match and not has_matching_values(match['vim'], vim):
            continue

        return processor, captures

    return None, None


def process_file(file: str, processors: Dict[str, Any], vim={}, debug=False):
    file_context = File(file)
    processor, captures = match_processor(file_context, processors, vim)
    if not processor:
        print("No matching processor found.")
        return

    handler_name = processor["process"]["handler"]
    handler = resolve_handler(handler_name)
    if not handler:
        print(f"Handler {handler_name} not found.")
        return

    args = []
    kwargs = processor["process"].get("kwargs", {})
    for arg in processor["process"].get("args", []):
        if arg == "$1":
            args.append(file_context.file)
        elif arg.startswith("$"):
            index = int(arg[1:]) - 2
            if index < len(captures):
                args.append(captures[index])
        else:
            args.append(arg)

    if debug:
        print('handler:', handler)
        print('args:', args)
        print('kwargs:', kwargs)
    else:
        return handler(*args, **kwargs)


# Example usage
yaml_config = {
    "processors": {
        "python_test_processor": {
            "priority": 1,
            "match": {"ext": "py", "vim": {'mode': 'test'}},
            "process": {"handler": "tasteful.test", "args": ['$1'], 'kwargs': {'min_result_length': 10}},
        },
        "wheel_processor": {
            "priority": 100,
            "match": {"ext": "whl"},
            "process": {"handler": "bash", "args": ['pip', 'install', "$1", '--break-system-packages']},
        },
        "custom_processor": {
            "match": {
                "pattern": "^.*/important/.*$",
                "directory": "/important",
                "name": "samm",
                "filename": "sammy.py",
            },
            "process": {"handler": "custom_handler", "args": ["$1", "extra_arg"]},
        },
    }
}

# sandir = '/mnt/chromeos/removable/USB Drive/CB1CB2'
# recent_file = get_most_recent_file(sandir)
# print(f"The most recent file is: {recent_file}")
# print(process_file(recent_file, yaml_config["processors"], debug = False))
