import json
import re
import yaml
import textwrap

from kevinlulee.validation import is_array, is_string
import kevinlulee.primary as kx
from .ao import to_array

BLANK = '<BLANK>'
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
                m = self.getter(word)
                if isinstance(m, dict):
                    return json.dumps(m, indent=2, ensure_ascii=False)
                if callable(m):
                    return m()
                return m

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
                if isinstance(value, (str, int, float)):
                    return str(value) + comma
                else:
                    return BLANK
                assert isinstance(value, (str, int, float)), f"without bullets, the value must be a primitive. the provided value <<{value}>> does not match."
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
        s = re.sub(TEMPLATER_PATTERN, self.replace, text)
        if BLANK in s:
            return re.sub(f'\n\s*{BLANK} *', '', s)
        return s

templater = Templater().format

import re
from typing import Any, Dict, Type

class AbstractTemplater:
    PATTERN = ''

    def __init__(self, scope, template, flags = 0):
        self.scope = scope
        self.template = template
        self.flags = flags

    def format(self):
        text = textwrap.dedent(self.template).strip()
        return re.sub(self.PATTERN, self.replace, text, flags = self.flags)

    def __str__(self):
        return self.format()
    

class ClassTemplater(AbstractTemplater):
    PATTERN = '''{(.*?)}'''

    def replace(self, match):
        scope = {'self': self.scope}
        keys = kx.split(match.group(1), '&')
        return kx.join_text(kx.each(keys, eval, scope))

__all__ = ['ClassTemplater', 'templater']


if __name__ == "__main__":
    print(templater('''
        hi\n$alphalphalpha\nbye
    ''', {'alphalpha': 1}))
