from __future__ import annotations
import kevinlulee as kx

from codefmt.lua import luafmt
from codefmt.yaml import yamlfmt
from codefmt.python import pythonfmt


from typing import TypedDict, List, Literal, Union
from pathlib import Path
import json

class FileEntry(TypedDict):
    name: str
    kind: Literal["file"]

class DirectoryTree(TypedDict):
    name: str
    kind: Literal["directory"]
    children: List[DirectoryTree | FileEntry]

def build_directory_tree(path: Path | str) -> DirectoryTree:
    
    p = Path(path)
    name = p.name

    if p.is_file() or not p.exists():
        return {"name": name, "kind": "file"}

    children: List[DirectoryTree] = []
    for entry in path.iterdir():
        children.append(build_directory_tree(entry))

    return {
        "name": path.name,
        "kind": "folder",
        "children": children
    }

import re
from typing import List, Optional

def _escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

class Node:
    def __init__(self, name: Optional[str], indent: int):
        self.name = name  # None for root or anonymous container
        self.indent = indent
        self.attrs = {}
        self.children: List[Node] = []
        self.text_lines: List[str] = []

    def add_child(self, node: "Node"):
        self.children.append(node)

    def add_text(self, text: str):
        self.text_lines.append(text)

def txflow(text: str) -> str:
    # Preprocess lines: capture indent and content
    raw_lines = text.splitlines()
    lines = []
    for ln in raw_lines:
        # measure leading spaces
        m = re.match(r"^( *)(.*)$", ln)
        indent = len(m.group(1))
        content = m.group(2).rstrip()
        if content == "":
            continue  # ignore blank lines
        lines.append((indent, content))

    # Helper to peek
    i = 0
    n = len(lines)

    # root dummy
    root = Node(name=None, indent=-1)
    stack = [root]  # stack of nodes; stack[-1] is current parent

    while i < n:
        indent, content = lines[i]

        # find the correct parent for this line by indent
        while stack and indent <= stack[-1].indent:
            stack.pop()

        parent = stack[-1]

        # If this line declares an element: "name:" or "name: some text"
        # m_colon = re.match(r"^([^\s:]+):(?:\s*(.*))?$", content)

        # If this line declares an element: "name:" or "name: some text"
        m_colon = re.match(r"^::([^\s:]+)::(?:\s*(.*))?$", content)
        if m_colon:
            name = m_colon.group(1)
            inline_text = m_colon.group(2) if m_colon.group(2) is not None and m_colon.group(2) != "" else None
            node = Node(name=name, indent=indent)
            if inline_text:
                node.add_text(inline_text)
            # attach to parent
            parent.add_child(node)
            stack.append(node)
            i += 1

            # Collect attributes: consecutive following lines with greater indent that match "key = value"
            while i < n and lines[i][0] > node.indent:
                next_indent, next_content = lines[i]
                m_attr = re.match(r"^([^\s=]+)\s*=\s*(.+)$", next_content)
                if m_attr:
                    key = m_attr.group(1)
                    val = m_attr.group(2)
                    node.attrs[key] = val
                    i += 1
                    continue
                else:
                    break
            continue

        # Not an element declaration. Could be a key=value that was not an attribute (no parent element just opened)
        m_kv = re.match(r"^([^\s=]+)\s*=\s*(.+)$", content)
        if m_kv:
            # If parent is root (no name) we treat key=value as a child element with attribute? Simpler: treat as text line "key = value"
            parent.add_text(content)
            i += 1
            continue

        # Otherwise treat as plain text line node under parent
        parent.add_text(content)
        i += 1

    # Render XML from root's children
    def render_node(node: Node, level: int) -> str:
        indentation = 0
        indent = " " * level * indentation
        if node.name is None:
            # anonymous root: render children only
            return "\n".join(render_node(c, level) for c in node.children)

        attrs_text = ""
        if node.attrs:
            attrs_text = " " + " ".join(f'{k}="{_escape_xml(v)}"' for k, v in node.attrs.items())

        # combine text lines into a single text content if present
        text_content = None
        if node.text_lines:
            # preserve line breaks as\n inside element
            text_content = "\n".join(_escape_xml(x) for x in node.text_lines)

        if not node.children and (text_content is None or text_content == ""):
            return f"{indent}<{node.name}{attrs_text} />"
        if not node.children and text_content is not None:
            if indentation:
                if "\n" in text_content:
                    text_content = "\n" + kx.indent(text_content, indentation) + "\n"
            else:
                text_content = ' ' + text_content + ' '
            return f"{indent}<{node.name}{attrs_text}>{text_content}</{node.name}>"
        # has children
        inner_parts = []
        if text_content is not None:
            # text followed by children: keep text as first inner line
            inner_parts.append(("text", text_content))
        for c in node.children:
            inner_parts.append(("node", render_node(c, level + 1)))
        # render inner
        if inner_parts and inner_parts[0][0] == "text" and len(inner_parts) == 1:
            # only text
            return f"{indent}<{node.name}{attrs_text}>{inner_parts[0][1]}</{node.name}>"
        else:
            lines = [f"{indent}<{node.name}{attrs_text}>"]
            for kind, val in inner_parts:
                if kind == "text":
                    # text lines may contain newlines -> indent each line
                    for ln in val.splitlines():
                        lines.append("  " * (level + 1) + ln)
                else:
                    lines.append(val)
            lines.append(f"{indent}</{node.name}>")
            return "\n".join(lines)

    xml = render_node(root, 0)
    return xml

# ---------------------
# Example call (one example as requested)
sample = """react:
    abc = 1
    ghi = 2
    adsfasdf afasdfasdf
    asfasdf asdfadf

    foobar: asdfasdf
    asdf: asdfasdf

    asdfasdf:
        alphalpha
        alphalpha fasdfasdf
        alphalpha

        asdf: asfadf
"""
# print(txflow(sample))

from kevinlulee import kx


def to_xml(tag, content:dict | list | str = '', indentation = 1, **attributes):
    """
    Recursively builds XML strings with smart formatting.
    
    - If content has newlines: uses multiline indented format
    - Otherwise: uses inline format
    - Supports attributes via kwargs
    - content can be a string or list
    """
    # Build attribute string
    attrs = ""
    if attributes:
        attrs = " " + " ".join(f'{k}={v}' for k, v in kx.filter_none(attributes).items())
    
    # Handle list content
    if isinstance(content, list):
        content = "\n".join(content)
    if isinstance(content, dict):
        content = "\n".join([to_xml(k, v) for k, v in content.items()])
    
    # Handle empty content
    if not content:
        return f"<{tag}{attrs}/>"
    
    # Check if content has newlines
    if not indentation:
        return f"<{tag}{attrs}>{content}</{tag}>"

    indentation = kx.to_spaces(indentation)
    if isinstance(content, str) and "\n" in content:
        indented = "\n".join(f"{indentation}{line}" for line in content.split("\n"))
        return f"<{tag}{attrs}>\n{indented}\n</{tag}>"
    else:
        # Inline format
        return f"<{tag}{attrs}>{content}</{tag}>"


def compile_requests():
    text = kx.text_getter("/home/kdog3682/scratch/requests.txt")
    def callback(s):
        if kx.test(s, '^[\w-]+:'):
            return txflow(s)
        return s
    items = kx.map(kx.split(text, '^(?:###).*'), callback)
    return kx.serialize_data(items)

