"""
Mathematical Expression Parser

This module provides a parser for mathematical expressions that builds an abstract
syntax tree (AST) representation. It supports:

- Atomic values: integers, decimals, symbols (pi, e), variables, units
- Binary operations: arithmetic (+, -, *, /, ^), relations (=, !=, <, <=, >, >=)
- Unary operations: negation, functions (sqrt, sin, cos, etc.)
- Subscripts: x_i, a_2
- Mixed numbers: 3'1/4
- Grouping: parentheses
- Implicit multiplication: 2x, xy
- Function calls: max(x, y, z)

Example usage:
    >>> ast = parse("sqrt(x**2 + y**2)")
    >>> print(ast.to_str())
    sqrt(x**2 + y**2)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List
import re


@dataclass
class AtomicNode:
    """
    Represents atomic values in mathematical expressions.

    Attributes:
        kind: Type of atomic value ('integer', 'decimal', 'symbol', 'variable', 'unit')
        value: The actual value (int, float, or str)

    Examples:
        AtomicNode('integer', 42)        # The number 42
        AtomicNode('decimal', 3.14)      # The number 3.14
        AtomicNode('symbol', 'pi')       # Mathematical constant π
        AtomicNode('variable', 'x')      # Variable x
        AtomicNode('unit', 'meters')     # Unit meters
    """

    kind: str
    value: Union[int, float, str]

    def to_str(self) -> str:
        """Convert the atomic node to its string representation."""
        return str(self.value)


@dataclass
class SubscriptNode:
    """
    Represents subscripted expressions.

    Attributes:
        kind: Always 'subscript'
        base: The base expression being subscripted
        subscript: The subscript value (must be variable or integer)

    Examples:
        x_i, a_2, alpha_n
    """

    kind: str = "subscript"
    base: ExpressionNode = None
    subscript: Union[AtomicNode, None] = None

    def to_str(self) -> str:
        """Convert the subscript node to its string representation."""
        return f"{self.base.to_str()}_{self.subscript.to_str()}"


@dataclass
class MixedNumberNode:
    """
    Represents mixed numbers (whole number with fraction).

    Attributes:
        kind: Always 'mixed_number'
        whole: The whole number part
        numerator: The fraction's numerator
        denominator: The fraction's denominator

    Examples:
        3'1/4 represents 3 and 1/4
        2'3/8 represents 2 and 3/8
    """

    kind: str = "mixed_number"
    whole: int = 0
    numerator: int = 0
    denominator: int = 0

    def to_str(self) -> str:
        """Convert the mixed number to its string representation."""
        return f"{self.whole}'{self.numerator}/{self.denominator}"


@dataclass
class BinaryNode:
    """
    Represents binary operations.

    Attributes:
        kind: Type of binary operation:
            Arithmetic: 'addition', 'subtraction', 'implicit_multiplication',
                       'dot_multiplication', 'cross_multiplication',
                       'fraction_division', 'explicit_division', 'exponent'
            Relations: 'equal', 'not_equal', 'less_than', 'less_equal',
                      'greater_than', 'greater_equal'
        left: Left operand expression
        right: Right operand expression

    Examples:
        BinaryNode('addition', x, y)              # x + y
        BinaryNode('implicit_multiplication', 2, x) # 2x
        BinaryNode('equal', x, 5)                 # x = 5
    """

    kind: str
    left: ExpressionNode = None
    right: ExpressionNode = None

    def get_operator_str(self) -> str:
        """Return the string representation of the operator."""
        op_map = {
            "addition": " + ",
            "subtraction": " - ",
            "implicit_multiplication": "",
            "dot_multiplication": " * ",
            "cross_multiplication": " times ",
            "fraction_division": " / ",
            "explicit_division": " div ",
            "exponent": "**",
            "equal": " = ",
            "not_equal": " != ",
            "less_than": " < ",
            "less_equal": " <= ",
            "greater_than": " > ",
            "greater_equal": " >= ",
        }
        return op_map.get(self.kind, " ? ")

    def get_precedence(self) -> int:
        """
        Return the precedence level of this operator.

        Higher numbers bind more tightly.
        Precedence levels:
            0: Relations (=, !=, <, <=, >, >=)
            1: Addition, Subtraction
            2: Multiplication, Division
            3: Exponentiation
        """
        precedence_map = {
            "equal": 0,
            "not_equal": 0,
            "less_than": 0,
            "less_equal": 0,
            "greater_than": 0,
            "greater_equal": 0,
            "addition": 1,
            "subtraction": 1,
            "implicit_multiplication": 2,
            "dot_multiplication": 2,
            "cross_multiplication": 2,
            "fraction_division": 2,
            "explicit_division": 2,
            "exponent": 3,
        }
        return precedence_map.get(self.kind, 0)

    def is_right_associative(self) -> bool:
        """Return True if operator is right-associative."""
        return self.kind == "exponent"

    def to_str(self) -> str:
        """Convert the binary node to its string representation."""
        left_str = self.left.to_str()
        right_str = self.right.to_str()
        return f"{left_str}{self.get_operator_str()}{right_str}"


@dataclass
class UnaryNode:
    """
    Represents unary operations.

    Attributes:
        kind: Type of operation ('negation' or function names like 'sqrt', 'sin')
        operand: The expression being operated on

    Examples:
        UnaryNode('negation', x)    # -x
        UnaryNode('sqrt', expr)     # sqrt(expr)
        UnaryNode('sin', x)         # sin(x)
    """

    kind: str
    operand: ExpressionNode = None

    def to_str(self) -> str:
        """Convert the unary node to its string representation."""
        if self.kind == "negation":
            operand_str = self.operand.to_str()
            if isinstance(self.operand, BinaryNode):
                operand_str = f"({operand_str})"
            return f"-{operand_str}"
        return f"{self.kind}({self.operand.to_str()})"


@dataclass
class FunctionNode:
    """
    Represents function calls with multiple arguments.

    Attributes:
        kind: Always 'function'
        name: Name of the function
        args: List of argument expressions

    Examples:
        FunctionNode('max', [x, y, z])    # max(x, y, z)
        FunctionNode('gcd', [a, b])       # gcd(a, b)
    """

    kind: str = "function"
    name: str = ""
    args: List[ExpressionNode] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []

    def to_str(self) -> str:
        """Convert the function node to its string representation."""
        args_str = ", ".join(arg.to_str() for arg in self.args)
        return f"{self.name}({args_str})"


@dataclass
class GroupNode:
    """
    Represents parenthesized expressions.

    Attributes:
        kind: Always 'group'
        expr: The expression inside parentheses
        explicit_parentheses: True if double parens or semantically unnecessary

    Examples:
        GroupNode(expr, False)    # (expr) - normal grouping
        GroupNode(expr, True)     # ((expr)) - explicit double parens
    """

    kind: str = "group"
    expr: ExpressionNode = None
    explicit_parentheses: bool = False

    def to_str(self) -> str:
        """Convert the group node to its string representation."""
        inner = self.expr.to_str()
        if self.explicit_parentheses:
            return f"(({inner}))"
        return f"({inner})"


ExpressionNode = Union[
    AtomicNode,
    SubscriptNode,
    MixedNumberNode,
    BinaryNode,
    UnaryNode,
    FunctionNode,
    GroupNode,
]


@dataclass
class Token:
    """
    Represents a lexical token from the input.

    Attributes:
        kind: Type of token (e.g., 'INTEGER', 'VAR', 'PLUS')
        value: The actual text value
        has_leading_whitespace: Whether whitespace preceded this token
    """

    kind: str
    value: str
    has_leading_whitespace: bool = False


def needs_parens(
    parent: BinaryNode, child: ExpressionNode, is_left: bool
) -> bool:
    """
    Determine if a child expression needs parentheses when used in a binary operation.

    Args:
        parent: The parent binary operation
        child: The child expression being considered
        is_left: True if child is the left operand, False if right

    Returns:
        True if parentheses are needed around the child expression

    This function implements precedence and associativity rules to minimize
    unnecessary parentheses while maintaining correctness.
    """
    if not isinstance(child, BinaryNode):
        return False

    parent_prec = parent.get_precedence()
    child_prec = child.get_precedence()

    # Special case: if both are implicit multiplication, no parens needed
    if (
        parent.kind == "implicit_multiplication"
        and child.kind == "implicit_multiplication"
    ):
        return False

    # Lower precedence always needs parens
    if child_prec < parent_prec:
        return True

    # Same precedence on the right side of left-associative operator needs parens
    if (
        child_prec == parent_prec
        and not is_left
        and not parent.is_right_associative()
    ):
        return True

    return False


def wrap_if_needed(
    parent: BinaryNode, child: ExpressionNode, is_left: bool
) -> ExpressionNode:
    """
    Wrap a child expression in a GroupNode if parentheses are needed.

    Args:
        parent: The parent binary operation
        child: The child expression
        is_left: True if child is the left operand

    Returns:
        Either the original child or a GroupNode wrapping it
    """
    if needs_parens(parent, child, is_left):
        return GroupNode(expr=child, explicit_parentheses=False)
    return child


class MathParser:
    """
    Recursive descent parser for mathematical expressions.

    The parser uses the following precedence hierarchy (lowest to highest):
        1. Relations (=, !=, <, <=, >, >=)
        2. Addition, Subtraction
        3. Multiplication, Division
        4. Exponentiation
        5. Unary operations (negation, functions)
        6. Subscripts
        7. Primary expressions (atoms, groups)

    Attributes:
        text: The input string to parse
        tokens: List of tokens from lexical analysis
        token_pos: Current position in token list
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens: List[Token] = []
        self.token_pos = 0

    def parse(self) -> ExpressionNode:
        """
        Parse the input text and return an AST.

        Returns:
            The root node of the abstract syntax tree
        """
        self.tokenize()
        result = self.parse_expression()
        return result

    def tokenize(self) -> None:
        """
        Convert input string into tokens, tracking whitespace.

        This method performs lexical analysis, breaking the input into
        meaningful tokens while preserving information about whitespace
        (used for distinguishing implicit multiplication from units).
        """
        patterns = [
            ("MIXED_NUM", r"\d+\'\d+/\d+"),
            ("DECIMAL", r"\d+\.\d+"),
            ("INTEGER", r"\d+"),
            ("SYMBOL", r"pi|e"),
            ("GREEK", r"alpha|beta|gamma|delta|theta|sigma|omega|Delta"),
            ("NOT_EQUAL", r"!="),
            ("LESS_EQUAL", r"<="),
            ("GREATER_EQUAL", r">="),
            ("EQUAL", r"="),
            ("LESS", r"<"),
            ("GREATER", r">"),
            ("TIMES", r"times"),
            ("DIV_OP", r"div"),
            ("WORD", r"sqrt|cbrt|sin|cos|tan|abs"),
            ("VAR", r"[a-zA-Z]+"),
            ("POW", r"\*\*|\^"),
            ("MULT", r"\*"),
            ("PLUS", r"\+"),
            ("MINUS", r"-"),
            ("SLASH", r"/"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("UNDERSCORE", r"_"),
            ("COMMA", r","),
            ("WS", r"\s+"),
        ]

        token_re = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in patterns
        )

        last_was_ws = False
        for match in re.finditer(token_re, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == "WS":
                last_was_ws = True
                continue

            token = Token(kind, value, has_leading_whitespace=last_was_ws)
            self.tokens.append(token)
            last_was_ws = False

    def peek(self, offset: int = 0) -> Token | None:
        """Look at token without consuming it."""
        pos = self.token_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def consume(self) -> Token | None:
        """Consume and return current token."""
        if self.token_pos < len(self.tokens):
            token = self.tokens[self.token_pos]
            self.token_pos += 1
            return token
        return None

    def parse_expression(self) -> ExpressionNode:
        """Parse full expression (starts with relations)."""
        return self.parse_relational()

    def parse_relational(self) -> ExpressionNode:
        """Parse relational operators (=, !=, <, <=, >, >=)."""
        left = self.parse_additive()

        while True:
            token = self.peek()
            if token and token.kind in [
                "EQUAL",
                "NOT_EQUAL",
                "LESS",
                "LESS_EQUAL",
                "GREATER",
                "GREATER_EQUAL",
            ]:
                op_token = self.consume()
                right = self.parse_additive()

                kind_map = {
                    "EQUAL": "equal",
                    "NOT_EQUAL": "not_equal",
                    "LESS": "less_than",
                    "LESS_EQUAL": "less_equal",
                    "GREATER": "greater_than",
                    "GREATER_EQUAL": "greater_equal",
                }

                node = BinaryNode(
                    kind=kind_map[op_token.kind], left=None, right=None
                )
                left = BinaryNode(
                    kind=node.kind,
                    left=wrap_if_needed(node, left, True),
                    right=wrap_if_needed(node, right, False),
                )
            else:
                break

        return left

    def parse_additive(self) -> ExpressionNode:
        """Parse addition and subtraction."""
        left = self.parse_multiplicative()

        while True:
            token = self.peek()
            if token and token.kind in ["PLUS", "MINUS"]:
                op_token = self.consume()
                right = self.parse_multiplicative()
                kind = "addition" if op_token.kind == "PLUS" else "subtraction"

                node = BinaryNode(kind=kind, left=None, right=None)
                left = BinaryNode(
                    kind=kind,
                    left=wrap_if_needed(node, left, True),
                    right=wrap_if_needed(node, right, False),
                )
            else:
                break

        return left

    def parse_multiplicative(self) -> ExpressionNode:
        """Parse multiplication and division."""
        left = self.parse_power()

        while True:
            token = self.peek()

            # Explicit operators
            if token and token.kind in ["MULT", "SLASH", "DIV_OP", "TIMES"]:
                op_token = self.consume()
                right = self.parse_power()

                kind_map = {
                    "MULT": "dot_multiplication",
                    "TIMES": "cross_multiplication",
                    "DIV_OP": "explicit_division",
                    "SLASH": "fraction_division",
                }

                node = BinaryNode(
                    kind=kind_map[op_token.kind], left=None, right=None
                )
                left = BinaryNode(
                    kind=node.kind,
                    left=wrap_if_needed(node, left, True),
                    right=wrap_if_needed(node, right, False),
                )
            # Implicit multiplication
            elif token and self._is_implicit_mult(left, token):
                right = self.parse_power()
                node = BinaryNode(
                    kind="implicit_multiplication", left=None, right=None
                )
                left = BinaryNode(
                    kind="implicit_multiplication",
                    left=wrap_if_needed(node, left, True),
                    right=wrap_if_needed(node, right, False),
                )
            else:
                break

        return left

    def _is_implicit_mult(
        self, left_expr: ExpressionNode, next_token: Token
    ) -> bool:
        """Check if implicit multiplication should occur."""
        if next_token.kind in [
            "VAR",
            "GREEK",
            "SYMBOL",
            "LPAREN",
            "WORD",
            "INTEGER",
            "DECIMAL",
        ]:
            if next_token.kind == "WORD" and next_token.value not in [
                "sqrt",
                "cbrt",
                "sin",
                "cos",
                "tan",
                "abs",
            ]:
                return False
            return True
        return False

    def parse_power(self) -> ExpressionNode:
        """Parse exponentiation (right-associative)."""
        left = self.parse_subscript()

        token = self.peek()
        if token and token.kind == "POW":
            self.consume()
            right = self.parse_power()  # Right associative

            node = BinaryNode(kind="exponent", left=None, right=None)
            return BinaryNode(
                kind="exponent",
                left=wrap_if_needed(node, left, True),
                right=wrap_if_needed(node, right, False),
            )

        return left

    def parse_subscript(self) -> ExpressionNode:
        """Parse subscripts (e.g., x_i, a_2)."""
        base = self.parse_unary()

        token = self.peek()
        if token and token.kind == "UNDERSCORE":
            self.consume()
            subscript = self.parse_primary()

            # Validate that subscript is only variable or integer
            if not isinstance(subscript, AtomicNode) or subscript.kind not in [
                "variable",
                "integer",
            ]:
                raise ValueError(
                    f"Subscript must be a variable or integer, got {subscript}"
                )

            return SubscriptNode(base=base, subscript=subscript)

        return base

    def parse_unary(self) -> ExpressionNode:
        """Parse unary operators (negation, functions)."""
        token = self.peek()

        if token and token.kind == "MINUS":
            self.consume()
            operand = self.parse_unary()
            return UnaryNode(kind="negation", operand=operand)

        return self.parse_primary()

    def parse_primary(self) -> ExpressionNode:
        """Parse primary expressions (atoms, groups, functions)."""
        token = self.peek()

        if not token:
            raise ValueError("Unexpected end of expression")

        # Mixed number
        if token.kind == "MIXED_NUM":
            return self.parse_mixed_number()

        # Decimal - check for unit pattern (e.g., "2.5 liters")
        if token.kind == "DECIMAL":
            self.consume()
            decimal_val = float(token.value)

            # Check if next token is a multi-letter VAR with leading whitespace (unit pattern)
            next_token = self.peek()
            if (
                next_token
                and next_token.kind == "VAR"
                and next_token.has_leading_whitespace
                and len(next_token.value) > 1
            ):
                # This is a unit pattern
                var_token = self.consume()
                unit = AtomicNode(kind="unit", value=var_token.value)
                node = BinaryNode(
                    kind="implicit_multiplication", left=None, right=None
                )
                return BinaryNode(
                    kind="implicit_multiplication",
                    left=AtomicNode(kind="decimal", value=decimal_val),
                    right=unit,
                )

            return AtomicNode(kind="decimal", value=decimal_val)

        # Integer - check for unit pattern (e.g., "5 grapes")
        if token.kind == "INTEGER":
            self.consume()
            int_val = int(token.value)

            # Check if next token is a multi-letter VAR with leading whitespace (unit pattern)
            next_token = self.peek()
            if (
                next_token
                and next_token.kind == "VAR"
                and next_token.has_leading_whitespace
                and len(next_token.value) > 1
            ):
                # This is a unit pattern
                var_token = self.consume()
                unit = AtomicNode(kind="unit", value=var_token.value)
                node = BinaryNode(
                    kind="implicit_multiplication", left=None, right=None
                )
                return BinaryNode(
                    kind="implicit_multiplication",
                    left=AtomicNode(kind="integer", value=int_val),
                    right=unit,
                )

            return AtomicNode(kind="integer", value=int_val)

        # Symbol (pi, e)
        if token.kind == "SYMBOL":
            self.consume()
            return AtomicNode(kind="symbol", value=token.value)

        # Greek letters
        if token.kind == "GREEK":
            self.consume()
            return AtomicNode(kind="variable", value=token.value)

        # Variable - need to handle implicit multiplication
        if token.kind == "VAR":
            var_token = self.consume()
            var_name = var_token.value

            # If no leading whitespace and multiple chars, split into individual vars
            if len(var_name) > 1 and not var_token.has_leading_whitespace:
                # Split into individual variables with implicit multiplication
                result = AtomicNode(kind="variable", value=var_name[0])
                for char in var_name[1:]:
                    node = BinaryNode(
                        kind="implicit_multiplication", left=None, right=None
                    )
                    result = BinaryNode(
                        kind="implicit_multiplication",
                        left=result,
                        right=AtomicNode(kind="variable", value=char),
                    )
                return result
            else:
                # Single char or has leading whitespace
                return AtomicNode(kind="variable", value=var_name)

        # Function
        if token.kind == "WORD" and token.value in [
            "sqrt",
            "cbrt",
            "sin",
            "cos",
            "tan",
            "abs",
        ]:
            return self.parse_function()

        # Parentheses
        if token.kind == "LPAREN":
            return self.parse_group()

        raise ValueError(f"Unexpected token: {token}")

    def parse_mixed_number(self) -> MixedNumberNode:
        """Parse mixed numbers like 3'1/4."""
        token = self.consume()
        match = re.match(r"(\d+)\'(\d+)/(\d+)", token.value)
        whole = int(match.group(1))
        num = int(match.group(2))
        den = int(match.group(3))
        return MixedNumberNode(whole=whole, numerator=num, denominator=den)

    def parse_function(self) -> FunctionNode:
        """Parse function calls."""
        name_token = self.consume()
        name = name_token.value

        # Expect opening parenthesis
        if not self.peek() or self.peek().kind != "LPAREN":
            raise ValueError(f"Expected '(' after function {name}")

        self.consume()  # consume '('

        args = []
        while True:
            args.append(self.parse_additive())

            if self.peek() and self.peek().kind == "COMMA":
                self.consume()
            else:
                break

        if not self.peek() or self.peek().kind != "RPAREN":
            raise ValueError(f"Expected ')' after function arguments")

        self.consume()  # consume ')'

        return FunctionNode(name=name, args=args)

    def parse_group(self) -> ExpressionNode:
        """Parse parenthesized expressions."""
        self.consume()  # consume first '('

        # Check for double parentheses
        if self.peek() and self.peek().kind == "LPAREN":
            saved_pos = self.token_pos
            self.consume()  # tentatively consume second '('

            try:
                inner_expr = self.parse_additive()

                # Check if next is ')' and after that is ')'
                if (
                    self.peek()
                    and self.peek().kind == "RPAREN"
                    and self.peek(1)
                    and self.peek(1).kind == "RPAREN"
                ):
                    # This is double parentheses!
                    self.consume()  # consume first ')'
                    self.consume()  # consume second ')'
                    return GroupNode(expr=inner_expr, explicit_parentheses=True)
                else:
                    # Not double parens, backtrack
                    self.token_pos = saved_pos
            except:
                # Error parsing, backtrack
                self.token_pos = saved_pos

        # Normal parentheses parsing
        expr = self.parse_additive()

        if not self.peek() or self.peek().kind != "RPAREN":
            raise ValueError("Expected ')'")

        self.consume()  # consume ')'

        return GroupNode(expr=expr, explicit_parentheses=False)


def parse(text: str) -> ExpressionNode:
    """
    Parse a mathematical expression string into an AST.

    Args:    
        text: The mathematical expression to parse

    Returns: The root node of the abstract syntax tree
    Raises:  ValueError: If the expression is malformed

    Examples:
        >>> ast = parse("2x + 3")
        >>> ast.to_str()
        '2x + 3'

        >>> ast = parse("x**2 + y**2 = r**2")
        >>> ast.to_str()
        'x**2 + y**2 = r**2'
    """
    parser = MathParser(text)
    return parser.parse()


__all__ = [
    "AtomicNode",
    "SubscriptNode",
    "MixedNumberNode",
    "BinaryNode",
    "UnaryNode",
    "FunctionNode",
    "GroupNode",
    "ExpressionNode",
    "parse",
]
