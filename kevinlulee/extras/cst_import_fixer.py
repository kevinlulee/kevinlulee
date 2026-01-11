import libcst as cst
import kevinlulee as kx
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ImportInfo:
    module: str
    names: list[str]
    node: cst.ImportFrom


class ExportCollector(cst.CSTVisitor):
    """Collect all exported names from a file."""
    
    def __init__(self):
        self.exports: set[str] = set()
        self._depth = 0
    
    def visit_ClassDef(self, node: cst.ClassDef):
        if self._depth == 0:
            self.exports.add(node.name.value)
        self._depth += 1
    
    def leave_ClassDef(self, node: cst.ClassDef):
        self._depth -= 1
    
    def visit_FunctionDef(self, node: cst.FunctionDef):
        if self._depth == 0:
            self.exports.add(node.name.value)
        self._depth += 1
    
    def leave_FunctionDef(self, node: cst.FunctionDef):
        self._depth -= 1
    
    def visit_Assign(self, node: cst.Assign):
        if self._depth > 0:
            return
        for target in node.targets:
            if isinstance(target.target, cst.Name):
                self.exports.add(target.target.value)
    
    def visit_AnnAssign(self, node: cst.AnnAssign):
        if self._depth > 0:
            return
        if isinstance(node.target, cst.Name):
            self.exports.add(node.target.value)


class ImportCollector(cst.CSTVisitor):
    """Collect all from imports."""
    
    def __init__(self):
        self.imports: list[ImportInfo] = []
    
    def visit_ImportFrom(self, node: cst.ImportFrom):
        if node.module is None or isinstance(node.names, cst.ImportStar):
            return
        
        module = _get_module_str(node.module)
        names = []
        for alias in node.names:
            if isinstance(alias, cst.ImportAlias) and isinstance(alias.name, cst.Name):
                names.append(alias.name.value)
        
        if names:
            self.imports.append(ImportInfo(module=module, names=names, node=node))


class ImportFixer(cst.CSTTransformer):
    """Fix broken imports by remapping to new sources."""
    
    def __init__(self, remappings: dict[str, dict[str, str]]):
        super().__init__()
        self.remappings = remappings
        self.new_imports: list[tuple[str, list[str]]] = []
        self.modified = False
    
    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom):
        if updated.module is None or isinstance(updated.names, cst.ImportStar):
            return updated
        
        module = _get_module_str(updated.module)
        if module not in self.remappings:
            return updated
        
        remap = self.remappings[module]
        keep_names = []
        move_names: dict[str, list[str]] = defaultdict(list)
        
        for alias in updated.names:
            if not isinstance(alias, cst.ImportAlias) or not isinstance(alias.name, cst.Name):
                keep_names.append(alias)
                continue
            
            name = alias.name.value
            if name in remap:
                move_names[remap[name]].append(name)
                self.modified = True
            else:
                keep_names.append(alias)
        
        for new_mod, names in move_names.items():
            self.new_imports.append((new_mod, names))
        
        if not keep_names:
            return cst.RemovalSentinel.REMOVE
        
        return updated.with_changes(names=keep_names)
    
    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        if not self.new_imports:
            return updated
        
        new_import_nodes = []
        for mod, names in self.new_imports:
            aliases = [cst.ImportAlias(name=cst.Name(n)) for n in names]
            new_import_nodes.append(
                cst.SimpleStatementLine(body=[
                    cst.ImportFrom(
                        module=_build_module_attr(mod),
                        names=aliases
                    )
                ])
            )
        
        insert_idx = 0
        for i, stmt in enumerate(updated.body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    insert_idx = i + 1
        
        new_body = list(updated.body[:insert_idx]) + new_import_nodes + list(updated.body[insert_idx:])
        return updated.with_changes(body=new_body)


def _get_module_str(node) -> str:
    parts = []
    current = node
    while isinstance(current, cst.Attribute):
        parts.append(current.attr.value)
        current = current.value
    if isinstance(current, cst.Name):
        parts.append(current.value)
    return ".".join(reversed(parts))


def _build_module_attr(module_str: str):
    parts = module_str.split(".")
    result = cst.Name(parts[0])
    for part in parts[1:]:
        result = cst.Attribute(value=result, attr=cst.Name(part))
    return result

from pathlib import Path
import re
from typing import Pattern

def get_paths(
    directory: Path | str,
    regex: str | Pattern[str],
) -> list[Path]:
    """
    Return all paths in a directory tree whose string path matches a regex.

    Args:
        directory: Root directory to search.
        regex: Compiled regex or pattern string.

    Returns:
        List of Path objects.
    """
    base = Path(directory).expanduser()
    pattern = re.compile(regex) if isinstance(regex, str) else regex

    return [
        p
        for p in base.rglob("*")
        if pattern.search(str(p))
    ]


def path_to_module(file_path: Path, root: Path) -> str:
    rel = file_path.relative_to(root)
    parts = list(rel.parts[:-1]) + [rel.stem]
    return ".".join(parts)


def cst_import_fixer(dir: str | Path) -> list[Path]:
    """
    Fix broken imports in the given files.
    
    Returns:
        List of files that were modified
    """
    # Build set of existing modules

    root = Path(dir).expanduser()
    file_paths = get_paths(root, '\.py$')
    kx.pretty_print(file_paths)
    existing_modules = set()
    for p in file_paths:
        mod = path_to_module(p, root)
        existing_modules.add(mod)
    
    # Build export index: {name: [module_paths that export it]}
    export_index: dict[str, list[str]] = defaultdict(list)
    
    for fp in file_paths:
        try:
            tree = cst.parse_module(fp.read_text())
            collector = ExportCollector()
            tree.visit(collector)
            mod_path = path_to_module(fp, root)
            for name in collector.exports:
                export_index[name].append(mod_path)
        except Exception as e:
            print(f"Error parsing {fp}: {e}")
            continue
    
    modified_files = []
    
    for fp in file_paths:
        try:
            source = fp.read_text()
            tree = cst.parse_module(source)
            
            # Collect imports
            import_collector = ImportCollector()
            tree.visit(import_collector)
            
            # Find broken imports and build remappings
            remappings: dict[str, dict[str, str]] = {}
            
            for imp in import_collector.imports:
                # Check if module exists
                if imp.module in existing_modules:
                    continue
                
                # Module doesn't exist, try to find new homes for names
                name_remaps = {}
                for name in imp.names:
                    candidates = export_index.get(name, [])
                    if candidates:
                        name_remaps[name] = candidates[0]
                
                if name_remaps:
                    remappings[imp.module] = name_remaps
            
            if not remappings:
                continue
            
            # Apply fixes
            fixer = ImportFixer(remappings)
            new_tree = tree.visit(fixer)
            
            if fixer.modified:
                fp.write_text(new_tree.code)
                modified_files.append(fp)
        
        except Exception as e:
            print(f"Error processing {fp}: {e}")
            continue
    
    print("Modified files:")
    for f in modified_files:
        print(f"  {f.relative_to(root)}")
        
    return modified_files


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create package structure
        (root / "pkg").mkdir()
        (root / "pkg" / "foobar").mkdir()
        (root / "pkg" / "__init__.py").write_text("")
        
        # File that exports MyClass and helper
        (root / "pkg" / "models.py").write_text(
"class MyClass:\n"
"    pass\n"
"\n"
"def helper():\n"
"    pass\n"
"\n"
"CONSTANT = 42\n"
)
        
        # File that exports process_data
        (root / "pkg" / "foobar" / "utils.py").write_text(
"def process_data(x):\n"
"    return x * 2\n"
)
        
        # File with broken import (old_module doesn't exist)
        (root / "pkg" / "main.py").write_text(
"from pkg.old_module import MyClass, helper\n"
"from pkg.deleted import process_data\n"
"\n"
"def run():\n"
"    obj = MyClass()\n"
"    helper()\n"
"    process_data(10)\n"
)
        
        # Gather all files
        print("\nOriginal main.py:")
        print((root / "pkg" / "main.py").read_text())
        
        # Run the fixer
        modified = cst_import_fixer(root)
        
        print("Modified files:")
        for f in modified:
            print(f"  {f.relative_to(root)}")
        
        print("\nFixed main.py:")
        print((root / "pkg" / "main.py").read_text())
