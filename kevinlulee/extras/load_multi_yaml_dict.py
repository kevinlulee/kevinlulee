from typing import Any, Dict, Union
import yaml
import kevinlulee as kx


_KEY_CANDIDATES = ("id", "uid", "key")


def load_multi_yaml_dict(
    source: Union[str, Any],
) -> Dict[Any, dict]:
    """
    Load a multi-document YAML and index documents by a sniffed key field.

    Rules:
    - Top-level YAML documents must be dicts
    - The key field is sniffed from the first document only (id → uid → key)
    - All documents must contain that field
    - Keys must be unique
    """

    # Load YAML documents
    # if isinstance(source, str) and "\n" not in source:
    #     with open(source, "r", encoding="utf-8") as f:
    #         docs = yaml.safe_load_all(f)
    # else:
    #     docs = yaml.safe_load_all(source)

    docs = yaml.safe_load_all(kx.readfile(source, raw = True))

    result: Dict[Any, dict] = {}

    chosen_field: str | None = None

    for idx, doc in enumerate(docs, start=1):
        if not isinstance(doc, dict):
            raise TypeError(
                f"YAML document #{idx} must be a mapping, "
                f"got {type(doc).__name__}"
            )

        # Sniff key field from first document only
        if chosen_field is None:
            for candidate in _KEY_CANDIDATES:
                if candidate in doc:
                    chosen_field = candidate
                    break
            if chosen_field is None:
                raise KeyError(
                    f"First document must contain one of {_KEY_CANDIDATES}"
                )

        if chosen_field not in doc:
            raise KeyError(
                f"Missing '{chosen_field}' in YAML document #{idx}"
            )

        key = doc[chosen_field]

        if key in result:
            raise KeyError(f"Duplicate key '{key}'")

        result[key] = doc

    return result



# path = "/home/kdog3682/projects/hammymathclass/workbook/long_division/frames.manim.yml"
# print(load_multi_yaml_dict(path))
