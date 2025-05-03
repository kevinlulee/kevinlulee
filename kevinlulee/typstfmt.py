from kevinlulee.ao import mapfilter
from kevinlulee.validation import is_array, is_number, is_string
from kevinlulee.text_tools import bracket_wrap, strcall
from kevinlulee.string_utils import dash_case
from kevinlulee.base import real
# import numpy as np
# i think this works
# i think we also need access to the primitives

def floatify(v):
    if is_array(v):
        return real(str(float(v)) + 'deg')
    
typst_color_keys = [
    "fill",
    "stroke",
    "paint",
    "highlight",
]

typst_length_keys = [
    "width",
    "height",
    "thickness",
    "inset",
    "outset",
    "spacing",
    "indent",
    "stroke-width",
    "radius",
    "gap",
    "margin",
    "padding",
    "pos",
]


import re


def markup(s):
    return bracket_wrap(value, bracket_type='[]', newlines=True)
css_unit_re = r"(-?\d*\.?\d+)(px|em|rem|vh|vw|vmin|vmax|%|cm|mm|in|pt|pc|ex|ch)$"

alignments = ('left', 'right', 'top', 'center', 'bottom', 'horizon')
# alignments left right top bottom center horizon
typst_keys = ('scale','stroke', 'wh', 'width', 'height', 'align')

def is_point_pair(x):
    return is_array(x) and isinstance(x[0], (float, int)) and len(x) == 2
class TypstArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def _coerce_value(self, k, v):
        if isinstance(v, (np.float32, np.float64, np.integer)):
            v = float(v)

        # if isinstance(v, (np.float32, np.float64, np.integer)):
        #     if k == 'rotate':
        #         return real(str(float(v)) + 'deg')
        #     else:
        #         return real(str(float(v)) + 'pt')
        if is_number(v):
            if k == 'rotate' or k == 'angle':
                return real(str(v) + 'deg')
            else:
                return real(str(v) + 'pt')
        if is_string(v):
            if k in typst_keys:
                return real(v)
            elif k in ('paint', 'fill', 'bg', 'fg'):
                return real(v)
            elif re.search(css_unit_re, v):
                return real(v)
            elif v in alignments:
                return real(v)
            else:
                return v
        if (k == 'args' or k == 'points') and is_array(v) and all(is_point_pair(p) for p in v):
            return [[real(str(float(v)) + 'pt') for v in el] for el in v]
        return v

    def format(self, value, level=0, coerce=False, parent_key = None):
        if value is None:
            return "none"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, dict):
            return self.format_dict(value, level, coerce, parent_key)
        if isinstance(value, (list, tuple)):
            return self.format_list(value, level, coerce, parent_key)
        if isinstance(value, str):
            if value.startswith('$') and value.endswith('$'):
                return value
            if value.startswith('`') and value.endswith('`'):
                return value
            if "\n" in value:
                return markup(value)
            return f'"{value}"'

        if parent_key and coerce:
            return self.coerce(value, parent_key)
        return str(value)

    def coerce(self, value, parent_key):
        if parent_key == 'rotate':
            return deg(value)
        if parent_key in typst_length_keys:
            return real(str(value))

        return value
    def format_list(self, lst, level=0, coerce=False, parent_key = None):
        args = [self.format(v, level + 1, coerce, parent_key=parent_key) for v in lst]
        comma = "," if len(args) == 1 else ""
        return self._format_collection(args, level, comma)

    def _format_raw_dict(self, dct, level=0, coerce=False, parent_key = None, as_argument = False):
        def callback(el):
            k, v = el
            prefix = dash_case(k) if as_argument else f'"{k}"' if not is_number(k) else dash_case(k)
            if v is None:
                return prefix + ": none"
            # if coerce:
            #     v = self._coerce_value(k, v)
            val = self.format(v, level + 1, coerce, parent_key=k)
            if val is None:
                return
            return prefix + ": " + str(val)

        return mapfilter(dct.items(), callback)

    def format_dict(self, dct, level=0, coerce=False, parent_key = None):
        return self._format_collection(self._format_raw_dict(dct, level, coerce, parent_key = parent_key), level)

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
        kwargs = self._format_raw_dict(kwargs, coerce=coerce, as_argument = True)
        hash = '#' if toplevel else ''
        return hash + strcall(name, args, kwargs)

    def include(self, s, toplevel=False):
        hash = '#' if toplevel else ''
        return f'{hash}include "{s}"'

    def comment(self, s):
        return '// ' + s

    def func(self, name, *args, toplevel=False, body='return', **kwargs):
        hash = '#' if toplevel else ''
        parts = self.call(name, *args, **kwargs)
        prefix = f'{hash}let {parts}'
        return prefix + bracket_wrap(body, bracket_type='{}', delimiter='', newlines=True)


typstfmt = TypstArgumentFormatter()



data = {
  "meta": {
    "debug": True,
    "topdown": False
  },
  "wrapper": {
    "width": 25.0,
    "height": 25.0,
    "inset": 0
  },
  "contents": [
    {
      "type": "line",
      "pos": 
        [
          135.0,
          115.0
        ]
      ,
      "args": [
        [
          135.0,
          115.0
        ]
      ],
      "kwargs": {
        "angle": 0.0,
        "length": 60.0
      }
    },
    {
      "type": "rect",
      "args": [
        [
          135.0,
          135.0
        ]
      ],
      "kwargs": {
        "width": 250.0,
        "height": 250.0
      }
    }
  ]
}


# print(typstfmt.format(data, coerce = True))
