from __future__ import annotations
import kevinlulee as kx

import re

def create_math_re():
    b = '[a-z]'
    a = r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?'
    c = f'(?:{a}|{b}|\d+{b})'
    op = '[+\-*/=<>]'
    pat = f'{c}(?:\s+{op}\s+{c})+'
    pat2 = re.compile(f'{pat}|{a}|\\b[x-z]\\b')
    return pat2

WRAP_MATH_PATTERN = create_math_re()

def wrap_math(text, inline=True):
    delimiter = "$" if inline else "$$$"
    
    def replacer(match):
        start = match.start()
        end = match.end()
        
        # Check if char right before has a dollar
        if start > 0 and text[start - 1] == '$':
            return match.group(0)
        
        # Check if char right after has a dollar
        if end < len(text) and text[end] == '$':
            return match.group(0)
        
        return kx.parens(match.group(0), delimiter)
    
    result = re.sub(WRAP_MATH_PATTERN, replacer, text)
    return result


examples = [
  "a + b + c",
  "a + b = 2x^2",
  "x^2 + y^2 + z",
  "3.14159",
  ".75",
  "-2.5",
  "x",
  "\\alpha + \\beta = \\gamma",
  "f(x) = 2x + 3",
  "\\sin(x) + \\cos(y)",
  "(x+y)/z",
  "x^{2} + y^{2} = z^{2}",
  "[a,b;c,d]",
  "\\frac{a}{b+c}",
  "\\int_0^1 x^2\\,dx",
  "\\sum_{i=1}^n i^2",
  "x \\in \\mathbb{R}",
  "x \\le y < z",
  "|x| = \\sqrt{x^2}",
  "\\vec{v}\\cdot\\vec{w}",
  "the equation x + y = z shows",
  "We saw 12 people today.",
  "$x+y$ already",
  "Compute f(x) = 2x + 3 in the sentence.",
  "alpha = 0.05 where \\beta < 0.2",
  "{a \\in S \\mid a>0}",
  "1,234.56",
  "x+y= z",
  "2x + 3y - 4z = 0",
  "\\lim_{x\\to 0} \\frac{\\sin x}{x}",
  "P(A\\mid B) = \\frac{P(A\\cap B)}{P(B)}",
  "\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}",
  "\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}",
  "(a + b) (comment)",
  "x + (y + z)"
]


if __name__ == '__main__':
    kx.run_tests(kx.filtered2(examples, lambda x: '\\' not in x), wrap_math)
    # merp.
