import yaml
from collections import defaultdict
from typing import Any
import keyword

def pascal_case(name: str) -> str:
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))

def sanitize_field_name(name: str) -> str:
    return f"{name}_" if keyword.iskeyword(name) else name

def infer_literal_list(lst):
    if all(isinstance(x, (str, int, float, bool)) for x in lst):
        literals = ', '.join(repr(x) for x in lst)
        return f"List[Literal[{literals}]]"
    return None

def infer_type(value: Any, class_defs: dict, class_name: str) -> str:
    if isinstance(value, dict):
        nested_class_name = f"{class_name}{pascal_case('')}"
        nested_class = generate_class(value, nested_class_name, class_defs)
        return f"Union[str, {nested_class}]"
    elif isinstance(value, list):
        if not value:
            return "List[Any]"
        lit_type = infer_literal_list(value)
        if lit_type:
            return lit_type
        inner_type = infer_type(value[0], class_defs, class_name)
        return f"List[{inner_type}]"
    elif isinstance(value, (str, int, float, bool)):
        return f"Literal[{repr(value)}]"
    elif value is None:
        return "Optional[Any]"
    else:
        return "Any"

def generate_class(obj: dict, class_name: str, class_defs: dict) -> str:
    fields = []
    for key, value in obj.items():
        field_name = sanitize_field_name(key)
        field_type = infer_type(value, class_defs, class_name + pascal_case(field_name))
        if value is None:
            field_type = f"Optional[{field_type}]"
        fields.append((field_name, field_type))

    class_body = f"@dataclass\nclass {class_name}:\n"
    for name, typ in fields:
        class_body += f"    {name}: {typ}\n"
    class_defs[class_name] = class_body
    return class_name

def generate_dataclasses(data: dict, root_class_name="Config") -> str:
    class_defs = {}
    generate_class(data, root_class_name, class_defs)

    imports = (
        "from dataclasses import dataclass\n"
        "from typing import List, Optional, Any, Union\n"
        "from typing import Literal\n\n"
    )
    return imports + "\n\n".join(class_defs[class_name] for class_name in list(class_defs.keys()))


# File handling
from kevinlulee import readfile, writefile

s = readfile('~/.env.yml')
generated_code = generate_dataclasses(s)
# print(generated_code)
writefile('/home/kdog3682/projects/python/kevinlulee/kevinlulee/configurable/base_model.py', generated_code)

