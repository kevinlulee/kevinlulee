from treebloom.utils.node_ops import get_root_node_from_source, get_node_text


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
    root = get_root_node_from_source(source)
    
    replacements = []
    
    for child in root.children:
        if child.type == "expression_statement":
            expr = child.children[0] if child.children else None
            if expr is None:
                continue
            
            should_wrap = False
            
            if expr.type == "string":
                should_wrap = True
            elif expr.type == "call":
                # Check if it's already a self.* call
                func = expr.child_by_field_name("function")
                if func and func.type == "attribute":
                    obj = func.child_by_field_name("object")
                    if obj and get_node_text(obj, source) == "self":
                        should_wrap = False
                    else:
                        should_wrap = True
                else:
                    should_wrap = True
            
            if should_wrap:
                original_text = get_node_text(expr, source)
                wrapped_text = f"{wrapper}({original_text})"
                replacements.append((expr.start_byte, expr.end_byte, wrapped_text))
    
    # Apply replacements in reverse order to preserve byte offsets
    result = source
    for start, end, new_text in reversed(replacements):
        result = result[:start] + new_text + result[end:]
    
    return result


# Example 1: Original example
source1 = """a = 1
# comments
Rectangle()
'a string'
foo = 1"""

print("Example 1:")
print(wrap_top_level_expressions(source1))
print()

# Example 2: Already has self.add
source2 = """self.add(Circle())
Rectangle('')
self.play(Animation())"""

print("Example 2:")
print(wrap_top_level_expressions(source2))
print()

# Example 3: Custom wrapper
source3 = """Text('hello')

42

  "another string" """

print("Example 3 (custom wrapper):")
print(wrap_top_level_expressions(source3, wrapper="scene.add"))

