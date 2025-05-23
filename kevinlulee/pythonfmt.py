from kevinlulee.ao import mapfilter
from kevinlulee.text_tools import bracket_wrap, strcall
from kevinlulee.base import real



class PythonArgumentFormatter:
    def __init__(self, max_width=50, indentation=2):
        self.indentation = indentation
        self.max_width = max_width

    def format(self, value, level=0, real = False):
        if value is None:
            return "None"
        if value is True:
            return "True"
        if value is False:
            return "False"
        if isinstance(value, dict):
            return self.format_dict(value, level, real = real)
        if isinstance(value, (list, tuple)):
            return self.format_list(value, level)
        if isinstance(value, str):
            if real:
                return value
            return f'"{value}"'
        return str(value)

    def format_list(self, lst, level=0):
        args = [self.format(v, level + 1) for v in lst]
        comma = "," if len(args) == 1 else ""
        return self._format_collection(args, level, comma, bracket_type='[]')

    def _format_raw_dict(self, dct, level=0, as_argument = False, real= False):
        delimiter = "=" if as_argument else ": "
        def callback(el):
            k, v = el
            prefix = k if as_argument else f'"{k}"'
            return f'{prefix}{delimiter}{self.format(v, level + 1, real = real)}'

        return mapfilter(dct.items(), callback)

    def format_dict(self, dct, level=0, real = False):
        value = self._format_raw_dict(dct, level, real = real)
        return self._format_collection(value, level, bracket_type='{}')

    def _format_collection(self, args, level=0, comma="", bracket_type = ''):
        sample = bracket_wrap(args, bracket_type=bracket_type, indent=self.indentation)
        if len(sample) < 30: # this fixes the look
            return sample
        else:
            return bracket_wrap(args, bracket_type=bracket_type, indent=self.indentation, newlines = True)

    def decl(self, name, value):
        return f'{name} = {self.format(value)}'

    def real_decl(self, name, value):
        middle = ' ' if name == 'return' else ' = '
        return f'{name}{middle}{self.format(value, real = True)}'

    def call(self, func_name, *args, **kwargs):
        args = [self.format(v) for v in args]
        kwargs = self._format_raw_dict(kwargs, as_argument = True)
        return strcall(func_name, args, kwargs, max_length = 60)

    def real_call(
        self,
        name,
        *args,
        **kwargs
    ):

        args = [self.format(real(v)) for v in args]
        kwargs = self._format_raw_dict(kwargs, as_argument = True)
        return strcall(name, args, kwargs, max_length = 60)
        

    def func_decl(self, name, *args, body='return', **kwargs, ):
        parts = self.real_call(name, *args, **kwargs)
        prefix = f'def {parts}'
        return prefix + bracket_wrap(body, bracket_type=':', delimiter='', newlines=True)


pythonfmt = PythonArgumentFormatter()
# print(pythonfmt.func_decl('asdf', 'xx', body = 'rsfsdfeturn'))

# print(pythonfmt.call('foobar', 'alphalpha', 'xx', [1,2,'hi'], {'a': {'a':1}}))
# aobj = {
#     'a': {
#         'b': "alphalpha",
#         'c': "alphalpha",
#     }
# }
# print(pythonfmt.real_decl('hi', aobj))
