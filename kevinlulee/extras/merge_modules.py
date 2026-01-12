"""LibCST codemod to merge two Python modules, replacing matching definitions."""

__all__ = ["merge_modules"]
__author__ = "Claude"

import libcst as cst
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Set, List, Union, Optional, Callable
from enum import Enum, auto


# =============================================================================
# Quick Exit: Full Replacement Detection
# =============================================================================

def _should_fully_replace(a_code: str, b_code: str) -> bool:
    """Check if B should completely replace A (B is a full module replacement)."""
    b_lines = b_code.strip().splitlines()
    a_lines = a_code.strip().splitlines()

    has_all = any(re.match(r'^__all__\s*=', line) for line in b_lines)
    has_author = any(re.match(r'^__author__\s*=', line) for line in b_lines)

    if has_all and has_author and len(b_lines) >= len(a_lines) * 0.8:
        return True

    return False


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CollectedImports:
    imports: List[Union[cst.Import, cst.ImportFrom]] = field(default_factory=list)
    import_keys: Set[str] = field(default_factory=set)

    def add(self, node: Union[cst.Import, cst.ImportFrom], key: str):
        if key not in self.import_keys:
            self.import_keys.add(key)
            self.imports.append(node)


class AssignmentKind(Enum):
    DICT = auto()
    LIST = auto()
    SET = auto()
    OTHER = auto()


@dataclass
class CollectedAssignment:
    name: str
    node: cst.SimpleStatementLine
    value_node: cst.BaseExpression
    kind: AssignmentKind


@dataclass
class CollectedDefinitions:
    functions: Dict[str, cst.FunctionDef] = field(default_factory=OrderedDict)
    classes: Dict[str, cst.ClassDef] = field(default_factory=OrderedDict)
    class_methods: Dict[str, Dict[str, cst.FunctionDef]] = field(default_factory=dict)
    class_bases: Dict[str, List[str]] = field(default_factory=dict)
    class_attributes: Dict[str, Set[str]] = field(default_factory=dict)  # class -> set of attr names
    assignments: Dict[str, CollectedAssignment] = field(default_factory=OrderedDict)


@dataclass
class OrphanMethod:
    name: str
    node: cst.FunctionDef
    accessed_attrs: Set[str] = field(default_factory=set)  # attrs accessed via self


@dataclass
class MergePlan:
    imports_to_add: List[Union[cst.Import, cst.ImportFrom]]
    functions_to_replace: Dict[str, cst.FunctionDef]
    functions_to_add: List[cst.FunctionDef]
    classes_to_replace: Dict[str, cst.ClassDef]
    classes_to_add: List[cst.ClassDef]
    method_merges: Dict[str, Dict[str, cst.FunctionDef]]
    assignment_merges: Dict[str, cst.SimpleStatementLine]
    assignments_to_add: List[cst.SimpleStatementLine]


# =============================================================================
# Utilities
# =============================================================================

def _node_to_code(node) -> str:
    return cst.parse_module("").code_for_node(node).strip()


def _classify_value(node: cst.BaseExpression) -> AssignmentKind:
    if isinstance(node, cst.Dict):
        return AssignmentKind.DICT
    if isinstance(node, (cst.List, cst.Tuple)):
        return AssignmentKind.LIST
    if isinstance(node, cst.Set):
        return AssignmentKind.SET
    if isinstance(node, cst.Call):
        func = node.func
        name = None
        if isinstance(func, cst.Name):
            name = func.value
        elif isinstance(func, cst.Attribute):
            name = func.attr.value
        if name in ("dict", "OrderedDict"):
            return AssignmentKind.DICT
        if name in ("list", "set", "frozenset"):
            return AssignmentKind.LIST if name == "list" else AssignmentKind.SET
    return AssignmentKind.OTHER


# =============================================================================
# Attribute Access Analyzer
# =============================================================================

class SelfAttributeCollector(cst.CSTVisitor):
    """Collects attributes accessed via 'self' in a function."""

    def __init__(self):
        self.attrs: Set[str] = set()

    def visit_Attribute(self, node: cst.Attribute) -> bool:
        if isinstance(node.value, cst.Name) and node.value.value == "self":
            self.attrs.add(node.attr.value)
        return True

    def visit_Call(self, node: cst.Call) -> bool:
        # Check for hasattr(self, 'x') or getattr(self, 'x')
        if isinstance(node.func, cst.Name) and node.func.value in ("hasattr", "getattr"):
            if len(node.args) >= 2:
                first_arg = node.args[0].value
                second_arg = node.args[1].value
                if isinstance(first_arg, cst.Name) and first_arg.value == "self":
                    if isinstance(second_arg, (cst.SimpleString, cst.ConcatenatedString)):
                        attr = second_arg.evaluated_value if hasattr(second_arg, 'evaluated_value') else None
                        if attr is None and isinstance(second_arg, cst.SimpleString):
                            # Extract string value manually
                            raw = second_arg.value
                            if (raw.startswith('"') and raw.endswith('"')) or \
                               (raw.startswith("'") and raw.endswith("'")):
                                attr = raw[1:-1]
                        if attr:
                            self.attrs.add(attr)
        return True


class ClassAttributeCollector(cst.CSTVisitor):
    """Collects all attributes defined/used in a class."""

    def __init__(self):
        self.attrs: Set[str] = set()
        self._class_depth = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._class_depth += 1
        return self._class_depth == 1  # Only recurse into the top-level class

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._class_depth -= 1

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        if self._class_depth == 1:
            self.attrs.add(node.name.value)
        return True  # Always recurse into function bodies to find self.x

    def visit_Attribute(self, node: cst.Attribute) -> bool:
        if self._class_depth == 1 and isinstance(node.value, cst.Name) and node.value.value == "self":
            self.attrs.add(node.attr.value)
        return True

    def visit_AnnAssign(self, node: cst.AnnAssign) -> bool:
        # Class-level annotated assignments
        if self._class_depth == 1 and isinstance(node.target, cst.Name):
            self.attrs.add(node.target.value)
        return True

    def visit_Assign(self, node: cst.Assign) -> bool:
        # Class-level assignments
        if self._class_depth == 1:
            for target in node.targets:
                if isinstance(target.target, cst.Name):
                    self.attrs.add(target.target.value)
        return True


def _extract_self_attrs(func: cst.FunctionDef) -> Set[str]:
    """Extract attributes accessed via self in a function."""
    collector = SelfAttributeCollector()
    func.visit(collector)
    return collector.attrs


def _extract_class_attrs(cls: cst.ClassDef) -> Set[str]:
    """Extract all attributes defined/used in a class."""
    collector = ClassAttributeCollector()
    cls.visit(collector)
    return collector.attrs


# =============================================================================
# Smart Chooser
# =============================================================================

class SmartChooser:
    """Analyzes orphan methods and matches them to best-fit classes."""

    def __init__(self, class_attrs: Dict[str, Set[str]]):
        self.class_attrs = class_attrs

    def choose(self, candidates: List[str], orphan: OrphanMethod) -> Optional[str]:
        """Choose the best class for an orphan method based on attribute overlap."""
        if not candidates:
            return None

        if not orphan.accessed_attrs:
            return candidates[0]

        scores: List[tuple[str, float, int]] = []

        for cls_name in candidates:
            cls_attrs = self.class_attrs.get(cls_name, set())
            
            overlap = orphan.accessed_attrs & cls_attrs
            overlap_count = len(overlap)
            
            # Coverage: what fraction of orphan's attrs are in this class
            coverage = overlap_count / len(orphan.accessed_attrs) if orphan.accessed_attrs else 0.0
            
            scores.append((cls_name, coverage, overlap_count))

        # Sort by coverage desc, then overlap count desc
        scores.sort(key=lambda x: (-x[1], -x[2]))
        
        return scores[0][0]


# =============================================================================
# Collectors
# =============================================================================

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
        self._depth = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        if self._depth == 0:
            name = node.name.value
            self._current_class = name
            self.result.classes[name] = node
            self.result.class_methods.setdefault(name, OrderedDict())
            self.result.class_bases[name] = self._extract_base_names(node)
            self.result.class_attributes[name] = _extract_class_attrs(node)
        self._depth += 1
        return True

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._depth -= 1
        if self._depth == 0:
            self._current_class = None

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        if self._depth > 0 and self._current_class:
            self.result.class_methods[self._current_class][node.name.value] = node
        elif self._depth == 0:
            if self._has_self_param(node):
                attrs = _extract_self_attrs(node)
                self.orphan_methods.append(OrphanMethod(node.name.value, node, attrs))
            else:
                self.result.functions[node.name.value] = node
        return False

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> bool:
        if self._depth > 0:
            return False
        for stmt in node.body:
            if isinstance(stmt, (cst.Assign, cst.AnnAssign)):
                self._collect_assignment(node, stmt)
        return False

    def _collect_assignment(self, line: cst.SimpleStatementLine, stmt: Union[cst.Assign, cst.AnnAssign]):
        if isinstance(stmt, cst.AnnAssign):
            if stmt.target and isinstance(stmt.target, cst.Name) and stmt.value:
                name = stmt.target.value
                kind = _classify_value(stmt.value)
                self.result.assignments[name] = CollectedAssignment(name, line, stmt.value, kind)
        elif isinstance(stmt, cst.Assign):
            for target in stmt.targets:
                if isinstance(target.target, cst.Name):
                    name = target.target.value
                    kind = _classify_value(stmt.value)
                    self.result.assignments[name] = CollectedAssignment(name, line, stmt.value, kind)

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
# Assignment Merger
# =============================================================================

class AssignmentMerger:
    def merge(self, a_assign: CollectedAssignment, b_assign: CollectedAssignment) -> cst.SimpleStatementLine:
        if a_assign.kind != b_assign.kind:
            return b_assign.node

        if a_assign.kind == AssignmentKind.DICT:
            return self._merge_dicts(a_assign, b_assign)
        elif a_assign.kind == AssignmentKind.LIST:
            return self._merge_lists(a_assign, b_assign)
        elif a_assign.kind == AssignmentKind.SET:
            return self._merge_sets(a_assign, b_assign)
        else:
            return b_assign.node

    def _merge_dicts(self, a: CollectedAssignment, b: CollectedAssignment) -> cst.SimpleStatementLine:
        if not isinstance(a.value_node, cst.Dict) or not isinstance(b.value_node, cst.Dict):
            return b.node

        a_elements = {self._dict_key_str(e): e for e in a.value_node.elements if isinstance(e, cst.DictElement)}
        for elem in b.value_node.elements:
            if isinstance(elem, cst.DictElement):
                a_elements[self._dict_key_str(elem)] = elem
            elif isinstance(elem, cst.StarredDictElement):
                a_elements[_node_to_code(elem)] = elem

        merged_dict = cst.Dict(elements=list(a_elements.values()))
        return self._replace_value(a.node, merged_dict)

    def _merge_lists(self, a: CollectedAssignment, b: CollectedAssignment) -> cst.SimpleStatementLine:
        a_elems = self._extract_list_elements(a.value_node)
        b_elems = self._extract_list_elements(b.value_node)

        seen = {_node_to_code(e) for e in a_elems}
        for elem in b_elems:
            code = _node_to_code(elem)
            if code not in seen:
                seen.add(code)
                a_elems.append(elem)

        if isinstance(a.value_node, cst.Tuple):
            merged = cst.Tuple(elements=[cst.Element(e) for e in a_elems])
        else:
            merged = cst.List(elements=[cst.Element(e) for e in a_elems])
        return self._replace_value(a.node, merged)

    def _merge_sets(self, a: CollectedAssignment, b: CollectedAssignment) -> cst.SimpleStatementLine:
        if not isinstance(a.value_node, cst.Set) or not isinstance(b.value_node, cst.Set):
            return b.node

        seen = {}
        for elem in a.value_node.elements:
            if isinstance(elem, cst.Element):
                seen[_node_to_code(elem.value)] = elem
        for elem in b.value_node.elements:
            if isinstance(elem, cst.Element):
                code = _node_to_code(elem.value)
                if code not in seen:
                    seen[code] = elem

        merged = cst.Set(elements=list(seen.values()))
        return self._replace_value(a.node, merged)

    def _dict_key_str(self, elem: cst.DictElement) -> str:
        return _node_to_code(elem.key) if elem.key else ""

    def _extract_list_elements(self, node: cst.BaseExpression) -> List[cst.BaseExpression]:
        if isinstance(node, (cst.List, cst.Tuple)):
            return [e.value for e in node.elements if isinstance(e, cst.Element)]
        return []

    def _replace_value(self, line: cst.SimpleStatementLine, new_value: cst.BaseExpression) -> cst.SimpleStatementLine:
        stmt = line.body[0]
        if isinstance(stmt, cst.AnnAssign):
            new_stmt = stmt.with_changes(value=new_value)
        elif isinstance(stmt, cst.Assign):
            new_stmt = stmt.with_changes(value=new_value)
        else:
            return line
        return line.with_changes(body=[new_stmt])


# =============================================================================
# Inheritance Analysis
# =============================================================================

class InheritanceAnalyzer:
    def __init__(self, a_bases: Dict[str, List[str]], b_bases: Dict[str, List[str]]):
        self.class_bases = {**a_bases, **b_bases}

    def find_root_classes(self) -> List[str]:
        roots = []
        for cls in self.class_bases:
            bases = self.class_bases.get(cls, [])
            has_local_super = any(b in self.class_bases for b in bases)
            if not has_local_super:
                roots.append(cls)
        return roots

    def get_candidate_targets(self) -> List[str]:
        if not self.class_bases:
            return []

        roots = self.find_root_classes()

        if len(roots) == len(self.class_bases):
            return list(self.class_bases.keys())

        return roots


# =============================================================================
# Merge Planning
# =============================================================================

class MergePlanner:
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
        self.assignment_merger = AssignmentMerger()

    def create_plan(self) -> MergePlan:
        imports_to_add = self._plan_imports()
        functions_to_replace, functions_to_add = self._plan_functions()
        classes_to_replace, classes_to_add, method_merges = self._plan_classes()
        assignment_merges, assignments_to_add = self._plan_assignments()

        self._assign_orphans(method_merges, functions_to_add, classes_to_add)

        return MergePlan(
            imports_to_add=imports_to_add,
            functions_to_replace=functions_to_replace,
            functions_to_add=functions_to_add,
            classes_to_replace=classes_to_replace,
            classes_to_add=classes_to_add,
            method_merges=method_merges,
            assignment_merges=assignment_merges,
            assignments_to_add=assignments_to_add,
        )

    def _plan_imports(self) -> List[Union[cst.Import, cst.ImportFrom]]:
        return [
            imp for imp in self.b_imports.imports
            if _node_to_code(imp) not in self.a_imports.import_keys
        ]

    def _plan_functions(self):
        replace = {n: f for n, f in self.b_defs.functions.items() if n in self.a_defs.functions}
        add = [f for n, f in self.b_defs.functions.items() if n not in self.a_defs.functions]
        return replace, add

    def _plan_classes(self):
        replace = {}
        add = []
        method_merges: Dict[str, Dict[str, cst.FunctionDef]] = {}

        for name, cls in self.b_defs.classes.items():
            if name in self.a_defs.classes:
                method_merges[name] = self.b_defs.class_methods.get(name, {})
            else:
                add.append(cls)

        return replace, add, method_merges

    def _plan_assignments(self):
        merges = {}
        adds = []

        for name, b_assign in self.b_defs.assignments.items():
            if name in self.a_defs.assignments:
                a_assign = self.a_defs.assignments[name]
                merges[name] = self.assignment_merger.merge(a_assign, b_assign)
            else:
                adds.append(b_assign.node)

        return merges, adds

    def _assign_orphans(
        self,
        method_merges: Dict[str, Dict[str, cst.FunctionDef]],
        functions_to_add: List[cst.FunctionDef],
        classes_to_add: List[cst.ClassDef],
    ):
        if not self.b_orphans:
            return

        analyzer = InheritanceAnalyzer(self.a_defs.class_bases, self.b_defs.class_bases)
        all_classes = set(self.a_defs.classes.keys()) | set(self.b_defs.classes.keys())

        if not all_classes:
            functions_to_add.extend(o.node for o in self.b_orphans)
            return

        candidates = analyzer.get_candidate_targets()

        if len(candidates) == 1:
            target = candidates[0]
            for orphan in self.b_orphans:
                self._add_orphan_to_target(orphan, target, method_merges, classes_to_add)
            return

        # Multiple candidates - use provided chooser or smart chooser
        all_class_attrs = {**self.a_defs.class_attributes, **self.b_defs.class_attributes}
        smart_chooser = SmartChooser(all_class_attrs)

        for orphan in self.b_orphans:
            choice = None

            if self.chooser:
                msg = f"Select target class for method '{orphan.name}':"
                choice = self.chooser(candidates, msg)

            if not choice or choice not in candidates:
                # Fall back to smart chooser
                choice = smart_chooser.choose(candidates, orphan)

            if choice:
                self._add_orphan_to_target(orphan, choice, method_merges, classes_to_add)
            else:
                functions_to_add.append(orphan.node)

    def _add_orphan_to_target(
        self,
        orphan: OrphanMethod,
        target: str,
        method_merges: Dict[str, Dict[str, cst.FunctionDef]],
        classes_to_add: List[cst.ClassDef],
    ):
        if target in self.a_defs.classes:
            method_merges.setdefault(target, {})
            method_merges[target][orphan.name] = orphan.node
        else:
            for i, cls in enumerate(classes_to_add):
                if cls.name.value == target:
                    new_body = list(cls.body.body) + [orphan.node]
                    classes_to_add[i] = cls.with_changes(
                        body=cls.body.with_changes(body=new_body)
                    )
                    break


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
        self._depth = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._depth += 1
        return True

    def leave_ClassDef(self, original: cst.ClassDef, updated: cst.ClassDef) -> cst.ClassDef:
        self._depth -= 1
        if self._depth > 0:
            return updated

        name = updated.name.value
        if name in self.plan.method_merges:
            merger = ClassMethodMerger(self.plan.method_merges[name], name)
            updated = updated.visit(merger)
        return updated

    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        self.seen_imports.add(_node_to_code(original))
        return updated

    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
        self.seen_imports.add(_node_to_code(original))
        return updated

    def leave_FunctionDef(self, original: cst.FunctionDef, updated: cst.FunctionDef) -> cst.FunctionDef:
        if self._depth > 0:
            return updated
        name = updated.name.value
        if name in self.plan.functions_to_replace:
            return self.plan.functions_to_replace[name]
        return updated

    def leave_SimpleStatementLine(
        self, original: cst.SimpleStatementLine, updated: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        if self._depth > 0:
            return updated

        for stmt in updated.body:
            name = None
            if isinstance(stmt, cst.AnnAssign) and isinstance(stmt.target, cst.Name):
                name = stmt.target.value
            elif isinstance(stmt, cst.Assign):
                for t in stmt.targets:
                    if isinstance(t.target, cst.Name):
                        name = t.target.value
                        break

            if name and name in self.plan.assignment_merges:
                return self.plan.assignment_merges[name]

        return updated

    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        new_body = list(updated.body)

        last_import_idx = -1
        last_assign_idx = -1

        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine):
                if any(isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body):
                    last_import_idx = i
                elif any(isinstance(s, (cst.Assign, cst.AnnAssign)) for s in stmt.body):
                    last_assign_idx = i

        imports_to_insert = []
        for imp in self.plan.imports_to_add:
            key = _node_to_code(imp)
            if key not in self.seen_imports:
                self.seen_imports.add(key)
                imports_to_insert.append(cst.SimpleStatementLine(body=[imp]))

        if imports_to_insert:
            pos = last_import_idx + 1 if last_import_idx >= 0 else 0
            new_body = new_body[:pos] + imports_to_insert + new_body[pos:]
            offset = len(imports_to_insert)
            if last_assign_idx >= pos:
                last_assign_idx += offset

        if self.plan.assignments_to_add:
            if last_assign_idx >= 0:
                pos = last_assign_idx + 1
            elif last_import_idx >= 0:
                pos = last_import_idx + 1 + len(imports_to_insert)
            else:
                pos = 0
            new_body = new_body[:pos] + self.plan.assignments_to_add + new_body[pos:]

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
        chooser: Optional callback for disambiguation: (choices, message) -> selected
                 If None or returns None, uses smart chooser based on attribute analysis.

    Full replacement:
        If B has __all__ and __author__ and is ~80%+ the size of A,
        B completely replaces A (no merge).

    Merge behavior:
        - Functions: B replaces A if same name, otherwise added
        - Classes: methods merged (B replaces), new classes added
        - Orphan methods (top-level with 'self'): smart-matched to classes by
          analyzing self.attr access patterns, or uses chooser callback
        - Dicts: B's keys override A's, new keys added
        - Lists/Tuples: extended uniquely
        - Sets: union
        - Other assignments: B replaces A
    """
    # Quick exit: full replacement
    if _should_fully_replace(a_code, b_code):
        return b_code

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
    # Example 1: Smart chooser matching based on attributes
    a_code = '''\
import os
from typing import List

CONFIG = {"debug": False}

PLUGINS = ["core", "auth"]


class FileHandler:
    """Handles file operations."""

    def __init__(self, path: str):
        self.path = path
        self.content = None

    def read(self) -> str:
        with open(self.path) as f:
            self.content = f.read()
        return self.content


class NetworkClient:
    """Handles network operations."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        self.connected = True
'''

    b_code = '''\
from pathlib import Path

CONFIG = {"debug": True, "verbose": True}

PLUGINS = ["metrics", "cache"]


def write(self, data: str) -> int:
    """Orphan method - accesses self.path and self.content -> FileHandler."""
    with open(self.path, "w") as f:
        f.write(data)
    self.content = data
    return len(data)


def disconnect(self) -> None:
    """Orphan method - accesses self.connected and self.host -> NetworkClient."""
    if self.connected:
        print(f"Disconnecting from {self.host}")
        self.connected = False
'''

    print("=" * 70)
    print("EXAMPLE 1: Smart chooser based on attribute analysis")
    print("=" * 70)
    
    # Debug: show what's being detected
    _, _, a_defs, _ = _collect_module(a_code)
    _, _, b_defs, b_orphans = _collect_module(b_code)
    
    print("\nClass attributes detected:")
    for cls_name, attrs in a_defs.class_attributes.items():
        print(f"  {cls_name}: {attrs}")
    
    print("\nOrphan methods and their self.* accesses:")
    for orphan in b_orphans:
        print(f"  {orphan.name}: {orphan.accessed_attrs}")
    
    print("\nMODULE A:")
    print(a_code)
    print("\nMODULE B:")
    print(b_code)
    print("\nMERGED (no chooser - uses smart matching):")
    print(merge_modules(a_code, b_code))

    # Example 2: Full replacement
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Full replacement (B has __all__ and __author__)")
    print("=" * 70)

    a_old = '''\
def old_func():
    pass

class OldClass:
    pass
'''

    b_new = '''\
"""New module that replaces the old one."""

__all__ = ["new_func", "NewClass"]
__author__ = "Claude"


def new_func():
    return "I'm new!"


class NewClass:
    def method(self):
        return "New class method"
'''

    print("\nMODULE A (old):")
    print(a_old)
    print("\nMODULE B (new with __all__ and __author__):")
    print(b_new)
    print("\nRESULT (full replacement):")
    print(merge_modules(a_old, b_new))
