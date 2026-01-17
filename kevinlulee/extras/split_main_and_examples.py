"""
Split source code into main content and example/script sections.

Separates function/component definitions from other content like
setup code, prose, and example calls. Supports multiple languages.
"""

from __future__ import annotations
from kevinlulee.extras.ts_utils import (
    get_root_node_from_source,
    get_node_text,
    get_filetype_from_root,
)


def _is_typst_function_def(node) -> bool:
    """Check if a node is a Typst function definition (#let name(...) = ...)."""
    if node.type != "code":
        return False
    for child in node.children:
        if child.type == "let":
            for let_child in child.children:
                if let_child.type == "call":
                    return True
    return False


def _is_typescript_definition(node) -> bool:
    """Check if a node is a TypeScript/React definition (function, class, const component)."""
    if node.type in ("function_declaration", "class_declaration"):
        return True
    
    if node.type in ("export_statement", "lexical_declaration"):
        # export function/class or const Component = ...
        for child in node.children:
            if child.type in ("function_declaration", "class_declaration"):
                return True
            if child.type == "variable_declarator":
                # Check if it's a component (arrow function or function)
                for vc in child.children:
                    if vc.type in ("arrow_function", "function"):
                        return True
            if child.type == "lexical_declaration":
                return _is_typescript_definition(child)
        return True
    
    if node.type == "import_statement":
        return True
    
    return False


def _split_typst(root) -> tuple[str, str]:
    """Split Typst source into definitions and examples."""
    main_parts = []
    example_parts = []

    for child in root.children:
        text = get_node_text(child)
        if _is_typst_function_def(child):
            main_parts.append(text)
        else:
            example_parts.append(text)

    return "\n".join(main_parts).strip(), "\n".join(example_parts).strip()


def _split_typescript(root) -> tuple[str, str]:
    """Split TypeScript/React source into definitions and examples."""
    main_parts = []
    example_parts = []

    for child in root.children:
        text = get_node_text(child)
        if _is_typescript_definition(child):
            main_parts.append(text)
        else:
            example_parts.append(text)

    return "\n".join(main_parts).strip(), "\n".join(example_parts).strip()


def split_main_and_examples(source: str) -> tuple[str, str]:
    """
    Split source code into definitions and example/script code.

    For Typst: Function definitions (#let name(...) = ...) go to main.
    For TypeScript/React: Functions, classes, components, imports go to main.
    
    Everything else (set rules, content, calls, expressions) goes to examples.

    Args:
        source: File path or source code string.

    Returns:
        Tuple of (main_code, example_code).
    """
    root = get_root_node_from_source(source)
    filetype = get_filetype_from_root(root)

    match filetype:
        case "typst":
            return _split_typst(root)
        case "typescript" | "tsx":
            return _split_typescript(root)
        case _:
            # Fallback: return everything as main
            return get_node_text(root), ""


if __name__ == "__main__":
    typst_src = """
#let a = 1
#set document(title: "Test")
#let highlight(text) = box(fill: red, text)
#let foo(x, y: 1) = x + y
Here is some #highlight[text].
"""
    main, examples = split_main_and_examples(typst_src)
    print("=== TYPST MAIN ===")
    print(main)
    print("\n=== TYPST EXAMPLES ===")
    print(examples)

    ts_src = """
import React from 'react';
import { useState } from 'react';

const Button = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>;
};

function formatDate(date) {
  return date.toISOString();
}

export class Counter extends React.Component {
  render() {
    return <div>{this.props.count}</div>;
  }
}

console.log('hello');
formatDate(new Date());
const x = 1 + 2;
"""
    # main, examples = split_main_and_examples(ts_src)
    # print("\n=== TYPESCRIPT MAIN ===")
    # print(main)
    # print("\n=== TYPESCRIPT EXAMPLES ===")
    # print(examples)
