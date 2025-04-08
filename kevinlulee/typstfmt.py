from kevinlulee.ao import mapfilter
from kevinlulee.text_tools import bracket_wrap
from kevinlulee.string_utils import dash_case
from kevinlulee.base import real, strcall

import re

css_unit_re = r"(-?\d*\.?\d+)(px|em|rem|vh|vw|vmin|vmax|%|cm|mm|in|pt|pc|ex|ch)$"

alignments = ('left', 'right', 'top', 'center', 'bottom', 'horizon')
# alignments left right top bottom center horizon
typst_keys = ('scale','stroke', 'wh', 'width', 'height', 'align')
class TypstArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def _coerce_value(self, k, v):
        if isinstance(v, (int, float)):
            if k == 'rotate':
                return deg(v)
            else:
                return pt(v)
        if isinstance(v, str):
            if k in typst_keys:
                return real(v)
            elif k in ('paint', 'fill', 'bg', 'fg'):
                return Color(v)
            elif re.search(css_unit_re, v):
                return real(v)
            elif v in alignments:
                return real(v)
            else:
                return v
        return v

    def format(self, value, level=0, coerce=False):
        if value is None:
            return "none"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, dict):
            return self.format_dict(value, level, coerce)
        if isinstance(value, (list, tuple)):
            return self.format_list(value, level, coerce)
        if isinstance(value, str):
            if value.startswith('$') and value.endswith('$'):
                return value
            if value.startswith('`') and value.endswith('`'):
                return value
            if "\n" in value:
                return bracket_wrap(value, bracket_type='[]')
            return f'"{value}"'
        return str(value)

    def format_list(self, lst, level=0, coerce=False):
        args = [self.format(v, level + 1, coerce) for v in lst]
        comma = "," if len(args) == 1 else ""
        return self._format_collection(args, level, comma)

    def _format_raw_dict(self, dct, level=0, coerce=False):
        def callback(el):
            k, v = el
            prefix = f'"{k}"' if isinstance(k, (int, float)) else dash_case(k)
            if not v:
                return prefix + ": none"
            if coerce:
                v = self._coerce_value(k, v)
            val = self.format(v, level + 1, coerce)
            if not val:
                return
            return prefix + ": " + val

        return mapfilter(dct.items(), callback)

    def format_dict(self, dct, level=0, coerce=False):
        return self._format_collection(self._format_raw_dict(dct, level, coerce), level)

    def _format_collection(self, args, level=0, comma=""):
        sample = f"({', '.join(args)}{comma})"
        if any("\n" in arg for arg in args):
            return bracket_wrap(args, "()", indent=self.indentation, newlines=True)
        elif len(sample) < self.max_width - (level * self.indentation):
            return sample
        else:
            return bracket_wrap(args, "()", indent=self.indentation, newlines = True)

    def decl(self, name, value, toplevel=False, coerce=False):
        hash = '#' if toplevel else ''
        return f'{hash}let {name} = {self.format(value, coerce=coerce)}'

    def call(self, _name, *args, reverse=True, toplevel=False, real=False, coerce=True, **kwargs):
        name = _name
        if not real:
            args = [self.format(v, coerce=coerce) for v in args]
        kwargs = self._format_raw_dict(kwargs, coerce=coerce)
        hash = '#' if toplevel else ''
        return hash + strcall(name, args, kwargs)

    def include(self, s, toplevel=False):
        hash = '#' if toplevel else ''
        return f'{hash}include "{s}"'

    def comment(self, s):
        return '// ' + s


typstfmt = TypstArgumentFormatter()

