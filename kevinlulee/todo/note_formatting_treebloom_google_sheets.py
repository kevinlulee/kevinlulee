
'''
"/home/kdog3682/projects/hammymathclass/typst/adapter.typ"
"/home/kdog3682/projects/hammymathclass/python/manimdoc/examples/gridpen.py"
"/home/kdog3682/projects/hammymathclass/python/manimdoc/adapter.py"
---

'''
from __future__ import annotations
from pprint import pprint
from kevinlulee import *
import kevinlulee as kx

import re

def parse_from_doc_string():
    import nvim
    import vim
    from treebloom import TreeBloom

    text = nvim.state.buffer.text
    filetype = nvim.state.buffer.filetype
    bloom = TreeBloom(text, filetype)
    # bloom = TreeBloom(nvim.state.file)
    m = bloom.query(bloom.root, '''
        (module
          (expression_statement
            (string
             (string_content) @value
            )))
    ''')
    value = m[0]['value']

    # lua.
    # from nvim.buffer import
    items = dash_split(value.text)
    main = items[-1]
    paths = extract_file_paths(main)
    pprint(main)
# def quick_register_file(file):
# parse_from_doc_string()



def my_toml(s):
    r = '^\[(\S+?)\]'
    items = split(s, r, flags = re.M)
    return dict(partition(items))


# vim.funcs.chdir('~/projects/hammymathclass/materials/')
# print(os.listdir())
# if __name__ == '__main__':
#     print(fancy_filetree('~/projects/hammymathclass/'))
from nvim.buffers import Buffers


# Buffers()
from nvim.utils.buffer_ops import get_today_buffers

# nvim.fs.clip(get_today_buffers(Buffers()))



        


s = """
    
---
frontmatter: true
formatter_version: 1
---


2025-02-12 i think it is actually impossible for me to get a dishwasher job in manhattan
  
"""

class NoteFormatterV1:
    """
        ----------------------------------------
        this formatter was written on 2025-05-10
        ----------------------------------------

        items are split by isodate: 2025-05-10
        sometimes items are split by 
        "--------------------" or  "----------------------------------------"

        - items have optional title and frontmatter. 
        - items are allowed to be single lines.
          they are categorized as "singleton"

        this is a complicated parser with many twists and turns
    """

    def __init__(self, spec: NoteFormatterSpec = {}):
        self.spec = spec

    def fix_bullets_with_extra_spaces(s):
        s = re.sub('^- +', '- ', s, flags = re.M)
        return s

    def pre_process_text(s):
        s = self.fix_bullets_with_extra_spaces(s)


    def collect(self, s):
        r = '^(?=\d\d\d\d-\d\d-\d\d |-{3,})'
        items = split(s, r, flags=re.M)
        return items

    def parse(self, s):
        s, date = mget(s, '^\d\d\d\d-\d\d-\d\d')
        s = s.strip()
        if not s:
            return 
        first_line = None
        if date:
            t, fm = extract_frontmatter(s)
            if fm:
                return {
                    'date': date,
                    **fm,
                    'text': t 
                }

            s, first_line = mget(s, '.*')
            if not s.strip():
                return {
                    'date': date,
                    'type': 'singleton',
                    'text': first_line
                }
            else:
                s, fm = extract_frontmatter(s)
                if fm and first_line:
                    fm['title'] = first_line
                if fm:
                    return {
                        'date': date,
                        **fm,
                        'text': s 
                    }
                if first_line:
                    if is_word(first_line):
                        return {
                            'type': first_line,
                            'text': s,
                        }
                        
                return {
                    'type': 'uncategorized',
                    'text': s,
                }
        else:
            # split by dash lines
            s, fm = extract_frontmatter(s)
            if s: fm['text'] = s
            if fm:
                return {
                    **fm,
                }
            else:
                if not s:
                    return 
                return {
                    'type': 'uncategorized',
                    'text': s,
                }
    def run(self, s):
        items = self.collect(s)
        return self.post_process([self.parse(item) for item in items if exists(item)])
        
    def post_process(self, result):
        month1, year1 = dt__parse(result[0], 'month', 'year')
        month2, year2 = dt__parse(result[-1], 'month', 'year')
        
        name = f'{month1}_{year1}_to_{month2}_{year2}.json'
        outpath = f'~/data/kevnotes/{name}'
        data = {
            'content': result,
            'meta': {
                'author': 'Kevin Lee',
                'created_at': strftime(),
                'formatter_info': {
                    'version': self.spec['formatter_version'],
                    'name': kx.nameof(self),
                }
            }
        }


def static(func):
    caller = get_caller(1).function
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if result:
            wrapper_func = getattr(self, '_' + caller)
            params = get_parameters(wrapper_func)
            logger = getattr(self, 'logger', None) # logger is an instance of Logger
            if logger:
                logger.log(caller, prefix = 'calling')
            return wrapper_func(result) if params else wrapper_func() 
    return wrapper

class NoteFormatter:
    def __init__(self, src_path = '~/documents/notes/notes.txt', debug = False):
        self.src_path = src_path
        self.formatter = None # assigned in self.run
        self.debug = debug

    def _postprocess(self, dst_path):
        nvim.fs.cp(self.src_path, kx.fnamemodify(dst_path, ext = 'txt'))
        nvim.fs.write(self.src_path, results, open = True)
        
        print('performing posptorcess')
        return 111

    def _write(self, result):
        return nvim.fs.write(outpath, result, debug = self.debug)
        

    @staticmethod
    def postprocess(func):
        return static(func)

    @staticmethod
    def write(func):
        return static(func)

    @postprocess # then this happens (baesed on the result of write)
    @write # first this happens
    def run(self, s):
        s, fm = kx.extract_frontmatter(s)
        has_fm = fm.get('frontmatter') == True
        formatter_version = fm.get('formatter_version')

        if has_fm and formatter_version:
            classes = {
                1: NoteFormatterV1
            }
            self.formatter = classes[formatter_version](fm)
        elif self.debug:
            self.formatter = NoteFormatterV2()
        else:
            panic('not implemented yet')

        if hasattr(self.formatter, 'pre_process_text'):
            v = self.formatter.pre_process_text(s)
            if v:
                s = v
        return self.formatter.run(s)

def _dt__get_date_string(input_value: str):
    """
    Checks if the input is a string and returns it.
    If the input is a dictionary, looks for date-related fields and returns that value.
    
    Args:
        input_value: The input to check
        
    Returns:
        str or None: The string value or None if no date field found
    """
    # If input is already a string, return it directly
    if isinstance(input_value, str):
        return input_value
    
    # If input is a dictionary, look for date-related fields
    if isinstance(input_value, dict):
        # Common date field names to check (case-insensitive)
        date_field_names = [
            'date',
            'datetime',
            'timestamp',
            'created_at',
            'updated_at',
            'creation_date',
            'modification_date',
            'time',
            'start_date',
            'end_date',
            'published_at',
            'created_on',
            'modified_on',
            'date_created',
            'date_modified',
            'birth_date',
            'expiry_date'
        ]
        
        # Check for exact matches
        for field in date_field_names:
            if field in input_value:
                return str(input_value[field])
        
        # Check for case-insensitive matches
        input_keys_lower = {k.lower(): k for k in input_value.keys()}
        for field in date_field_names:
            if field.lower() in input_keys_lower:
                original_key = input_keys_lower[field.lower()]
                return str(input_value[original_key])
        
        # Look for any key that contains 'date' or 'time'
        for key in input_value:
            key_lower = key.lower()
            if 'date' in key_lower or 'time' in key_lower:
                return str(input_value[key])
    
    # Return None if no date-related field was found
    return None
def dt__parse(date_string, *args):
    date_string = _dt__get_date_string(date_string)
    import dateutil
    import calendar
    parsed_date = dateutil.parser.parse(date_string)
    component_map = {
        "year": parsed_date.year,
        "month": parsed_date.month,
        "day": parsed_date.day,
        "hour": parsed_date.hour,
        "minute": parsed_date.minute,
        "second": parsed_date.second,
        "weekday": parsed_date.weekday(),  # 0 = Monday, 6 = Sunday
       "month": calendar.month_name[parsed_date.month],  # Full month name
        "month_abbr": calendar.month_abbr[parsed_date.month],  # Abbreviated month name
        "weekday": calendar.day_name[parsed_date.weekday()],  # Full weekday name
        "weekday_abbr": calendar.day_abbr[parsed_date.weekday()],  # Abbreviated we
        # "date": parsed_date.date(),        # returns datetime.date object
        # "time": parsed_date.time(),        # returns datetime.time object
        # "datetime": parsed_date,           # returns full datetime object
        # "timestamp": parsed_date.timestamp(), # returns UNIX timestamp
        # "isoweekday": parsed_date.isoweekday(), # 1 = Monday, 7 = Sunday
    }
    
    return list(component_map[arg.lower()] for arg in args)


# NoteFormatter().run(s)
# print(dt__parse({'date': '6/6/25'}, 'month', 'year', 'day', 'weekday'))

"""
turn dt__parse into kx.dt.parse()
turn writefile into kx.fs.write
mod stuff into kx.mod.reload
a gradual introduction of these things i guess
"""
def readnote(*queries):
    s = readfile('/home/kdog3682/documents/notes/notes.txt')
    r = '^\d\d\d\d-\d\d-\d\d'
    base = split(s, r, flags = re.M)
    # aggregate it up
    if queries:
        store = []
        for item in reversed(base):
            a, b = split_once(item, '\n')
            if a in queries:
                store.append(b)
                if len(store) == len(queries):
                    return smallify(store)
    else:
        return base[-1]



# https://docs.google.com/spreadsheets/d/1nbGoHvqSvtVetqkgYp9nHEtmHC4ck0ab7BKgkBoKnoI/edit?gid=2069222857#gid=2069222857 # this is the my daily tracker spreadsheet
# form = NoteFormatter(debug = True)
# kx.pprint(form.run(PROMPT_LIBRARY))

