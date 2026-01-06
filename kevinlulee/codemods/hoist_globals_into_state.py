import libcst as cst
from libcst import matchers as m
from libcst.metadata import ParentNodeProvider


class HoistGlobalsIntoState(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (ParentNodeProvider,)

    def __init__(self, transformer):
        self.new_assignments = []
        self.transformer = transformer

    def leave_Module(self, original_node, updated_node):
        return updated_node.with_changes(
            body=list(updated_node.body) + self.new_assignments
        )

    def leave_Assign(self, original_node, updated_node):
        # Get parent (SimpleStatementLine) and grandparent (Module)
        parent = self.get_metadata(ParentNodeProvider, original_node)
        if not isinstance(parent, cst.SimpleStatementLine):
            return updated_node
        
        grandparent = self.get_metadata(ParentNodeProvider, parent)
        if not isinstance(grandparent, cst.Module):
            return updated_node

        # Only handle simple: NAME = ...
        if (
            len(original_node.targets) != 1
            or not m.matches(original_node.targets[0].target, m.Name())
        ):
            return updated_node

        var_name = original_node.targets[0].target.value
        # only capture the uppercases
        if var_name != var_name.upper():
            return updated_node

        new_assignment = self.transformer (var_name)
        if new_assignment is None:
            return updated_node
        self.new_assignments.append(new_assignment)
        return updated_node


def transform_code(source: str) -> str:
    module = cst.parse_module(source)
    wrapper = cst.MetadataWrapper(module)
    transformer = HoistGlobalsIntoState()
    return wrapper.visit(transformer).code


