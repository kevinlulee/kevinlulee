from kevinlulee.ao import mapfilter
from kevinlulee.text_tools import bracket_wrap
from kevinlulee.base import real, strcall



class PythonArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def format(self, value, level=0):
        if value is None:
            return "None"
        if value is True:
            return "True"
        if value is False:
            return "False"
        if isinstance(value, dict):
            return self.format_dict(value, level)
        if isinstance(value, (list, tuple)):
            return self.format_list(value, level)
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)

    def format_list(self, lst, level=0):
        args = [self.format(v, level + 1) for v in lst]
        comma = "," if len(args) == 1 else ""
        return self._format_collection(args, level, comma, bracket_type='[]')

    def _format_raw_dict(self, dct, level=0, as_argument = False):
        delimiter = "=" if as_argument else ": "
        def callback(el):
            k, v = el
            return f'"{k}"{delimiter}{self.format(v, level + 1)}'

        return mapfilter(dct.items(), callback)

    def format_dict(self, dct, level=0):
        value = self._format_raw_dict(dct, level)
        return self._format_collection(value, level, bracket_type='{}')

    def _format_collection(self, args, level=0, comma="", bracket_type = ''):
        a, b = list(bracket_type)
        sample = f"{a}{', '.join(args)}{comma}{b}"
        if len(sample) < self.max_width - (level * self.indentation):
            return sample
        else:
            return bracket_wrap(args, bracket_type=bracket_type, indent=self.indentation)

    def decl(self, name, value):
        return f'{name} = {self.format(value)}'

    def call(self, name, *args, **kwargs):
        args = [self.format(v) for v in args]
        kwargs = self._format_raw_dict(kwargs, as_argument = True)
        return strcall(name, args, kwargs, max_length = 60)

    def real_call(
        self,
        name,
        *args,
        **kwargs
    ):

        args = [self.format(real(v)) for v in args]
        kwargs = self._format_raw_dict(kwargs, as_argument = True)
        return strcall(name, args, kwargs, max_length = 60)
        

pythonfmt = PythonArgumentFormatter()

# print(pythonfmt.call('foobar', 'alphalpha', 'xx', [1,2,'hi'], {'a': {'a':1}}))
