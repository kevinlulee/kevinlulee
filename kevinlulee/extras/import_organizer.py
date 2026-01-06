"""
LibCST codemods to organize Python imports.

ImportOrganizer: Removes unused imports, consolidates duplicates, and sorts into groups
(stdlib, third-party, local) with `import` before `from` within each group.
Handles TYPE_CHECKING blocks, `from __future__` imports, string forward references,
`# noqa` comments, and `__all__` exports.
"""

__all__ = ["ImportOrganizer"]
__author__ = "Claude"

import importlib
import re
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


STDLIB_MODULES = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio", "asyncore",
    "atexit", "audioop", "base64", "bdb", "binascii", "binhex", "bisect",
    "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk", "cmath", "cmd",
    "code", "codecs", "codeop", "collections", "colorsys", "compileall",
    "concurrent", "configparser", "contextlib", "contextvars", "copy", "copyreg",
    "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses", "datetime",
    "dbm", "decimal", "difflib", "dis", "distutils", "doctest", "email",
    "encodings", "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput",
    "fnmatch", "fractions", "ftplib", "functools", "gc", "getopt", "getpass",
    "gettext", "glob", "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac",
    "html", "http", "idlelib", "imaplib", "imghdr", "imp", "importlib", "inspect",
    "io", "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache",
    "locale", "logging", "lzma", "mailbox", "mailcap", "marshal", "math",
    "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc", "nis",
    "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform", "plistlib",
    "poplib", "posix", "posixpath", "pprint", "profile", "pstats", "pty", "pwd",
    "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random", "re",
    "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched", "secrets",
    "select", "selectors", "shelve", "shlex", "shutil", "signal", "site",
    "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd", "sqlite3",
    "ssl", "stat", "statistics", "string", "stringprep", "struct", "subprocess",
    "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny", "tarfile",
    "telnetlib", "tempfile", "termios", "test", "textwrap", "threading", "time",
    "timeit", "tkinter", "token", "tokenize", "tomllib", "trace", "traceback",
    "tracemalloc", "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
    "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc",
    "zipapp", "zipfile", "zipimport", "zlib", "zoneinfo", "_thread", "__future__",
}

# Pattern to extract identifiers from string annotations
STRING_ANNOTATION_PATTERN = re.compile(r'\b([A-Z_][A-Za-z0-9_]*)\b')


class ImportInfo(NamedTuple):
    """Stores import information with noqa status."""
    asname: Optional[str]
    has_noqa: bool


class UsedNameCollector(cst.CSTVisitor):
    """Collect all used names, ignoring import statements."""

    def __init__(self):
        self.used_names: Set[str] = set()
        self.in_import = False
        self.in_type_checking = False
        self.type_checking_names: Set[str] = set()
        self.all_exports: Set[str] = set()
        self.has_future_annotations = False

    def visit_Import(self, node: cst.Import) -> bool:
        self.in_import = True
        return False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        # Check for `from __future__ import annotations`
        module = cst.helpers.get_full_name_for_node(node.module) if node.module else ""
        if module == "__future__" and not isinstance(node.names, cst.ImportStar):
            for alias in node.names:
                if alias.name.value == "annotations":
                    self.has_future_annotations = True
        self.in_import = True
        return False

    def leave_Import(self, node: cst.Import) -> None:
        self.in_import = False

    def leave_ImportFrom(self, node: cst.ImportFrom) -> None:
        self.in_import = False

    def visit_If(self, node: cst.If) -> bool:
        if self._is_type_checking_block(node.test):
            self.in_type_checking = True
        return True

    def leave_If(self, node: cst.If) -> None:
        if self._is_type_checking_block(node.test):
            self.in_type_checking = False

    def _is_type_checking_block(self, test: cst.BaseExpression) -> bool:
        if isinstance(test, cst.Name) and test.value == "TYPE_CHECKING":
            return True
        if isinstance(test, cst.Attribute):
            full = cst.helpers.get_full_name_for_node(test)
            return full == "typing.TYPE_CHECKING"
        return False

    def visit_Name(self, node: cst.Name) -> None:
        if not self.in_import:
            if self.in_type_checking:
                self.type_checking_names.add(node.value)
            else:
                self.used_names.add(node.value)

    def visit_Attribute(self, node: cst.Attribute) -> bool:
        if not self.in_import and isinstance(node.value, cst.Name):
            if self.in_type_checking:
                self.type_checking_names.add(node.value.value)
            else:
                self.used_names.add(node.value.value)
        return True

    def visit_Assign(self, node: cst.Assign) -> bool:
        # Check for __all__ = [...]
        for target in node.targets:
            if isinstance(target.target, cst.Name) and target.target.value == "__all__":
                self._extract_all_exports(node.value)
        return True

    def visit_AnnAssign(self, node: cst.AnnAssign) -> bool:
        # Check for __all__: list[str] = [...]
        if isinstance(node.target, cst.Name) and node.target.value == "__all__":
            if node.value:
                self._extract_all_exports(node.value)
        return True

    def visit_AugAssign(self, node: cst.AugAssign) -> bool:
        # Check for __all__ += [...]
        if isinstance(node.target, cst.Name) and node.target.value == "__all__":
            self._extract_all_exports(node.value)
        return True

    def _extract_all_exports(self, node: cst.BaseExpression) -> None:
        """Extract names from __all__ = [...] or __all__ = (...)"""
        if isinstance(node, (cst.List, cst.Tuple)):
            for el in node.elements:
                if isinstance(el, cst.Element) and isinstance(el.value, (cst.SimpleString, cst.ConcatenatedString)):
                    name = self._extract_string_value(el.value)
                    if name:
                        self.all_exports.add(name)

    def _extract_string_value(self, node: cst.BaseExpression) -> Optional[str]:
        """Extract string value from a string node."""
        if isinstance(node, cst.SimpleString):
            # Remove quotes
            val = node.value
            if val.startswith(('"""', "'''")):
                return val[3:-3]
            elif val.startswith(('"', "'")):
                return val[1:-1]
        elif isinstance(node, cst.ConcatenatedString):
            parts = []
            for part in node.left, node.right:
                extracted = self._extract_string_value(part)
                if extracted:
                    parts.append(extracted)
            return "".join(parts) if parts else None
        return None

    def visit_Annotation(self, node: cst.Annotation) -> bool:
        self._collect_annotation_names(node.annotation)
        return False

    def _collect_annotation_names(self, node: cst.BaseExpression) -> None:
        """Recursively collect names from type annotations, including string annotations."""
        if isinstance(node, cst.Name):
            self.used_names.add(node.value)
        elif isinstance(node, cst.Attribute):
            if isinstance(node.value, cst.Name):
                self.used_names.add(node.value.value)
        elif isinstance(node, cst.Subscript):
            self._collect_annotation_names(node.value)
            for el in node.slice:
                if isinstance(el, cst.SubscriptElement):
                    if isinstance(el.slice, cst.Index):
                        self._collect_annotation_names(el.slice.value)
        elif isinstance(node, cst.BinaryOperation):
            self._collect_annotation_names(node.left)
            self._collect_annotation_names(node.right)
        elif isinstance(node, (cst.SimpleString, cst.ConcatenatedString, cst.FormattedString)):
            # String forward reference
            self._extract_names_from_string_annotation(node)

    def _extract_names_from_string_annotation(self, node: cst.BaseExpression) -> None:
        """Extract type names from string annotations like 'List[User]'."""
        string_val = self._extract_string_value(node)
        if string_val:
            # Find all potential type names (capitalized identifiers)
            matches = STRING_ANNOTATION_PATTERN.findall(string_val)
            for match in matches:
                self.used_names.add(match)


class ImportOrganizer(VisitorBasedCodemodCommand):
    """
    Sorts imports into groups: __future__, stdlib, third-party, local.
    Within each group: `import` statements before `from` statements.
    Removes unused imports and consolidates duplicates.
    Preserves TYPE_CHECKING blocks, noqa comments, and __all__ exports.
    """

    DESCRIPTION = "Organizes imports: removes unused, consolidates, and sorts."

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        # module -> {(asname, has_noqa), ...}
        self.imports: Dict[str, Set[Tuple[Optional[str], bool]]] = defaultdict(set)
        # module -> {name -> ImportInfo}
        self.from_imports: Dict[str, Dict[str, ImportInfo]] = defaultdict(dict)
        self.type_checking_imports: Dict[str, Set[Tuple[Optional[str], bool]]] = defaultdict(set)
        self.type_checking_from_imports: Dict[str, Dict[str, ImportInfo]] = defaultdict(dict)
        self.in_type_checking = False
        self.future_imports: Dict[str, ImportInfo] = {}
        self._current_stmt_has_noqa = False

    def _classify_import(self, module: str) -> int:
        if module == "__future__":
            return -1
        if module.startswith("."):
            return 2
        root = module.split(".")[0]
        if root in STDLIB_MODULES:
            return 0
        return 1

    def _has_noqa(self, node: cst.SimpleStatementLine) -> bool:
        """Check if the statement has a noqa comment."""
        tw = node.trailing_whitespace
        if isinstance(tw, cst.TrailingWhitespace) and tw.comment:
            comment = tw.comment.value.lower()
            if "noqa" in comment:
                # Check for F401 specifically or bare noqa
                if "f401" in comment or "noqa:" not in comment:
                    return True
        return False

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> bool:
        self._current_stmt_has_noqa = self._has_noqa(node)
        return True

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        self._current_stmt_has_noqa = False
        return updated_node

    def visit_If(self, node: cst.If) -> bool:
        if self._is_type_checking_block(node.test):
            self.in_type_checking = True
        return True

    def leave_If(
        self, original_node: cst.If, updated_node: cst.If
    ) -> cst.If:
        if self._is_type_checking_block(original_node.test):
            self.in_type_checking = False
        return updated_node

    def _is_type_checking_block(self, test: cst.BaseExpression) -> bool:
        if isinstance(test, cst.Name) and test.value == "TYPE_CHECKING":
            return True
        if isinstance(test, cst.Attribute):
            full = cst.helpers.get_full_name_for_node(test)
            return full == "typing.TYPE_CHECKING"
        return False

    def visit_Import(self, node: cst.Import) -> None:
        if isinstance(node.names, cst.ImportStar):
            return
        has_noqa = self._current_stmt_has_noqa
        target = self.type_checking_imports if self.in_type_checking else self.imports
        for alias in node.names:
            module = cst.helpers.get_full_name_for_node(alias.name)
            if module:
                asname = alias.asname.name.value if alias.asname and isinstance(alias.asname.name, cst.Name) else None
                target[module].add((asname, has_noqa))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        module = cst.helpers.get_full_name_for_node(node.module) if node.module else ""
        dots = "." * len(node.relative) if node.relative else ""
        full_module = dots + module
        has_noqa = self._current_stmt_has_noqa

        if full_module == "__future__":
            if not isinstance(node.names, cst.ImportStar):
                for alias in node.names:
                    name = alias.name.value
                    asname = alias.asname.name.value if alias.asname and isinstance(alias.asname.name, cst.Name) else None
                    self.future_imports[name] = ImportInfo(asname, has_noqa)
            return

        target = self.type_checking_from_imports if self.in_type_checking else self.from_imports

        if isinstance(node.names, cst.ImportStar):
            target[full_module]["*"] = ImportInfo(None, has_noqa)
            return

        for alias in node.names:
            name = alias.name.value
            asname = alias.asname.name.value if alias.asname and isinstance(alias.asname.name, cst.Name) else None
            # Preserve noqa if any import of this name had it
            existing = target[full_module].get(name)
            new_noqa = has_noqa or (existing.has_noqa if existing else False)
            target[full_module][name] = ImportInfo(asname, new_noqa)

    def _build_import_statement(
        self, module: str, asname: Optional[str] = None, has_noqa: bool = False
    ) -> cst.SimpleStatementLine:
        if "." in module:
            parts = module.split(".")
            mod_node: cst.BaseExpression = cst.Name(parts[0])
            for part in parts[1:]:
                mod_node = cst.Attribute(value=mod_node, attr=cst.Name(part))
        else:
            mod_node = cst.Name(module)

        if asname:
            alias = cst.ImportAlias(
                name=mod_node,
                asname=cst.AsName(
                    name=cst.Name(asname),
                    whitespace_before_as=cst.SimpleWhitespace(" "),
                    whitespace_after_as=cst.SimpleWhitespace(" ")
                )
            )
        else:
            alias = cst.ImportAlias(name=mod_node)

        trailing = cst.TrailingWhitespace(
            whitespace=cst.SimpleWhitespace("  "),
            comment=cst.Comment(value="# noqa: F401"),
            newline=cst.Newline()
        ) if has_noqa else cst.TrailingWhitespace()

        return cst.SimpleStatementLine(
            body=[cst.Import(names=[alias])],
            trailing_whitespace=trailing
        )

    def _build_from_import_statement(
        self, module: str, names: Dict[str, ImportInfo], any_noqa: bool = False
    ) -> cst.SimpleStatementLine:
        dots: List[cst.Dot] = []
        clean_module = module
        while clean_module.startswith("."):
            dots.append(cst.Dot())
            clean_module = clean_module[1:]

        mod_node: Optional[cst.BaseExpression] = None
        if clean_module:
            if "." in clean_module:
                parts = clean_module.split(".")
                mod_node = cst.Name(parts[0])
                for part in parts[1:]:
                    mod_node = cst.Attribute(value=mod_node, attr=cst.Name(part))
            else:
                mod_node = cst.Name(clean_module)

        import_names: Union[cst.ImportStar, List[cst.ImportAlias]]
        if "*" in names:
            import_names = cst.ImportStar()
            any_noqa = names["*"].has_noqa
        else:
            aliases: List[cst.ImportAlias] = []
            for name in sorted(names.keys()):
                info = names[name]
                if info.asname:
                    alias = cst.ImportAlias(
                        name=cst.Name(name),
                        asname=cst.AsName(
                            name=cst.Name(info.asname),
                            whitespace_before_as=cst.SimpleWhitespace(" "),
                            whitespace_after_as=cst.SimpleWhitespace(" ")
                        )
                    )
                else:
                    alias = cst.ImportAlias(name=cst.Name(name))
                aliases.append(alias)
            import_names = aliases

        trailing = cst.TrailingWhitespace(
            whitespace=cst.SimpleWhitespace("  "),
            comment=cst.Comment(value="# noqa: F401"),
            newline=cst.Newline()
        ) if any_noqa else cst.TrailingWhitespace()

        return cst.SimpleStatementLine(
            body=[cst.ImportFrom(
                module=mod_node,
                names=import_names,
                relative=dots if dots else []
            )],
            trailing_whitespace=trailing
        )

    def _filter_imports(
        self,
        imports: Dict[str, Set[Tuple[Optional[str], bool]]],
        from_imports: Dict[str, Dict[str, ImportInfo]],
        used_names: Set[str],
        all_exports: Set[str]
    ) -> Tuple[Dict[str, Set[Tuple[Optional[str], bool]]], Dict[str, Dict[str, ImportInfo]]]:
        combined_used = used_names | all_exports

        filtered_imports: Dict[str, Set[Tuple[Optional[str], bool]]] = defaultdict(set)
        for module, entries in imports.items():
            for asname, has_noqa in entries:
                check_name = asname if asname else module.split(".")[0]
                if check_name in combined_used or has_noqa:
                    filtered_imports[module].add((asname, has_noqa))

        filtered_from: Dict[str, Dict[str, ImportInfo]] = defaultdict(dict)
        for module, names in from_imports.items():
            for name, info in names.items():
                if name == "*":
                    filtered_from[module]["*"] = info
                else:
                    check_name = info.asname if info.asname else name
                    if check_name in combined_used or info.has_noqa:
                        filtered_from[module][name] = info

        return filtered_imports, filtered_from

    def _build_sorted_imports(
        self,
        imports: Dict[str, Set[Tuple[Optional[str], bool]]],
        from_imports: Dict[str, Dict[str, ImportInfo]]
    ) -> List[cst.SimpleStatementLine]:
        groups: List[List[Tuple[str, int, cst.SimpleStatementLine]]] = [[], [], []]

        for module, entries in imports.items():
            cat = self._classify_import(module)
            if cat == -1:
                continue
            for asname, has_noqa in entries:
                stmt = self._build_import_statement(module, asname, has_noqa)
                sort_key = (asname or module).lower()
                groups[cat].append((sort_key, 0, stmt))

        for module, names in from_imports.items():
            cat = self._classify_import(module)
            if cat == -1 or not names:
                continue
            any_noqa = any(info.has_noqa for info in names.values())
            stmt = self._build_from_import_statement(module, names, any_noqa)
            sort_key = module.lstrip(".").lower()
            groups[cat].append((sort_key, 1, stmt))

        for g in groups:
            g.sort(key=lambda x: (x[1], x[0]))

        result: List[cst.SimpleStatementLine] = []
        for i, group in enumerate(groups):
            if group:
                if result:
                    # Add blank line between groups
                    last = result[-1]
                    result[-1] = last.with_changes(
                        trailing_whitespace=cst.TrailingWhitespace(
                            newline=cst.Newline(value="\n")
                        )
                    )
                result.extend([stmt for _, _, stmt in group])

        return result

    def _build_type_checking_block(
        self,
        imports: Dict[str, Set[Tuple[Optional[str], bool]]],
        from_imports: Dict[str, Dict[str, ImportInfo]]
    ) -> Optional[cst.If]:
        stmts = self._build_sorted_imports(imports, from_imports)
        if not stmts:
            return None

        return cst.If(
            test=cst.Name("TYPE_CHECKING"),
            body=cst.IndentedBlock(body=stmts),
            leading_lines=[cst.EmptyLine()],
        )

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        collector = UsedNameCollector()
        wrapper = cst.MetadataWrapper(original_node, unsafe_skip_copy=True)
        wrapper.visit(collector)
        used_names = collector.used_names | collector.type_checking_names
        all_exports = collector.all_exports

        filtered_imports, filtered_from = self._filter_imports(
            self.imports, self.from_imports, used_names, all_exports
        )
        filtered_tc_imports, filtered_tc_from = self._filter_imports(
            self.type_checking_imports, self.type_checking_from_imports,
            collector.type_checking_names, set()
        )

        new_body: List[Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]] = []
        import_insertion_idx = 0
        found_first_import = False

        for stmt in updated_node.body:
            is_import = (
                isinstance(stmt, cst.SimpleStatementLine)
                and len(stmt.body) == 1
                and isinstance(stmt.body[0], (cst.Import, cst.ImportFrom))
            )
            is_tc_block = isinstance(stmt, cst.If) and self._is_type_checking_block(stmt.test)

            if is_import or is_tc_block:
                if not found_first_import:
                    found_first_import = True
                    import_insertion_idx = len(new_body)
                continue
            new_body.append(stmt)

        organized: List[Union[cst.SimpleStatementLine, cst.If]] = []

        # __future__ first
        if self.future_imports:
            any_noqa = any(info.has_noqa for info in self.future_imports.values())
            stmt = self._build_from_import_statement("__future__", {
                k: v for k, v in self.future_imports.items()
            }, any_noqa)
            stmt = stmt.with_changes(
                trailing_whitespace=cst.TrailingWhitespace(newline=cst.Newline(value="\n"))
            )
            organized.append(stmt)

        regular = self._build_sorted_imports(filtered_imports, filtered_from)
        organized.extend(regular)

        tc_block = self._build_type_checking_block(filtered_tc_imports, filtered_tc_from)
        if tc_block:
            if organized:
                last = organized[-1]
                if isinstance(last, cst.SimpleStatementLine):
                    organized[-1] = last.with_changes(
                        trailing_whitespace=cst.TrailingWhitespace(newline=cst.Newline(value="\n"))
                    )
            organized.append(tc_block)

        final_body = new_body[:import_insertion_idx] + organized + new_body[import_insertion_idx:]
        return updated_node.with_changes(body=final_body)


if __name__ == "__main__":
    test_code = '''
from __future__ import annotations
import sys
import requests
from typing import TYPE_CHECKING, List, Dict
from foobar import *
from os import path, getcwd
from os import listdir
from collections import defaultdict
import json
from .local import helper
import unused_module
import kept_for_side_effects  # noqa: F401

if TYPE_CHECKING:
    from myapp.models import User
    from myapp.models import Order

__all__ = ["exported_func", "helper", 'unused_module']

def exported_func():
    pass

def main(user: "User") -> "List[Dict]":
    print(sys.version)
    print(path.exists("."))
    print(getcwd())
    print(listdir("."))
    data = defaultdict(list)
    items: List[Dict] = []
    resp = requests.get("http://example.com")
    helper()
    return items
'''

    print("=== ImportOrganizer ===")
    tree = cst.parse_module(test_code)
    modified = tree.visit(ImportOrganizer(CodemodContext()))
    print(modified.code)
