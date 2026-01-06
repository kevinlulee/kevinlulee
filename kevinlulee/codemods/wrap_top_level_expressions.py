import libcst as cst
from libcst import matchers as m
from kevinlulee.extras.libcst import transform_code


class WrapTopLevelExpressions(cst.CSTTransformer):
    """
    Wrap top-level calls and string literals with a wrapper function.
    
    Skips:
    - Assignments (e.g., a = 1)
    - Comments
    - Expressions that are already self.<something> calls
    
    Wraps:
    - Standalone function calls (e.g., Rectangle())
    - Standalone string literals (e.g., 'a string')
    """

    def __init__(self, wrapper: str = "self.add"):
        super().__init__()
        self.wrapper = wrapper
        self._wrapper_node = self._parse_wrapper(wrapper)

    def _parse_wrapper(self, wrapper: str) -> cst.BaseExpression:
        """Parse the wrapper string into a CST node."""
        parts = wrapper.split(".")
        if len(parts) == 1:
            return cst.Name(parts[0])
        
        result = cst.Name(parts[0])
        for part in parts[1:]:
            result = cst.Attribute(value=result, attr=cst.Name(part))
        return result

    def _is_self_call(self, node: cst.Call) -> bool:
        """Check if a call is already a self.* call."""
        if isinstance(node.func, cst.Attribute):
            if isinstance(node.func.value, cst.Name):
                return node.func.value.value == "self"
        return False

    def _should_wrap(self, expr: cst.BaseExpression) -> bool:
        """Determine if an expression should be wrapped."""
        if isinstance(expr, (cst.SimpleString, cst.ConcatenatedString, cst.FormattedString)):
            return True
        
        if isinstance(expr, cst.Call):
            return not self._is_self_call(expr)
        
        return False

    def _wrap_expression(self, expr: cst.BaseExpression) -> cst.Call:
        """Wrap an expression with the wrapper function."""
        return cst.Call(
            func=self._wrapper_node,
            args=[cst.Arg(value=expr)],
        )

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        if len(updated_node.body) != 1:
            return updated_node
        
        stmt = updated_node.body[0]
        
        if not isinstance(stmt, cst.Expr):
            return updated_node
        
        expr = stmt.value
        
        if self._should_wrap(expr):
            wrapped = self._wrap_expression(expr)
            new_stmt = stmt.with_changes(value=wrapped)
            return updated_node.with_changes(body=[new_stmt])
        
        return updated_node


def wrap_top_level_expressions(source: str, wrapper: str = "self.add") -> str:
    """
    Wrap top-level calls and string literals with a wrapper function.
    
    Skips:
    - Assignments (e.g., a = 1)
    - Comments
    - Expressions that are already self.<something> calls
    
    Wraps:
    - Standalone function calls (e.g., Rectangle())
    - Standalone string literals (e.g., 'a string')
    """
    return transform_code(source, WrapTopLevelExpressions(wrapper = wrapper))






if __name__ == "__main__":
    # Example 1: Original example
    source1 = """a = 1
# comments
Rectangle()
'a string'
foo = 1"""
    print("Example 1:")
    print(wrap_top_level_expressions(source1))
    print()

# 2025-12-28 aicmp: print_statements should also be skipped
# if the things being wrapped has 'asset' in it, the wrapper should be self.section.add_asset
# we also ... it belongs together...
