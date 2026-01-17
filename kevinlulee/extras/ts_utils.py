from __future__ import annotations
from typing import Callable
import tree_sitter
from tree_sitter import Language, Parser, Tree, Node, Query
from kevinlulee import kx


def get_language(filetype: str) -> Language:
    """
    Get the tree-sitter Language object for a given filetype.

    Args:
        filetype: Language identifier (e.g., "python", "javascript", "typescript", "tsx", "html", "typst")

    Returns:
        The tree-sitter Language object for parsing.

    Raises:
        ValueError: If the filetype is not supported.
    """
    match filetype:
        case "python":
            import tree_sitter_python
            return Language(tree_sitter_python.language())
        case "javascript":
            import tree_sitter_javascript
            return Language(tree_sitter_javascript.language())
        case "typescript":
            import tree_sitter_typescript
            return Language(tree_sitter_typescript.language_typescript())
        case "tsx":
            import tree_sitter_typescript
            return Language(tree_sitter_typescript.language_tsx())
        case "html":
            import tree_sitter_html
            return Language(tree_sitter_html.language())
        case "typst":
            import tree_sitter_typst
            return Language(tree_sitter_typst.language())
        case _:
            raise ValueError(f"Unsupported filetype: {filetype}")


def get_syntax_tree(text: str, filetype: str) -> Tree:
    """
    Parse source code into a tree-sitter syntax tree.

    Args:
        text: Source code as a string.
        filetype: Language identifier for the parser.

    Returns:
        The parsed tree-sitter Tree object.
    """
    language = get_language(filetype)
    parser = Parser()
    parser.language = language
    return parser.parse(bytes(text, "utf8"))


def get_root_node(text: str, filetype: str) -> Node:
    """
    Parse source code and return the root node of the syntax tree.

    Args:
        text: Source code as a string.
        filetype: Language identifier for the parser.

    Returns:
        The root Node of the parsed syntax tree.
    """
    return get_syntax_tree(text, filetype).root_node


def get_root_node_from_source(source: str | Callable | Node | Tree) -> Node:
    """
    Convert various input types to a tree-sitter root Node.

    Accepts multiple input formats and returns the corresponding syntax tree root node.
    The language is automatically inferred from the source content or file extension.

    Args:
        source: One of the following:
            - tree_sitter.Node: Returned as-is
            - tree_sitter.Tree: Returns the tree's root_node
            - Callable: Extracts source code via inspect.getsource and parses it
            - str (file path): Reads and parses the file contents
            - str (source code): Parses the string as source code

    Returns:
        The root Node of the parsed syntax tree.

    Raises:
        ValueError: If the language cannot be inferred or is unsupported.
    """
    if isinstance(source, tree_sitter.Node):
        return source
    if isinstance(source, tree_sitter.Tree):
        return source.root_node
    if callable(source):
        text = kx.inspect.getsource(source)
        return get_root_node(text, kx.infer_lang(text))
    if kx.is_file(source):
        text = kx.readfile(source)
        filetype = kx.resolve_filetype(source)
        return get_root_node(text, filetype)
    return get_root_node(source, kx.infer_lang(source))


def get_node_text(node: Node) -> str:
    """
    Extract the text content of a tree-sitter node.

    Args:
        node: A tree-sitter Node object.

    Returns:
        The UTF-8 decoded text that the node spans in the source code.
    """
    return node.text.decode("utf-8")


def get_filetype_from_root(node: Node) -> str:
    """
    Infer the filetype from a root node's type.

    Args:
        node: A tree-sitter root node.

    Returns:
        The inferred filetype string, or "unknown" if not recognized.
    """
    match node.type:
        case "module":
            return "python"
        case "source_file":
            return "typst"
        case "translation_unit":
            return "c"
        case "program":
            return "typescript"
        case "source":
            return "rust"
        case "compilation_unit":
            return "java"
        case "document":
            return "html"
        case "stylesheet":
            return "css"
        case "script" | "chunk":
            return "lua"
        case "package":
            return "go"
        case "fragment":
            return "sql"
        case "stream":
            return "yaml"
        case "expression":
            return "nix"
        case _:
            return "unknown"


