from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List
import re


@dataclass
class AtomicNode:
    """Represents atomic values: integers, decimals, symbols, variables, units."""
    kind: str  # 'integer', 'decimal', 'symbol', 'variable', 'unit'
    value: Union[int, float, str]

    def to_str(self) -> str:
        if self.kind == 'integer':
            return str(self.value)
        elif self.kind == 'decimal':
            return str(self.value)
        else:  # symbol, variable, unit
            return str(self.value)


@dataclass
class SubscriptNode:
    """Represents subscripted expressions like x_i or a_2."""
    kind: str = 'subscript'
    base: Expression = None
    subscript: Union[AtomicNode, None] = None  # Must be variable or integer

    def to_str(self) -> str:
        return f"{self.base.to_str()}_{self.subscript.to_str()}"


@dataclass
class MixedNumberNode:
    """Represents mixed numbers like 3'1/4."""
    kind: str = 'mixed_number'
    whole: int = 0
    numerator: int = 0
    denominator: int = 0

    def to_str(self) -> str:
        return f"{self.whole}'{self.numerator}/{self.denominator}"


@dataclass
class BinaryNode:
    """Represents binary operations."""
    kind: str  # 'addition', 'subtraction', 'implicit_multiplication', 'explicit_multiplication', 
               # 'times_multiplication', 'dot_multiplication', 'cross_multiplication', 
               # 'division', 'div_operation', 'exponent'
    left: Expression = None
    right: Expression = None

    def get_operator_str(self) -> str:
        """Return the string representation of the operator."""
        op_map = {
            'addition': ' + ',
            'subtraction': ' - ',
            'implicit_multiplication': '',
            'explicit_multiplication': ' * ',
            'times_multiplication': ' times ',
            'dot_multiplication': ' dot ',
            'cross_multiplication': ' cross ',
            'division': ' / ',
            'div_operation': ' div ',
            'exponent': '**',
        }
        return op_map.get(self.kind, ' ? ')

    def get_precedence(self) -> int:
        """Return the precedence level of this operator."""
        precedence_map = {
            'addition': 1,
            'subtraction': 1,
            'implicit_multiplication': 2,
            'explicit_multiplication': 2,
            'times_multiplication': 2,
            'dot_multiplication': 2,
            'cross_multiplication': 2,
            'division': 2,
            'div_operation': 2,
            'exponent': 3,
        }
        return precedence_map.get(self.kind, 0)

    def is_right_associative(self) -> bool:
        """Return True if operator is right-associative."""
        return self.kind == 'exponent'

    def to_str(self) -> str:
        left_str = self.left.to_str()
        right_str = self.right.to_str()

        # Add parentheses for complex expressions if needed
        if isinstance(self.left, BinaryNode) and self._needs_parens(self.left, True):
            left_str = f"({left_str})"
        if isinstance(self.right, BinaryNode) and self._needs_parens(self.right, False):
            right_str = f"({right_str})"

        return f"{left_str}{self.get_operator_str()}{right_str}"

    def _needs_parens(self, expr: BinaryNode, is_left: bool) -> bool:
        parent_prec = self.get_precedence()
        child_prec = expr.get_precedence()

        # Special case: if both are implicit multiplication, no parens needed
        if (self.kind == 'implicit_multiplication' and 
            expr.kind == 'implicit_multiplication'):
            return False

        if child_prec < parent_prec:
            return True
        if child_prec == parent_prec and not is_left and not self.is_right_associative():
            # Right operand needs parens for left-associative operators of same precedence
            return True
        return False


@dataclass
class UnaryNode:
    """Represents unary operations."""
    kind: str  # 'negation', or function names like 'sqrt', 'sin', etc.
    operand: Expression = None

    def to_str(self) -> str:
        if self.kind == 'negation':
            operand_str = self.operand.to_str()
            if isinstance(self.operand, BinaryNode):
                operand_str = f"({operand_str})"
            return f"-{operand_str}"
        return f"{self.kind}({self.operand.to_str()})"


@dataclass
class FunctionNode:
    """Represents function calls."""
    kind: str = 'function'
    name: str = ''
    args: List[Expression] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []

    def to_str(self) -> str:
        args_str = ', '.join(arg.to_str() for arg in self.args)
        return f"{self.name}({args_str})"


@dataclass
class GroupNode:
    """Represents parenthesized expressions."""
    kind: str = 'group'
    expr: Expression = None
    explicit_parentheses: bool = False  # True if double parens or unnecessary parens

    def to_str(self) -> str:
        inner = self.expr.to_str()
        if self.explicit_parentheses:
            return f"(({inner}))"
        return f"({inner})"


Expression = Union[AtomicNode, SubscriptNode, MixedNumberNode, BinaryNode, 
                   UnaryNode, FunctionNode, GroupNode]


@dataclass
class Token:
    kind: str
    value: str
    has_leading_whitespace: bool = False


class MathParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens: List[Token] = []
        self.token_pos = 0

    def parse(self) -> Expression:
        self.tokenize()
        result = self.parse_expression()
        return result

    def tokenize(self) -> None:
        """Convert input string into tokens, tracking whitespace."""
        patterns = [
            ('MIXED_NUM', r'\d+\'\d+/\d+'),
            ('DECIMAL', r'\d+\.\d+'),
            ('INTEGER', r'\d+'),
            ('SYMBOL', r'pi|e'),
            ('GREEK', r'alpha|beta|gamma|delta|theta|sigma|omega|Delta'),
            ('DOT_OP', r'dot'),
            ('CROSS_OP', r'cross'),
            ('TIMES', r'times'),
            ('DIV_OP', r'div'),
            ('WORD', r'sqrt|cbrt|sin|cos|tan|abs'),
            ('VAR', r'[a-zA-Z]+'),
            ('POW', r'\*\*|\^'),
            ('MULT', r'\*'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('SLASH', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('UNDERSCORE', r'_'),
            ('COMMA', r','),
            ('WS', r'\s+'),
        ]

        token_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)

        last_was_ws = False
        for match in re.finditer(token_re, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'WS':
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

    def parse_expression(self) -> Expression:
        """Parse full expression."""
        return self.parse_additive()

    def parse_additive(self) -> Expression:
        """Parse addition and subtraction."""
        left = self.parse_multiplicative()

        while True:
            token = self.peek()
            if token and token.kind in ['PLUS', 'MINUS']:
                op_token = self.consume()
                right = self.parse_multiplicative()
                kind = 'addition' if op_token.kind == 'PLUS' else 'subtraction'
                left = BinaryNode(kind=kind, left=left, right=right)
            else:
                break

        return left

    def parse_multiplicative(self) -> Expression:
        """Parse multiplication and division."""
        left = self.parse_power()

        while True:
            token = self.peek()

            # Explicit operators
            if token and token.kind in ['MULT', 'SLASH', 'DIV_OP', 'DOT_OP', 'CROSS_OP', 'TIMES']:
                self.consume()
                right = self.parse_power()
                
                kind_map = {
                    'MULT': 'explicit_multiplication',
                    'DOT_OP': 'dot_multiplication',
                    'CROSS_OP': 'cross_multiplication',
                    'TIMES': 'times_multiplication',
                    'DIV_OP': 'div_operation',
                    'SLASH': 'division',
                }
                left = BinaryNode(kind=kind_map[token.kind], left=left, right=right)
            # Implicit multiplication
            elif token and self._is_implicit_mult(left, token):
                right = self.parse_power()
                left = BinaryNode(kind='implicit_multiplication', left=left, right=right)
            else:
                break

        return left

    def _is_implicit_mult(self, left_expr: Expression, next_token: Token) -> bool:
        """Check if implicit multiplication should occur."""
        if next_token.kind in ['VAR', 'GREEK', 'SYMBOL', 'LPAREN', 'WORD', 'INTEGER', 'DECIMAL']:
            if next_token.kind == 'WORD' and next_token.value not in ['sqrt', 'cbrt', 'sin', 'cos', 'tan', 'abs']:
                return False
            return True
        return False

    def parse_power(self) -> Expression:
        """Parse exponentiation."""
        left = self.parse_subscript()

        token = self.peek()
        if token and token.kind == 'POW':
            self.consume()
            right = self.parse_power()  # Right associative
            return BinaryNode(kind='exponent', left=left, right=right)

        return left

    def parse_subscript(self) -> Expression:
        """Parse subscripts."""
        base = self.parse_unary()

        token = self.peek()
        if token and token.kind == 'UNDERSCORE':
            self.consume()
            subscript = self.parse_primary()
            
            # Validate that subscript is only variable or integer
            if not isinstance(subscript, AtomicNode) or subscript.kind not in ['variable', 'integer']:
                raise ValueError(f"Subscript must be a variable or integer, got {subscript}")
            
            return SubscriptNode(base=base, subscript=subscript)

        return base

    def parse_unary(self) -> Expression:
        """Parse unary operators."""
        token = self.peek()

        if token and token.kind == 'MINUS':
            self.consume()
            operand = self.parse_unary()
            return UnaryNode(kind='negation', operand=operand)

        return self.parse_primary()

    def parse_primary(self) -> Expression:
        """Parse primary expressions."""
        token = self.peek()

        if not token:
            raise ValueError("Unexpected end of expression")

        # Mixed number
        if token.kind == 'MIXED_NUM':
            return self.parse_mixed_number()

        # Decimal - check for unit pattern (e.g., "2.5 liters")
        if token.kind == 'DECIMAL':
            self.consume()
            decimal_val = float(token.value)
            
            # Check if next token is a multi-letter VAR with leading whitespace (unit pattern)
            next_token = self.peek()
            if (next_token and next_token.kind == 'VAR' and 
                next_token.has_leading_whitespace and len(next_token.value) > 1):
                # This is a unit pattern
                var_token = self.consume()
                unit = AtomicNode(kind='unit', value=var_token.value)
                return BinaryNode(kind='implicit_multiplication', 
                                left=AtomicNode(kind='decimal', value=decimal_val), 
                                right=unit)
            
            return AtomicNode(kind='decimal', value=decimal_val)

        # Integer - check for unit pattern (e.g., "5 grapes")
        if token.kind == 'INTEGER':
            self.consume()
            int_val = int(token.value)
            
            # Check if next token is a multi-letter VAR with leading whitespace (unit pattern)
            next_token = self.peek()
            if (next_token and next_token.kind == 'VAR' and 
                next_token.has_leading_whitespace and len(next_token.value) > 1):
                # This is a unit pattern
                var_token = self.consume()
                unit = AtomicNode(kind='unit', value=var_token.value)
                return BinaryNode(kind='implicit_multiplication',
                                left=AtomicNode(kind='integer', value=int_val),
                                right=unit)
            
            return AtomicNode(kind='integer', value=int_val)

        # Symbol (pi, e)
        if token.kind == 'SYMBOL':
            self.consume()
            return AtomicNode(kind='symbol', value=token.value)

        # Greek letters
        if token.kind == 'GREEK':
            self.consume()
            return AtomicNode(kind='variable', value=token.value)

        # Variable - need to handle implicit multiplication
        if token.kind == 'VAR':
            var_token = self.consume()
            var_name = var_token.value
            
            # If no leading whitespace and multiple chars, split into individual vars
            if len(var_name) > 1 and not var_token.has_leading_whitespace:
                # Split into individual variables with implicit multiplication
                result = AtomicNode(kind='variable', value=var_name[0])
                for char in var_name[1:]:
                    result = BinaryNode(kind='implicit_multiplication',
                                      left=result,
                                      right=AtomicNode(kind='variable', value=char))
                return result
            else:
                # Single char or has leading whitespace
                return AtomicNode(kind='variable', value=var_name)

        # Function
        if token.kind == 'WORD' and token.value in ['sqrt', 'cbrt', 'sin', 'cos', 'tan', 'abs']:
            return self.parse_function()

        # Parentheses
        if token.kind == 'LPAREN':
            return self.parse_group()

        raise ValueError(f"Unexpected token: {token}")

    def parse_mixed_number(self) -> MixedNumberNode:
        """Parse mixed numbers like 3'1/4."""
        token = self.consume()
        match = re.match(r'(\d+)\'(\d+)/(\d+)', token.value)
        whole = int(match.group(1))
        num = int(match.group(2))
        den = int(match.group(3))
        return MixedNumberNode(whole=whole, numerator=num, denominator=den)

    def parse_function(self) -> FunctionNode:
        """Parse function calls."""
        name_token = self.consume()
        name = name_token.value

        # Expect opening parenthesis
        if not self.peek() or self.peek().kind != 'LPAREN':
            raise ValueError(f"Expected '(' after function {name}")

        self.consume()  # consume '('

        args = []
        while True:
            args.append(self.parse_additive())

            if self.peek() and self.peek().kind == 'COMMA':
                self.consume()
            else:
                break

        if not self.peek() or self.peek().kind != 'RPAREN':
            raise ValueError(f"Expected ')' after function arguments")

        self.consume()  # consume ')'

        return FunctionNode(name=name, args=args)

    def parse_group(self) -> Expression:
        """Parse parenthesized expressions."""
        self.consume()  # consume first '('

        # Check for double parentheses
        if self.peek() and self.peek().kind == 'LPAREN':
            saved_pos = self.token_pos
            self.consume()  # tentatively consume second '('

            try:
                inner_expr = self.parse_additive()

                # Check if next is ')' and after that is ')'
                if (self.peek() and self.peek().kind == 'RPAREN' and
                    self.peek(1) and self.peek(1).kind == 'RPAREN'):
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

        if not self.peek() or self.peek().kind != 'RPAREN':
            raise ValueError("Expected ')'")

        self.consume()  # consume ')'

        return GroupNode(expr=expr, explicit_parentheses=False)


def parse_math(text: str) -> Expression:
    """Parse a mathematical expression string."""
    parser = MathParser(text)
    return parser.parse()


__all__ = [
    'AtomicNode', 'SubscriptNode', 'MixedNumberNode', 'BinaryNode',
    'UnaryNode', 'FunctionNode', 'GroupNode', 'Expression', 'parse_math'
]


if __name__ == "__main__":
    # Basic tests
    basic_tests = [
        ("2ab", "2ab", "2 * a * b"),
        ("2 ab", "2ab", "2 * Unit('ab')"),
        ("ab + 5", "ab + 5", "a * b + 5"),
        ("5 grapes", "5grapes", "5 * Unit('grapes')"),
        ("3.14", "3.14", "Decimal"),
        ("42", "42", "Integer"),
        ("pi", "pi", "Symbol"),
        ("2pi", "2pi", "2 * pi (implicit)"),
        ("x_i + y_j", "x_i + y_j", "Subscripts"),
        ("a^2 + b^2", "a**2 + b**2", "Powers"),
        ("((x + y))", "((x + y))", "Double parens"),
        ("(x + y)", "(x + y)", "Single parens"),
        ("2 * 3 + 4", "2 * 3 + 4", "Explicit ops"),
        ("abc", "abc", "a * b * c"),
        ("2abc", "2abc", "2 * a * b * c"),
        ("10 meters", "10meters", "10 * Unit('meters')"),
    ]

    # Unit-specific tests
    unit_tests = [
        ("5 apples", "5apples", "5 * Unit('apples')"),
        ("10 kg", "10kg", "10 * Unit('kg')"),
        ("3 meters", "3meters", "3 * Unit('meters')"),
        ("100 USD", "100USD", "100 * Unit('USD')"),
        ("2.5 liters", "2.5liters", "2.5 * Unit('liters')"),
        ("7 days", "7days", "7 * Unit('days')"),
        ("abc + 5 units", "abc + 5units", "Implicit mult + units"),
        ("2 x + 3 y", "2x + 3y", "Variables that look like units but aren't"),
    ]

    # Edge cases
    edge_tests = [
        ("xyz", "xyz", "Three vars multiplied"),
        ("2x", "2x", "Number with single var"),
        ("x2", "x2", "Var with number (implicit mult)"),
        ("3pi", "3pi", "Number with symbol"),
        ("e + pi", "e + pi", "Multiple symbols"),
        ("2 a", "2a", "Number space single-letter var (NOT a unit)"),
    ]
    
    # Subscript validation tests
    subscript_tests = [
        ("x_1", "x_1", "Valid: integer subscript"),
        ("a_i", "a_i", "Valid: variable subscript"),
        ("y_10", "y_10", "Valid: integer subscript"),
    ]

    print("=" * 60)
    print("BASIC TESTS")
    print("=" * 60)
    for expr_str, expected, description in basic_tests:
        try:
            result = parse_math(expr_str)
            output = result.to_str()
            status = "✓" if output == expected else f"✗ (expected: {expected})"
            print(f"{status} {expr_str!r:20} → {output:20} # {description}")
        except Exception as e:
            print(f"✗ {expr_str!r:20} → Error: {e}")
    
    print("\n" + "=" * 60)
    print("UNIT TESTS")
    print("=" * 60)
    for expr_str, expected, description in unit_tests:
        try:
            result = parse_math(expr_str)
            output = result.to_str()
            status = "✓" if output == expected else f"✗ (expected: {expected})"
            print(f"{status} {expr_str!r:20} → {output:20} # {description}")
            
            # Check if it contains a unit
            def check_for_unit(node) -> bool:
                if isinstance(node, AtomicNode) and node.kind == 'unit':
                    return True
                if isinstance(node, BinaryNode):
                    return check_for_unit(node.left) or check_for_unit(node.right)
                elif isinstance(node, UnaryNode):
                    return check_for_unit(node.operand)
                elif isinstance(node, FunctionNode):
                    return any(check_for_unit(arg) for arg in node.args)
                elif isinstance(node, GroupNode):
                    return check_for_unit(node.expr)
                elif isinstance(node, SubscriptNode):
                    return check_for_unit(node.base) or check_for_unit(node.subscript)
                return False
            
            has_unit = check_for_unit(result)
            if "Unit" in description and has_unit:
                print(f"  → Contains unit kind ✓")
            elif "Unit" in description and not has_unit:
                print(f"  → Missing unit kind ✗")
                
        except Exception as e:
            print(f"✗ {expr_str!r:20} → Error: {e}")

    print("\n" + "=" * 60)
    print("EDGE CASES")
    print("=" * 60)
    for expr_str, expected, description in edge_tests:
        try:
            result = parse_math(expr_str)
            output = result.to_str()
            status = "✓" if output == expected else f"✗ (expected: {expected})"
            print(f"{status} {expr_str!r:20} → {output:20} # {description}")
        except Exception as e:
            print(f"✗ {expr_str!r:20} → Error: {e}")
    
    print("\n" + "=" * 60)
    print("SUBSCRIPT VALIDATION TESTS")
    print("=" * 60)
    for expr_str, expected, description in subscript_tests:
        try:
            result = parse_math(expr_str)
            output = result.to_str()
            status = "✓" if output == expected else f"✗ (expected: {expected})"
            print(f"{status} {expr_str!r:20} → {output:20} # {description}")
        except Exception as e:
            print(f"✗ {expr_str!r:20} → Error: {e}")

    # Test invalid subscripts
    print("\n" + "=" * 60)
    print("INVALID SUBSCRIPT TESTS (should fail)")
    print("=" * 60)
    invalid_subscript_tests = [
        ("x_(a+b)", "Should fail: expression subscript"),
        ("y_pi", "Should fail: symbol subscript"),
    ]
    
    for expr_str, description in invalid_subscript_tests:
        try:
            result = parse_math(expr_str)
            output = result.to_str()
            print(f"✗ {expr_str!r:20} → {output:20} # {description} (should have failed)")
        except ValueError as e:
            print(f"✓ {expr_str!r:20} → Correctly rejected # {description}")
        except Exception as e:
            print(f"? {expr_str!r:20} → Unexpected error: {e}")

    # Print sample node structure
    print("\n" + "=" * 60)
    print("SAMPLE NODE STRUCTURE")
    print("=" * 60)
    sample = parse_math("2 apples + 3x")
    print(f"Expression: '2 apples + 3x'")
    print(f"Root node kind: {sample.kind}")
    if isinstance(sample, BinaryNode):
        print(f"  Left: {sample.left} (kind: {sample.left.kind if hasattr(sample.left, 'kind') else 'N/A'})")
        print(f"  Right: {sample.right} (kind: {sample.right.kind if hasattr(sample.right, 'kind') else 'N/A'})")
