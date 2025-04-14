import re
import yaml
import textwrap

from kevinlulee.validation import is_array, is_string
from .ao import to_array

TEMPLATER_PATTERN = re.compile(r'''
    (?:(^|\n)(\s*)([-*•]|\d+[.)])(\s+))?  # Optional leading bullet (•, *, -, or numbered)
    \$                                  # Literal $ symbol
    (?:
        ({.*?})                         # Bracket expression
        |                               # OR
        (\w+)                           # Simple word variable
        (,?)                            # Optional trailing comma
    )
''', flags=re.VERBOSE)


class Templater:
    def __init__(self):
        self.scope = {}
    
    def replace(self, match):
        groups = match.groups()
        newline, ind, bullet, after_spaces, bracket_expr, word, comma = groups
        comma = comma or ''

        def get(bracket_expr, word):
            if bracket_expr:
                rendered = self.format(bracket_expr.strip('{}'), self.scope)
                return str(eval(rendered))
            elif word:
                return self.getter(word)

        def add_spacing(value, newline, ind, bullet, after_spaces, comma):
            if bullet:
                if isinstance(value, dict):
                    raise Exception("no dicts allowed in templater")
                if is_array(value):
                    s = newline

                    def fix(i, bullet):
                        def replacer(x):
                            return str(int(x.group(0)) + i)
                        return re.sub(r'\d', replacer, bullet)

                    length = len(value)
                    for i, arg in enumerate(value):
                        if i == length - 1:
                            s += ind + fix(i, bullet) + after_spaces + str(arg)
                        else:
                            s += ind + fix(i, bullet) + after_spaces + str(arg) + comma + "\n"
                            
                    return s
                else:
                    return newline + ind + bullet + after_spaces + str(value) + comma
            else:
                assert isinstance(value, (str, int, float)), "without bullets, the value must be a primitive"
                return str(value) + comma

        value = get(bracket_expr, word) 
        return add_spacing(value, newline, ind, bullet, after_spaces, comma)

    def format(self, s, scope=None):
        self.scope = scope or {}
        if isinstance(self.scope, dict):
            self.getter = self.scope.get
        elif isinstance(self.scope, (list, tuple)):
            self.getter = lambda x: self.scope[int(x) - 1]
        else:
            self.getter = lambda x: getattr(self.scope, x)

        text = textwrap.dedent(s).strip()
        return re.sub(TEMPLATER_PATTERN, self.replace, text)

def rgetattr(obj, attr):
    for part in attr.split('.'):
        obj = getattr(obj, part)
    return obj

templater = Templater().format
