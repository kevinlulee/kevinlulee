"""LibCST codemod to merge two Python modules, replacing matching definitions."""

__all__ = ["merge_modules"]
__author__ = "Claude"

import libcst as cst
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Set, List, Union, Optional, Callable


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CollectedImports:
    """All imports from a module, deduplicated by code representation."""
    imports: List[Union[cst.Import, cst.ImportFrom]] = field(default_factory=list)
    import_keys: Set[str] = field(default_factory=set)

    def add(self, node: Union[cst.Import, cst.ImportFrom], key: str):
        if key not in self.import_keys:
            self.import_keys.add(key)
            self.imports.append(node)


@dataclass
class CollectedDefinitions:
    """All top-level definitions from a module."""
    functions: Dict[str, cst.FunctionDef] = field(default_factory=OrderedDict)
    classes: Dict[str, cst.ClassDef] = field(default_factory=OrderedDict)
    class_methods: Dict[str, Dict[str, cst.FunctionDef]] = field(default_factory=dict)
    class_bases: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class OrphanMethod:
    """A function with 'self' param that isn't inside a class."""
    name: str
    node: cst.FunctionDef


@dataclass
class MergePlan:
    """The complete plan for how to merge module B into module A."""
    imports_to_add: List[Union[cst.Import, cst.ImportFrom]]
    functions_to_replace: Dict[str, cst.FunctionDef]
    functions_to_add: List[cst.FunctionDef]
    classes_to_add: List[cst.ClassDef]
    method_merges: Dict[str, Dict[str, cst.FunctionDef]]  # class_name -> {method_name -> node}


# =============================================================================
# Collectors
# =============================================================================

def _node_to_code(node) -> str:
    return cst.parse_module("").code_for_node(node).strip()


class ImportCollector(cst.CSTVisitor):
    def __init__(self):
        self.result = CollectedImports()

    def visit_Import(self, node: cst.Import) -> bool:
        self.result.add(node, _node_to_code(node))
        return False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        self.result.add(node, _node_to_code(node))
        return False


class DefinitionCollector(cst.CSTVisitor):
    def __init__(self):
        self.result = CollectedDefinitions()
        self.orphan_methods: List[OrphanMethod] = []
        self._current_class: Optional[str] = None

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        name = node.name.value
        self._current_class = name
        self.result.classes[name] = node
        self.result.class_methods.setdefault(name, OrderedDict())
        self.result.class_bases[name] = self._extract_base_names(node)
        return True

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._current_class = None

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        name = node.name.value
        if self._current_class:
            self.result.class_methods[self._current_class][name] = node
        elif self._has_self_param(node):
            self.orphan_methods.append(OrphanMethod(name, node))
        else:
            self.result.functions[name] = node
        return False

    def _has_self_param(self, node: cst.FunctionDef) -> bool:
        if node.params.params:
            first = node.params.params[0]
            if isinstance(first.name, cst.Name) and first.name.value == "self":
                return True
        return False

    def _extract_base_names(self, node: cst.ClassDef) -> List[str]:
        bases = []
        for arg in node.bases:
            if isinstance(arg.value, cst.Name):
                bases.append(arg.value.value)
            elif isinstance(arg.value, cst.Attribute):
                bases.append(_node_to_code(arg.value))
        return bases


# =============================================================================
# Analysis
# =============================================================================

class InheritanceAnalyzer:
    """Analyzes class inheritance to find optimal placement for orphan methods."""

    def __init__(self, class_bases: Dict[str, List[str]]):
        self.class_bases = class_bases

    def find_root_classes(self) -> List[str]:
        """Find classes that have no local superclass."""
        roots = []
        for cls in self.class_bases:
            bases = self.class_bases.get(cls, [])
            has_local_super = any(b in self.class_bases for b in bases)
            if not has_local_super:
                roots.append(cls)
        return roots

    def get_candidate_targets(self) -> List[str]:
        """Get candidate classes for orphan methods, preferring superclasses."""
        if not self.class_bases:
            return []

        roots = self.find_root_classes()

        # If all classes are roots (no inheritance), return all
        if len(roots) == len(self.class_bases):
            return list(self.class_bases.keys())

        return roots


class MergePlanner:
    """Creates a merge plan from collected definitions."""

    def __init__(
        self,
        a_defs: CollectedDefinitions,
        a_imports: CollectedImports,
        b_defs: CollectedDefinitions,
        b_imports: CollectedImports,
        b_orphans: List[OrphanMethod],
        chooser: Optional[Callable[[List[str], str], Optional[str]]] = None,
    ):
        self.a_defs = a_defs
        self.a_imports = a_imports
        self.b_defs = b_defs
        self.b_imports = b_imports
        self.b_orphans = b_orphans
        self.chooser = chooser

    def create_plan(self) -> MergePlan:
        # Imports
        imports_to_add = [
            imp for imp in self.b_imports.imports
            if _node_to_code(imp) not in self.a_imports.import_keys
        ]

        # Functions
        functions_to_replace = {
            name: func for name, func in self.b_defs.functions.items()
            if name in self.a_defs.functions
        }
        functions_to_add = [
            func for name, func in self.b_defs.functions.items()
            if name not in self.a_defs.functions
        ]

        # New classes
        classes_to_add = [
            cls for name, cls in self.b_defs.classes.items()
            if name not in self.a_defs.classes
        ]

        # Method merges for existing classes
        method_merges: Dict[str, Dict[str, cst.FunctionDef]] = {}
        for class_name, methods in self.b_defs.class_methods.items():
            if class_name in self.a_defs.classes:
                method_merges[class_name] = methods

        # Handle orphan methods
        self._assign_orphans(method_merges, functions_to_add)

        return MergePlan(
            imports_to_add=imports_to_add,
            functions_to_replace=functions_to_replace,
            functions_to_add=functions_to_add,
            classes_to_add=classes_to_add,
            method_merges=method_merges,
        )

    def _assign_orphans(
        self,
        method_merges: Dict[str, Dict[str, cst.FunctionDef]],
        functions_to_add: List[cst.FunctionDef],
    ):
        """Assign orphan methods to classes or fall back to regular functions."""
        if not self.b_orphans:
            return

        if not self.a_defs.classes:
            # No classes - orphans become regular functions
            functions_to_add.extend(o.node for o in self.b_orphans)
            return

        analyzer = InheritanceAnalyzer(self.a_defs.class_bases)
        candidates = analyzer.get_candidate_targets()

        if len(candidates) == 1:
            target = candidates[0]
            method_merges.setdefault(target, {})
            for orphan in self.b_orphans:
                method_merges[target][orphan.name] = orphan.node
            return

        # Multiple candidates - need chooser
        if not self.chooser:
            # No chooser, orphans become regular functions
            functions_to_add.extend(o.node for o in self.b_orphans)
            return

        for orphan in self.b_orphans:
            msg = f"Select target class for method '{orphan.name}':"
            choice = self.chooser(candidates, msg)
            if choice and choice in candidates:
                method_merges.setdefault(choice, {})
                method_merges[choice][orphan.name] = orphan.node
            else:
                functions_to_add.append(orphan.node)


# =============================================================================
# Transformers
# =============================================================================

class ClassMethodMerger(cst.CSTTransformer):
    def __init__(self, methods: Dict[str, cst.FunctionDef], class_name: str):
        super().__init__()
        self.methods = methods
        self.class_name = class_name
        self.replaced: Set[str] = set()
        self._in_target = False

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._in_target = node.name.value == self.class_name
        return True

    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        if not self._in_target:
            return updated
        name = updated.name.value
        if name in self.methods:
            self.replaced.add(name)
            return self.methods[name]
        return updated

    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        if updated.name.value != self.class_name:
            return updated
        self._in_target = False

        new_methods = [m for n, m in self.methods.items() if n not in self.replaced]
        if not new_methods:
            return updated

        new_body = list(updated.body.body) + new_methods
        return updated.with_changes(body=updated.body.with_changes(body=new_body))


class ModuleTransformer(cst.CSTTransformer):
    def __init__(self, plan: MergePlan):
        super().__init__()
        self.plan = plan
        self.seen_imports: Set[str] = set()
        self.replaced_functions: Set[str] = set()
        self.merged_classes: Set[str] = set()

    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        self.seen_imports.add(_node_to_code(original))
        return updated

    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
        self.seen_imports.add(_node_to_code(original))
        return updated

    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        name = updated.name.value
        if name in self.plan.functions_to_replace:
            self.replaced_functions.add(name)
            return self.plan.functions_to_replace[name]
        return updated

    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        name = updated.name.value
        self.merged_classes.add(name)
        if name in self.plan.method_merges:
            merger = ClassMethodMerger(self.plan.method_merges[name], name)
            updated = updated.visit(merger)
        return updated

    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        new_body = list(updated.body)

        # Find last import
        last_import_idx = -1
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    last_import_idx = i

        # Insert new imports
        imports_to_insert = []
        for imp in self.plan.imports_to_add:
            key = _node_to_code(imp)
            if key not in self.seen_imports:
                self.seen_imports.add(key)
                imports_to_insert.append(cst.SimpleStatementLine(body=[imp]))

        if imports_to_insert:
            pos = last_import_idx + 1 if last_import_idx >= 0 else 0
            new_body = new_body[:pos] + imports_to_insert + new_body[pos:]

        # Add new functions and classes
        new_body.extend(self.plan.functions_to_add)
        new_body.extend(self.plan.classes_to_add)

        return updated.with_changes(body=new_body)


# =============================================================================
# Public API
# =============================================================================

def _collect_module(code: str):
    tree = cst.parse_module(code)

    ic = ImportCollector()
    tree.visit(ic)

    dc = DefinitionCollector()
    tree.visit(dc)

    return tree, ic.result, dc.result, dc.orphan_methods


def merge_modules(
    a_code: str,
    b_code: str,
    chooser: Optional[Callable[[List[str], str], Optional[str]]] = None,
) -> str:
    """Merge module B into module A.

    Args:
        a_code: Source code of module A (base)
        b_code: Source code of module B (to merge in)
        chooser: Callback for disambiguation: (choices, message) -> selected
                 Matches nvim.ui.select signature. If None or returns None,
                 ambiguous orphan methods become regular functions.

    Returns:
        Merged source code.
    """
    a_tree, a_imports, a_defs, _ = _collect_module(a_code)
    _, b_imports, b_defs, b_orphans = _collect_module(b_code)

    planner = MergePlanner(a_defs, a_imports, b_defs, b_imports, b_orphans, chooser)
    plan = planner.create_plan()

    transformer = ModuleTransformer(plan)
    merged = a_tree.visit(transformer)

    return merged.code


# =============================================================================
# Example
# =============================================================================

if __name__ == "__main__":
    a_code = '''\
import os
from typing import List


class Animal:
    """Base class for animals."""

    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog:
    """A dog."""

    def speak(self) -> str:
        return "Woof!"


class Cat(Animal):
    """A cat."""

    def speak(self) -> str:
        return "Meow!"


def create_zoo() -> List[Animal]:
    return [Dog("Rex"), Cat("Whiskers")]
'''

    b_code = '''\
from datetime import datetime
import abc_datetime
import xx

a = 111

def eat(self, food: str) -> str:
    """Orphan method - will be added to Animal (the superclass)."""
    return f"{self.name} eats {food}"


def sleep(self) -> str:
    """Another orphan method."""
    return f"{self.name} is sleeping..."


def get_time() -> str:
    """Regular function, no self."""
    return abc_datetime.now().isoformat()


class Dog:
    def fetch(self, item: str) -> str:
        """Method specifically for Dog."""
        return f"{self.name} fetches the {item}!"
'''

    # print("=" * 60)
    # print("MODULE A:")
    # print("=" * 60)
    # print(a_code)
    #
    # print("=" * 60)
    # print("MODULE B:")
    # print("=" * 60)
    # print(b_code)

    def demo_chooser(choices: List[str], message: str) -> Optional[str]:
        """Simulates nvim.ui.select."""
        print(f"\n[nvim.ui.select] {message}")
        print(f"[choices] {choices}")
        print(f"[selected] Animal\n")
        return "Animal"

    print("=" * 60)
    print("MERGED (chooser selects 'Animal' for orphan methods):")
    print("=" * 60)
    print(merge_modules(a_code, b_code, chooser=demo_chooser))
