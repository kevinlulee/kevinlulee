from enum import Enum
from kevinlulee import *
pointlike_keys = ['args', 'points']
numpy_keys = ['pos', 'points']


angular = ['rotate', 'angle']

def quotify(s):
    return f'"{s}"'
def pointify(value, unit = 'pt'):
    return str(value) + unit
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
    "length",
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
    return is_array(x) and isinstance(x[0], (float, int)) and len(x) >= 2
class TypstArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def format(self, value, level=0, coerce=False, parent_key = None):
        if value is None:
            return "none"
        if value is True:
            return "true"
        if value is False:
            return "false"
        # print(value, parent_key)
        if isinstance(value, dict):
            return self.format_dict(value, level, coerce, parent_key)

        if isinstance(value, (list, tuple)):
            # if coerce:
            #     if parent_key == 'pos':
            #         return self.numpify(value)
            #     if parent_key == 'points':
            #         return self.numpify2(value)
                    
            return self.format_list(value, level, coerce, parent_key)

        if parent_key and coerce:
            return self.coerce(value, parent_key)

        return str(value)

    # def numpify2(self, value):
    #     return self._format_collection(self._format_collection([pointify(x) for x in p[0:2]]) for p in value)
    # def numpify(self, value):
    #
    #                 return self._format_collection([pointify(x) for x in value[0:2]])
    def coerce(self, value, parent_key):
        # print('hi', value, parent_key)
        if isinstance(value, Enum):
            if parent_key == 'dash':
                return quotify(value.value)
            return value.value
        if parent_key in angular:
            return pointify(value, "deg")
        # if parent_key in numpy_keys:
        #     return self.numpify(value)
        # if parent_key in typst_length_keys:
        #     return pointify(value)
        if parent_key in typst_color_keys:
            if isinstance(value, str):
                if value.startswith('#'):
                    return f'rgb("{value}")'
                if value.endswith(')'):
                    return value
            return str(value)

        if isinstance(value, str):
            if value.startswith('$') and value.endswith('$'):
                return value
            if value.startswith('`') and value.endswith('`'):
                return value
            if "\n" in value:
                return markup(value)
            return f'"{value}"'

        return str(value)
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
        return self._format_collection(self._format_raw_dict(dct, level, coerce, parent_key = parent_key), level, kind = "dict")

    def _format_collection(self, args, level=0, comma="", kind = ''):
        sample = f"({', '.join(args)}{comma})"
        # extra_comma = "" if kind == dict or len(args) == 1 else ","
        if any("\n" in arg for arg in args):
            return bracket_wrap(args, "()", indent=self.indentation, newlines=True, extra_comma=comma)
        elif len(sample) < self.max_width - (level * self.indentation):
            return sample
        else:
            return bracket_wrap(args, "()", indent=self.indentation, newlines = True, extra_comma=comma)

    def imports(self, *keys):
        ref = {
            "typkit": '#import "@local/typkit:0.3.0": *',
        }
        if not keys:
            keys = ['typkit']

        imports = join_text(each(keys, lambda key: ref.get(key)))
        return imports + "\n\n" 
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
          115.0,
          115.0,
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


data = {

      "kwargs": {
        "angle": 0.0,
        'fill': '#adf',
        'pos': (1, 1, 1),
        # 'pos': np.array([1,1,1]),
        'args': [(1, 1, 1), (2,2,2)],
        # 'args': [np.array([1,1,1]), np.array([1,1,1])],
#         'args': np.array([
#     [1, 2, 3, 4],
#     [5, 6, 7, 8],
#     [9, 10, 11, 12]
# ])
      },
      'asdas': 1,
      'contents': [{
          'alphasdfasdf': 11111,
          'sdf': 11111,
          'sdfsdf': 11111,
          
      }]
}

adata = {
      'contents': [{
          'alphasdfasdf': 11111,
          'sdf': 11111,
          'sdfsdf': 11111,
      }]
}
if __name__ == '__main__':
    print(typstfmt.format(data, coerce = True))
