"""LibCST codemod to merge two Python modules, replacing matching definitions."""

__all__ = ["merge_modules"]
__author__ = "Claude"

import libcst as cst
from collections import OrderedDict
from typing import Dict, Set, List, Union, Sequence



class ImportCollector(cst.CSTTransformer):
    """Collects all imports from a module."""
    
    def __init__(self):
        super().__init__()
        self.imports: List[Union[cst.Import, cst.ImportFrom]] = []
        self.import_keys: Set[str] = set()
    
    def _node_to_code(self, node) -> str:
        return cst.parse_module("").code_for_node(node).strip()
    
    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        key = self._node_to_code(original)
        if key not in self.import_keys:
            self.import_keys.add(key)
            self.imports.append(original)
        return updated
    
    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
        key = self._node_to_code(original)
        if key not in self.import_keys:
            self.import_keys.add(key)
            self.imports.append(original)
        return updated


class DefinitionCollector(cst.CSTTransformer):
    """Collects top-level definitions and class methods."""
    
    def __init__(self):
        super().__init__()
        self.functions: Dict[str, cst.FunctionDef] = OrderedDict()
        self.classes: Dict[str, cst.ClassDef] = OrderedDict()
        self.class_methods: Dict[str, Dict[str, cst.FunctionDef]] = {}
        self._current_class: str = None
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._current_class = node.name.value
        self.classes[node.name.value] = node
        self.class_methods.setdefault(node.name.value, OrderedDict())
        return True
    
    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        self._current_class = None
        return updated
    
    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        name = original.name.value
        if self._current_class:
            self.class_methods[self._current_class][name] = original
        else:
            self.functions[name] = original
        return updated


class MergeClassMethods(cst.CSTTransformer):
    """Merges methods from source class into target class."""
    
    def __init__(self, source_methods: Dict[str, cst.FunctionDef], class_name: str):
        super().__init__()
        self.source_methods = source_methods
        self.class_name = class_name
        self.replaced_methods: Set[str] = set()
        self._in_target_class = False
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        if node.name.value == self.class_name:
            self._in_target_class = True
        return True
    
    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        if not self._in_target_class:
            return updated
        name = updated.name.value
        if name in self.source_methods:
            self.replaced_methods.add(name)
            return self.source_methods[name]
        return updated
    
    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        if updated.name.value != self.class_name:
            return updated
        
        self._in_target_class = False
        
        new_methods = [
            m for name, m in self.source_methods.items()
            if name not in self.replaced_methods
        ]
        
        if not new_methods:
            return updated
        
        new_body = list(updated.body.body)
        for method in new_methods:
            new_body.append(method)
        
        return updated.with_changes(body=updated.body.with_changes(body=new_body))


class ModuleMerger(cst.CSTTransformer):
    """Merges module B into module A."""
    
    def __init__(self, b_collector: DefinitionCollector, b_imports: List):
        super().__init__()
        self.b_collector = b_collector
        self.b_imports = b_imports
        self.replaced_functions: Set[str] = set()
        self.replaced_classes: Set[str] = set()
        self.seen_imports: Set[str] = set()
    
    def _node_to_code(self, node) -> str:
        return cst.parse_module("").code_for_node(node).strip()
    
    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        self.seen_imports.add(self._node_to_code(original))
        return updated
    
    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
        self.seen_imports.add(self._node_to_code(original))
        return updated
    
    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        name = updated.name.value
        if name in self.b_collector.functions:
            self.replaced_functions.add(name)
            return self.b_collector.functions[name]
        return updated
    
    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        name = updated.name.value
        self.replaced_classes.add(name)
        
        if name in self.b_collector.class_methods:
            merger = MergeClassMethods(self.b_collector.class_methods[name], name)
            updated = updated.visit(merger)
        
        return updated
    
    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        new_body = list(updated.body)
        
        last_import_idx = -1
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    last_import_idx = i
        
        imports_to_insert = []
        for imp in self.b_imports:
            key = self._node_to_code(imp)
            if key not in self.seen_imports:
                self.seen_imports.add(key)
                imports_to_insert.append(cst.SimpleStatementLine(body=[imp]))
        
        if imports_to_insert:
            insert_pos = last_import_idx + 1 if last_import_idx >= 0 else 0
            new_body = new_body[:insert_pos] + imports_to_insert + new_body[insert_pos:]
        
        additions = []
        
        for name, func in self.b_collector.functions.items():
            if name not in self.replaced_functions:
                additions.append(func)
        
        for name, cls in self.b_collector.classes.items():
            if name not in self.replaced_classes:
                additions.append(cls)
        
        if additions:
            new_body.extend(additions)
        
        return updated.with_changes(body=new_body)


def merge_modules(a_code: str, b_code: str) -> str:
    """Merge module B into module A, returning the merged code."""
    a_tree = cst.parse_module(a_code)
    b_tree = cst.parse_module(b_code)
    
    b_import_collector = ImportCollector()
    b_tree.visit(b_import_collector)
    
    b_def_collector = DefinitionCollector()
    b_tree.visit(b_def_collector)
    
    merger = ModuleMerger(b_def_collector, b_import_collector.imports)
    merged_tree = a_tree.visit(merger)
    
    return merged_tree.code


if __name__ == "__main__":
    a_code = '''\
import os
from typing import List, Optional


def foobar(x: int) -> int:
    """Original foobar in A."""
    return x + 1


def helper():
    """This only exists in A."""
    print("I'm a helper")


class MyClass:
    def __init__(self, name: str):
        self.name = name
    
    def abc(self) -> str:
        """Original abc method in A."""
        return f"Hello from A: {self.name}"
    
    def only_in_a(self):
        """This method only exists in A."""
        return "only in A"


class OnlyInA:
    """This class only exists in A."""
    pass
'''

    b_code = '''\
import json
from typing import Dict
from pathlib import Path


def foobar(x: int) -> int:
    """Replacement foobar from B - does something different."""
    return x * 100


def new_function():
    """This function only exists in B."""
    return "I'm new from B"


class MyClass:
    def abc(self) -> str:
        """Replacement abc method from B."""
        return f"Hello from B: {self.name} (improved!)"
    
    def new_method(self):
        """This method only exists in B."""
        return "new method from B"


class OnlyInB:
    """This class only exists in B."""
    
    def do_stuff(self):
        return Path(".").resolve()
'''

    print(merge_modules(a_code, b_code))
