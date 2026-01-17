"""
Extract function definitions from Typst source files.

Parses Typst files to extract function signatures including positional arguments,
named arguments with their types/defaults, and spread parameters.
"""

from __future__ import annotations
from kevinlulee.extras.ts_utils import (
    get_root_node_from_source,
    get_node_text,
    get_language,
)
from tree_sitter import Query


TYPST_FUNCTION_QUERY = """
(
  source_file
  (code
    (let
      pattern: (call
        item: (ident) @name
        (group) @arglist
      )
    ) @block
  )
)
"""


def query_typst(node, query_string: str) -> list[dict]:
    """
    Run a tree-sitter query on a Typst node.

    Args:
        node: The tree-sitter node to query.
        query_string: The tree-sitter query pattern.

    Returns:
        List of dicts mapping capture names to nodes.
    """
    language = get_language("typst")
    ts_query = Query(language, query_string)
    raw = ts_query.captures(node)

    if not raw:
        return []

    keys = list(raw.keys())
    
    # Sort each list by start position so they align correctly
    for k in keys:
        raw[k] = sorted(raw[k], key=lambda n: (n.start_point[0], n.start_point[1]))

    num_matches = len(raw[keys[0]])

    return [{k: raw[k][i] for k in keys} for i in range(num_matches)]


def build_typst_library(source: str, include_text: bool = False) -> list[dict]:
    """
    Extract function definitions from a Typst source file.

    Args:
        source: File path or source code string.
        include_text: If True, include the full function text in results.

    Returns:
        List of dicts with function metadata:
            - name: Function name
            - params: Dict containing:
                - pos: List of positional parameter names
                - named: Dict of named params with type/value info
                - elude: Spread parameter name if present
            - text: Full function text (only if include_text=True)
    """
    root = get_root_node_from_source(source)
    captures = query_typst(root, TYPST_FUNCTION_QUERY)

    results = []
    for capture in captures:
        func_data = _parse_function(capture, include_text)
        results.append(func_data)

    return results


def _parse_function(capture: dict, include_text: bool) -> dict:
    """Parse a single function capture into structured data."""
    name = get_node_text(capture["name"])
    arglist = capture["arglist"]

    pos = []
    named = {}
    elude = None

    for child in arglist.children:
        match child.type:
            case "ident":
                pos.append(get_node_text(child))
            case "tagged":
                children = child.children
                key_node = children[0]
                value_node = children[-1]
                key = get_node_text(key_node)
                named[key] = {
                    "type": value_node.type,
                    "value": get_node_text(value_node),
                }
            case "elude":
                elude = get_node_text(child.children[1])

    result = {
        "name": name,
        "params": {"pos": pos, "named": named, "elude": elude},
    }

    if include_text:
        result["text"] = '#' + get_node_text(capture["block"])

    return result


if __name__ == "__main__":
    from pprint import pprint

    files = [
        "~/projects/typst/typkit/0.3.0/src/components.typ",
        # "~/projects/typst/typkit/0.3.0/src/div.typ",
        # "~/projects/typst/typkit/0.3.0/src/layout.typ",
    ]

    for f in files:
        funcs = build_typst_library(f, include_text=True)
        pprint(funcs)
