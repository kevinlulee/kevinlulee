from kevinlulee.ao import mapfilter
from kevinlulee.text_tools import bracket_wrap
from kevinlulee.string_utils import dash_case
from kevinlulee.base import real, strcall

import re

css_unit_re = r"(-\d*\.?\d+)(px|em|rem|vh|vw|vmin|vmax|%|cm|mm|in|pt|pc|ex|ch)$"

class TypstArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def format(self, value, level=0):
        if value is None:
            return "none"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, dict):
            return self.format_dict(value, level)
        if isinstance(value, (list, tuple)):
            return self.format_list(value, level)
        # if isinstance(value, )
        if isinstance(value, str):
            if value.startswith('$') and value.endswith('$'):
                return value

            if value.startswith('`') and value.endswith('`'):
                return value
            if re.search(css_unit_re, value):
                return value
            if "\n" in value:
                return bracket_wrap(value, bracket_type='[]')
            return f'"{value}"'
        return str(value)

    def format_list(self, lst, level=0):
        args = [self.format(v, level + 1) for v in lst]
        comma = "," if len(args) == 1 else ""
        return self._format_collection(args, level, comma)

    def _format_raw_dict(self, dct, level=0, coerce_integers=False):
        def callback(el):
            k, v = el
            prefix = f'"{k}"' if isinstance(k, (int, float)) else dash_case(k)
            if not v:
                return prefix + ": none"
                return

            if coerce_integers:
                if type(v) == int or type(v) == float:
                    if k == 'rotate':
                        v = deg(v)
                    elif k == 'thickness':
                        v = pt(v)
                    else:
                        v = pt(v)
                elif k in ('scale','stroke', 'paint', 'fill', 'bg', 'fg', 'wh', 'width', 'height') and isinstance(v, str):
                    v = real(v)
                elif k in ('paint', 'fill', 'bg', 'fg') and isinstance(v, str):
                    v = Color(v)
            val = self.format(v, level + 1)
            if not val:
                # return prefix + ": " +  "none"
                return

            value = prefix + ": " +val 
            return value

        args = mapfilter(dct.items(), callback)
        return args
    def format_dict(self, dct, level=0):
        return self._format_collection(self._format_raw_dict(dct, level), level)

    def _format_collection(self, args, level=0, comma=""):
        sample = f"({', '.join(args)}{comma})"
        if any(["\n" in arg for arg in args]):
            return bracket_wrap(args, "()", indent=self.indentation, newlines = True)
            
        elif len(sample) < self.max_width - (level * self.indentation):
            return sample
        else:
            return bracket_wrap(args, "()", indent=self.indentation)

    def decl(self, name, value, toplevel = False):
        hash = '#' if toplevel else ''
        return f'{hash}let {name} = {self.format(value)}'
    def call(self, _name, *args, reverse=True, toplevel = False, real = False, **kwargs):
        name = _name
        a = len(args)
        k = len(kwargs)
        if not real:
            args = [self.format(v) for v in args]
        kwargs = self._format_raw_dict(kwargs, coerce_integers=True)
        hash = '#' if toplevel else ''
        return hash + strcall(name, args, kwargs)

    def include(self, s, toplevel = False):
        hash = '#' if toplevel else ''
        return f'{hash}include "{s}"'

    def comment(self, s):
        return '// ' + s


typstfmt = TypstArgumentFormatter()
