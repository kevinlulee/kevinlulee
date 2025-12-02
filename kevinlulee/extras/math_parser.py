from dataclasses import dataclass
from typing import Union, List, Optional
import re


@dataclass
class Number:
    value: float

    def to_str(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)


@dataclass
class Variable:
    name: str

    def to_str(self) -> str:
        return self.name


@dataclass
class Subscript:
    base: 'Expression'
    subscript: 'Expression'

    def to_str(self) -> str:
        return f"{self.base.to_str()}_{self.subscript.to_str()}"


@dataclass
class MixedNumber:
    whole: int
    numerator: int
    denominator: int

    def to_str(self) -> str:
        return f"{self.whole}'{self.numerator}/{self.denominator}"


@dataclass
class BinaryOp:
    op: str  # normalized operator: '+', '-', '*', '/', '**', 'dot', 'cross', 'times', 'div'
    left: 'Expression'
    right: 'Expression'
    implicit: bool = False  # True if multiplication was implicit

    def to_str(self) -> str:
        left_str = self.left.to_str()
        right_str = self.right.to_str()

        # Add parentheses for complex expressions if needed
        if isinstance(self.left, BinaryOp) and self._needs_parens(self.left, True):
            left_str = f"({left_str})"
        if isinstance(self.right, BinaryOp) and self._needs_parens(self.right, False):
            right_str = f"({right_str})"

        # Implicit multiplication has no operator
        if self.implicit:
            return f"{left_str}{right_str}"

        # Map operators to display strings
        op_map = {
            '+': ' + ',
            '-': ' - ',
            '*': ' * ',
            '/': ' / ',  # fraction display
            '**': '**',
            'times': ' times ',  # times symbol display
            'div': ' div ',  # division display
            'dot': ' dot ',  # dot product display
            'cross': ' cross ',  # cross product display
        }
        return f"{left_str}{op_map.get(self.op, self.op)}{right_str}"

    def _needs_parens(self, expr: 'BinaryOp', is_left: bool) -> bool:
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, 'times': 2, 'div': 2, '**': 3, 'dot': 2, 'cross': 2}
        parent_prec = precedence.get(self.op, 0)
        child_prec = precedence.get(expr.op, 0)

        if child_prec < parent_prec:
            return True
        if child_prec == parent_prec and not is_left and self.op in ['/', '-', '**', 'div']:
            return True
        return False


@dataclass
class UnaryOp:
    op: str
    operand: 'Expression'

    def to_str(self) -> str:
        if self.op == '-':
            operand_str = self.operand.to_str()
            if isinstance(self.operand, BinaryOp):
                operand_str = f"({operand_str})"
            return f"-{operand_str}"
        return f"{self.op}({self.operand.to_str()})"


@dataclass
class Function:
    name: str
    args: List['Expression']

    def to_str(self) -> str:
        args_str = ', '.join(arg.to_str() for arg in self.args)
        return f"{self.name}({args_str})"


@dataclass
class Group:
    expr: 'Expression'
    doubled: bool = False  # True if double parens like ((x))

    def to_str(self) -> str:
        inner = self.expr.to_str()
        if self.doubled:
            return f"(({inner}))"
        return f"({inner})"


@dataclass
class Relation:
    op: str
    left: 'Expression'
    right: 'Expression'

    def to_str(self) -> str:
        op_map = {
            '=': ' = ',
            '!=': ' not equal ',
            '<': ' < ',
            '>': ' > ',
            '<=': ' <= ',
            '>=': ' >= ',
        }
        return f"{self.left.to_str()}{op_map.get(self.op, self.op)}{self.right.to_str()}"


Expression = Union[Number, Variable, Subscript, MixedNumber, BinaryOp, UnaryOp,
                   Function, Group, Relation]


@dataclass
class Equation:
    left: Expression
    right: Expression

    def to_str(self) -> str:
        return f"{self.left.to_str()} = {self.right.to_str()}"


class MathParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.token_pos = 0

    def parse(self) -> Union[Expression, Equation]:
        self.tokenize()
        result = self.parse_expression()
        return result

    def tokenize(self):
        """Convert input string into tokens."""
        patterns = [
            ('MIXED_NUM', r'\d+\'\d+/\d+'),
            ('NUMBER', r'\d+\.?\d*'),
            ('GREEK', r'alpha|beta|gamma|delta|theta|pi|sigma|omega|Delta'),
            ('DOT_OP', r'dot'),
            ('CROSS_OP', r'cross'),
            ('TIMES', r'times'),
            ('DIV_OP', r'div'),
            ('WORD', r'sqrt|cbrt|sin|cos|tan|abs|not\s+equal'),
            ('VAR', r'[a-zA-Z][a-zA-Z0-9]*'),
            ('POW', r'\*\*|\^'),
            ('MULT', r'\*'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('SLASH', r'/'),
            ('EQUALS', r'='),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('UNDERSCORE', r'_'),
            ('COMMA', r','),
            ('WS', r'\s+'),
        ]

        token_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)

        for match in re.finditer(token_re, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'WS':
                continue

            self.tokens.append((kind, value))

    def peek(self, offset=0):
        """Look at token without consuming it."""
        pos = self.token_pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def consume(self):
        """Consume and return current token."""
        if self.token_pos < len(self.tokens):
            token = self.tokens[self.token_pos]
            self.token_pos += 1
            return token
        return None

    def parse_expression(self) -> Expression:
        """Parse full expression, handling equations."""
        left = self.parse_comparison()

        # Check for equation
        if self.peek() and self.peek()[0] == 'EQUALS':
            self.consume()  # consume '='
            right = self.parse_comparison()
            return Equation(left, right)

        return left

    def parse_comparison(self) -> Expression:
        """Parse comparison operators."""
        left = self.parse_additive()

        token = self.peek()
        if token and token[0] == 'WORD' and token[1] == 'not equal':
            self.consume()
            right = self.parse_additive()
            return Relation('!=', left, right)

        return left

    def parse_additive(self) -> Expression:
        """Parse addition and subtraction."""
        left = self.parse_multiplicative()

        while True:
            token = self.peek()
            if token and token[0] in ['PLUS', 'MINUS']:
                op_token = self.consume()
                op = '+' if op_token[0] == 'PLUS' else '-'
                right = self.parse_multiplicative()
                left = BinaryOp(op, left, right)
            else:
                break

        return left

    def parse_multiplicative(self) -> Expression:
        """Parse multiplication and division."""
        left = self.parse_power()

        while True:
            token = self.peek()

            # Explicit operators
            if token and token[0] in ['MULT', 'SLASH', 'DIV_OP', 'DOT_OP', 'CROSS_OP', 'TIMES']:
                if token[0] == 'MULT':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('*', left, right, implicit=False)
                elif token[0] == 'DOT_OP':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('dot', left, right, implicit=False)
                elif token[0] == 'CROSS_OP':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('cross', left, right, implicit=False)
                elif token[0] == 'TIMES':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('times', left, right, implicit=False)
                elif token[0] == 'DIV_OP':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('div', left, right, implicit=False)
                elif token[0] == 'SLASH':
                    self.consume()
                    right = self.parse_power()
                    left = BinaryOp('/', left, right, implicit=False)
            # Implicit multiplication
            elif token and self._is_implicit_mult(left, token):
                right = self.parse_power()
                left = BinaryOp('*', left, right, implicit=True)
            else:
                break

        return left

    def _is_implicit_mult(self, left_expr, next_token) -> bool:
        """Check if implicit multiplication should occur."""
        if next_token[0] in ['VAR', 'GREEK', 'LPAREN', 'WORD']:
            if next_token[0] == 'WORD' and next_token[1] not in ['sqrt', 'cbrt', 'sin', 'cos', 'tan', 'abs']:
                return False
            return True
        return False

    def parse_power(self) -> Expression:
        """Parse exponentiation."""
        left = self.parse_subscript()

        token = self.peek()
        if token and token[0] == 'POW':
            self.consume()
            right = self.parse_power()  # Right associative
            return BinaryOp('**', left, right)

        return left

    def parse_subscript(self) -> Expression:
        """Parse subscripts."""
        base = self.parse_unary()

        token = self.peek()
        if token and token[0] == 'UNDERSCORE':
            self.consume()
            subscript = self.parse_primary()
            return Subscript(base, subscript)

        return base

    def parse_unary(self) -> Expression:
        """Parse unary operators."""
        token = self.peek()

        if token and token[0] == 'MINUS':
            self.consume()
            operand = self.parse_unary()
            return UnaryOp('-', operand)

        return self.parse_primary()

    def parse_primary(self) -> Expression:
        """Parse primary expressions."""
        token = self.peek()

        if not token:
            raise ValueError("Unexpected end of expression")

        # Mixed number
        if token[0] == 'MIXED_NUM':
            return self.parse_mixed_number()

        # Number
        if token[0] == 'NUMBER':
            self.consume()
            return Number(float(token[1]))

        # Variable or Greek letter
        if token[0] in ['VAR', 'GREEK']:
            self.consume()
            return Variable(token[1])

        # Function
        if token[0] == 'WORD' and token[1] in ['sqrt', 'cbrt', 'sin', 'cos', 'tan', 'abs']:
            return self.parse_function()

        # Parentheses
        if token[0] == 'LPAREN':
            return self.parse_group()

        raise ValueError(f"Unexpected token: {token}")

    def parse_mixed_number(self) -> MixedNumber:
        """Parse mixed numbers like 3'1/4."""
        token = self.consume()
        match = re.match(r'(\d+)\'(\d+)/(\d+)', token[1])
        whole = int(match.group(1))
        num = int(match.group(2))
        den = int(match.group(3))
        return MixedNumber(whole, num, den)

    def parse_function(self) -> Function:
        """Parse function calls."""
        name_token = self.consume()
        name = name_token[1]

        # Expect opening parenthesis
        if not self.peek() or self.peek()[0] != 'LPAREN':
            raise ValueError(f"Expected '(' after function {name}")

        self.consume()  # consume '('

        args = []
        while True:
            args.append(self.parse_additive())

            if self.peek() and self.peek()[0] == 'COMMA':
                self.consume()
            else:
                break

        if not self.peek() or self.peek()[0] != 'RPAREN':
            raise ValueError(f"Expected ')' after function arguments")

        self.consume()  # consume ')'

        return Function(name, args)

    def parse_group(self) -> Expression:
        """Parse parenthesized expressions."""
        self.consume()  # consume first '('

        # Check for double parentheses
        if self.peek() and self.peek()[0] == 'LPAREN':
            saved_pos = self.token_pos
            self.consume()  # tentatively consume second '('

            try:
                inner_expr = self.parse_additive()

                # Check if next is ')' and after that is ')'
                if (self.peek() and self.peek()[0] == 'RPAREN' and
                    self.peek(1) and self.peek(1)[0] == 'RPAREN'):
                    # This is double parentheses!
                    self.consume()  # consume first ')'
                    self.consume()  # consume second ')'
                    return Group(inner_expr, doubled=True)
                else:
                    # Not double parens, backtrack
                    self.token_pos = saved_pos
            except:
                # Error parsing, backtrack
                self.token_pos = saved_pos

        # Normal parentheses parsing
        expr = self.parse_additive()

        if not self.peek() or self.peek()[0] != 'RPAREN':
            raise ValueError("Expected ')'")

        self.consume()  # consume ')'

        return Group(expr, doubled=False)


def parse_math(text: str) -> Union[Expression, Equation]:
    """Parse a mathematical expression string."""
    parser = MathParser(text)
    return parser.parse()


# Example usage
if __name__ == "__main__":
    examples = [
        "2x",
        "(3 times 4 / (2 + 5))",
        "(a_2)^2 / b_1",
        "(x + y)",
        "x_i + y_j"
    ]
    
    for expr_str in examples:
        result = parse_math(expr_str)
        print(f"Input:  {expr_str}")
        print(f"Output: {result.to_str()}")
        print()


