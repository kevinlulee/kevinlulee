from __future__ import annotations
import kevinlulee as kx

import libcst as cst

def transform_code(source: str, *transformers) -> str:
    module = cst.parse_module(source)

    for transformer in transformers:
        wrapper = cst.MetadataWrapper(module)
        module = wrapper.visit(transformer)

    return module.code


"""
LibCST helper for building CST expressions from template patterns.

Converts patterns like 'self.<name> = {abc = <value>}' into appropriate CST nodes,
with smart coercion of values based on context.
"""

import libcst as cst
import re
from typing import Any, Union, Callable, Dict


def coerce_to_cst(value: Any, context: str = "value") -> cst.BaseExpression:
    """
    Smartly coerce a Python value into the appropriate CST expression.
    
    Args:
        value: The value to coerce (str, int, float, bool, None, dict, list, or cst node)
        context: Hint about the context ("name", "attr", "value")
    
    Returns:
        Appropriate CST expression node
    """
    if isinstance(value, cst.BaseExpression):
        return value
    
    if value is None:
        return cst.Name("None")
    
    if isinstance(value, bool):
        return cst.Name("True" if value else "False")
    
    if isinstance(value, int):
        if value < 0:
            return cst.UnaryOperation(
                operator=cst.Minus(),
                expression=cst.Integer(str(abs(value)))
            )
        return cst.Integer(str(value))
    
    if isinstance(value, float):
        if value < 0:
            return cst.UnaryOperation(
                operator=cst.Minus(),
                expression=cst.Float(str(abs(value)))
            )
        return cst.Float(str(value))
    
    if isinstance(value, str):
        if context in ("name", "attr"):
            return cst.Name(value)
        return cst.SimpleString(repr(value))
    
    if isinstance(value, list):
        return cst.List(
            elements=[
                cst.Element(value=coerce_to_cst(item, "value"))
                for item in value
            ]
        )
    
    if isinstance(value, tuple):
        return cst.Tuple(
            elements=[
                cst.Element(value=coerce_to_cst(item, "value"))
                for item in value
            ]
        )
    
    if isinstance(value, dict):
        return cst.Dict(
            elements=[
                cst.DictElement(
                    key=coerce_to_cst(k, "value"),
                    value=coerce_to_cst(v, "value")
                )
                for k, v in value.items()
            ]
        )
    
    if isinstance(value, set):
        return cst.Set(
            elements=[
                cst.Element(value=coerce_to_cst(item, "value"))
                for item in value
            ]
        )
    
    return cst.Name(str(value))


def build_name(name: str) -> cst.Name:
    """Build a CST Name node."""
    return cst.Name(name)


def build_attribute(obj: Union[str, cst.BaseExpression], attr: str) -> cst.Attribute:
    """
    Build a CST Attribute node (e.g., self.foo).
    
    Args:
        obj: The object (e.g., "self" or a CST expression)
        attr: The attribute name
    """
    if isinstance(obj, str):
        obj = cst.Name(obj)
    return cst.Attribute(value=obj, attr=cst.Name(attr))


def build_self_attr(name: str) -> cst.Attribute:
    """Build self.<name> attribute access."""
    return cst.Attribute(
        value=cst.Name("self"),
        attr=cst.Name(name)
    )


def build_assign(target: Union[str, cst.BaseAssignTargetExpression], 
                 value: Any) -> cst.Assign:
    """
    Build a CST Assign node.
    
    Args:
        target: Assignment target (string for simple name, or CST node)
        value: Value to assign (will be coerced)
    """
    if isinstance(target, str):
        target = cst.Name(target)
    
    return cst.Assign(
        targets=[cst.AssignTarget(target=target)],
        value=coerce_to_cst(value, "value")
    )


def build_self_assign(name: str, value: Any) -> cst.SimpleStatementLine:
    """
    Build self.<name> = <value> as a statement line.
    
    Args:
        name: Attribute name
        value: Value to assign (will be smartly coerced)
    
    Returns:
        CST SimpleStatementLine containing the assignment
    """
    return cst.SimpleStatementLine(
        body=[
            cst.Assign(
                targets=[
                    cst.AssignTarget(
                        target=cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(name)
                        )
                    )
                ],
                value=coerce_to_cst(value, "value")
            )
        ]
    )


def build_self_assign_dict(name: str, **kwargs: Any) -> cst.SimpleStatementLine:
    """
    Build self.<name> = {key1=value1, key2=value2, ...} as a statement line.
    
    Args:
        name: Attribute name
        **kwargs: Key-value pairs for the dict
    
    Returns:
        CST SimpleStatementLine containing the assignment
    """
    return cst.SimpleStatementLine(
        body=[
            cst.Assign(
                targets=[
                    cst.AssignTarget(
                        target=cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(name)
                        )
                    )
                ],
                value=cst.Dict(
                    elements=[
                        cst.DictElement(
                            key=coerce_to_cst(k, "value"),
                            value=coerce_to_cst(v, "value")
                        )
                        for k, v in kwargs.items()
                    ]
                )
            )
        ]
    )


def build_call(func: Union[str, cst.BaseExpression], 
               *args: Any, 
               **kwargs: Any) -> cst.Call:
    """
    Build a function call.
    
    Args:
        func: Function name or expression
        *args: Positional arguments (will be coerced)
        **kwargs: Keyword arguments (will be coerced)
    """
    if isinstance(func, str):
        func = cst.Name(func)
    
    call_args = []
    for arg in args:
        call_args.append(cst.Arg(value=coerce_to_cst(arg, "value")))
    
    for key, val in kwargs.items():
        call_args.append(
            cst.Arg(
                keyword=cst.Name(key),
                value=coerce_to_cst(val, "value")
            )
        )
    
    return cst.Call(func=func, args=call_args)


def build_method_call(obj: Union[str, cst.BaseExpression],
                      method: str,
                      *args: Any,
                      **kwargs: Any) -> cst.Call:
    """
    Build a method call (e.g., self.method(args)).
    
    Args:
        obj: Object (e.g., "self")
        method: Method name
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    if isinstance(obj, str):
        obj = cst.Name(obj)
    
    return build_call(
        cst.Attribute(value=obj, attr=cst.Name(method)),
        *args,
        **kwargs
    )


class CSTBuilder:
    """
    Fluent builder for constructing CST nodes.
    
    Example:
        builder = CSTBuilder()
        node = builder.self_assign("config", {"abc": "value", "num": 42})
    """
    
    def __init__(self):
        pass
    
    def name(self, n: str) -> cst.Name:
        return build_name(n)
    
    def attr(self, obj: Union[str, cst.BaseExpression], attr: str) -> cst.Attribute:
        return build_attribute(obj, attr)
    
    def self_attr(self, name: str) -> cst.Attribute:
        return build_self_attr(name)
    
    def assign(self, target: Union[str, cst.BaseAssignTargetExpression], 
               value: Any) -> cst.Assign:
        return build_assign(target, value)
    
    def self_assign(self, name: str, value: Any) -> cst.SimpleStatementLine:
        return build_self_assign(name, value)
    
    def self_assign_dict(self, name: str, **kwargs: Any) -> cst.SimpleStatementLine:
        return build_self_assign_dict(name, **kwargs)
    
    def call(self, func: Union[str, cst.BaseExpression], 
             *args: Any, **kwargs: Any) -> cst.Call:
        return build_call(func, *args, **kwargs)
    
    def method_call(self, obj: Union[str, cst.BaseExpression],
                    method: str, *args: Any, **kwargs: Any) -> cst.Call:
        return build_method_call(obj, method, *args, **kwargs)
    
    def coerce(self, value: Any, context: str = "value") -> cst.BaseExpression:
        return coerce_to_cst(value, context)
    
    def statement(self, expr: cst.BaseSmallStatement) -> cst.SimpleStatementLine:
        """Wrap an expression/statement in a SimpleStatementLine."""
        return cst.SimpleStatementLine(body=[expr])


def to_code(node: Union[cst.BaseStatement, cst.BaseExpression, cst.CSTNode]) -> str:
    """Convert a CST node to source code string."""
    if isinstance(node, cst.BaseExpression):
        node = cst.SimpleStatementLine(body=[cst.Expr(node)])
    if isinstance(node, (cst.BaseStatement, cst.BaseSmallStatement)):
        if isinstance(node, cst.BaseSmallStatement):
            node = cst.SimpleStatementLine(body=[node])
        return cst.Module(body=[node]).code.strip()
    return cst.Module(body=[node]).code.strip()


def cst_template(template: str) -> Callable[..., cst.CSTNode]:
    """
    Create a CST builder function from a template string.
    
    Placeholders are marked with <name> and become keyword arguments.
    Context is inferred from position:
      - After 'self.' or before '.' → name context
      - After '=' → value context
    
    Args:
        template: Template string like 'self.<name> = <value>'
    
    Returns:
        A function that takes placeholder values and returns CST node
    
    Example:
        builder = cst_template('self.<name> = <value>')
        node = builder(name='config', value={'a': 1})
        print(to_code(node))  # self.config = {"a": 1}
    """
    placeholder_pattern = re.compile(r'<(\w+)>')
    placeholders = placeholder_pattern.findall(template)
    
    def build(**kwargs: Any) -> cst.CSTNode:
        missing = set(placeholders) - set(kwargs.keys())
        if missing:
            raise TypeError(f"Missing required arguments: {missing}")
        
        filled = template
        for name in placeholders:
            filled = filled.replace(f'<{name}>', f'__PLACEHOLDER_{name}__')
        
        try:
            parsed = cst.parse_statement(filled)
        except Exception:
            try:
                parsed = cst.parse_expression(filled)
            except Exception:
                parsed = cst.parse_module(filled)
        
        class PlaceholderReplacer(cst.CSTTransformer):
            def __init__(self, values: Dict[str, Any]):
                self.values = values
                super().__init__()
            
            def leave_Name(self, original: cst.Name, updated: cst.Name) -> cst.BaseExpression:
                for name, val in self.values.items():
                    if updated.value == f'__PLACEHOLDER_{name}__':
                        ctx = _infer_context(template, name)
                        return coerce_to_cst(val, ctx)
                return updated
        
        return parsed.visit(PlaceholderReplacer(kwargs))
    
    build.__doc__ = f"Build CST from template: {template}\nArgs: {', '.join(placeholders)}"
    return build


def _infer_context(template: str, placeholder: str) -> str:
    """Infer the context of a placeholder from its position in the template."""
    pattern = f'<{placeholder}>'
    idx = template.find(pattern)
    if idx == -1:
        return "value"
    
    before = template[:idx].rstrip()
    after = template[idx + len(pattern):].lstrip()
    
    if before.endswith('self.'):
        return "name"
    if before.endswith('.'):
        return "attr"
    if after.startswith('.'):
        return "name"
    if after.startswith('('):
        return "name"
    
    return "value"



# Create a builder from template
if __name__ == '__main__':
    builder = cst_template('self.<name> = <value>')
    
    # Use it with arguments
    node = builder(name='config', value={'abc': 'hello', 'num': 42})
    print(to_code(node))
    # self.config = {"abc": "hello", "num": 42}
    
    # Another example
    call_builder = cst_template('<obj>.<method>(<arg>)')
    node = call_builder(obj='self', method='process', arg={'key': 'value'})
    print(to_code(node))
    # self.process({"key": "value"})
