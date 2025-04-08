from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, PlainScalarString
from ruamel.yaml.comments import CommentedMap, CommentedSeq
import os

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096  # prevent line wrapping

def normalize_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if '\n' in v:
                    obj[k] = LiteralScalarString(v.rstrip() + '\n')
                else:
                    obj[k] = PlainScalarString(v)
            else:
                normalize_strings(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                if '\n' in v:
                    obj[i] = LiteralScalarString(v.rstrip() + '\n')
                else:
                    obj[i] = PlainScalarString(v)
            else:
                normalize_strings(v)

def deep_merge(a, b):
    if isinstance(a, CommentedMap) and isinstance(b, dict):
        for k, v in b.items():
            if k in a:
                a[k] = deep_merge(a[k], v)
            else:
                a[k] = v
        return a
    elif isinstance(a, CommentedSeq) and isinstance(b, list):
        a.extend(b)
        return a
    elif isinstance(a, dict) and isinstance(b, dict):
        cm = CommentedMap(a)
        for k, v in b.items():
            if k in cm:
                cm[k] = deep_merge(cm[k], v)
            else:
                cm[k] = v
        return cm
    elif isinstance(a, list) and isinstance(b, list):
        return CommentedSeq(a + b)
    else:
        return b  # b overrides a

def appendyaml(file, content):
    data = CommentedMap()
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            data = yaml.load(f) or CommentedMap()

    data = deep_merge(data, content)
    normalize_strings(data)

    with open(file, 'w') as f:
        yaml.dump(data, f)

if __name__ == '__main__':
    appendyaml('/home/kdog3682/scratch/foo.yaml', {'alphalphalphalpha': 11111})

