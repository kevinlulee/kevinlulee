import re
import yaml
import textwrap
from .ao import to_array

def bracket_wrap(
    items, bracket_type: str = "()", indent: int = 4, delimiter=", ", newlines = False,
) -> str:
    brackets = {
        "()": ("(", ")"),
        "[]": ("[", "]"),
        "[[]]": ("[[", "]]"),
        "{}": ("{", "}"),
        '"': ('"', '"'),
        "'": ("'", "'"),
        "'''": ("'''", "'''"),
        '"""': ('"""', '"""'),
        "``": ("`", "`"),
        "```": ("```", "```"),
        "({})": ("({", "})"),
        "([])": ("([", "])"),
    }

    if newlines and delimiter == ', ':
        delimiter = ',\n'
    open_bracket, close_bracket = brackets[bracket_type]
    text = delimiter.join(str(el) for el in to_array(items))
    if re.search("^[\(\{\[]\n", text):
        return open_bracket + text + close_bracket
    indented_text = textwrap.indent(text, " " * indent)
    return f"{open_bracket}\n{indented_text}{close_bracket}"


def extract_frontmatter(text: str):
    """
    Extracts YAML frontmatter from the beginning of a text and returns it as a dictionary,
    along with the remaining content.

    Frontmatter must start at the beginning and follow YAML format (key-value pairs or lists).
    It ends at the first empty line or a non-matching line.

    Returns:
        tuple[str, dict]: (content, frontmatter_dict)

    Edge Cases:
    - If no valid frontmatter is found, returns the full text as content and an empty dictionary.
    - If improperly formatted, YAML parsing may fail or return unexpected results.
    """
    frontmatter_pattern = re.compile(r'^\s*\w+:|^\s+-')
    
    lines = text.split('\n')
    if not lines or not frontmatter_pattern.match(lines[0]):
        return text, {}
    
    frontmatter_lines = []
    content_start = 0
    
    for i, line in enumerate(lines):
        if not line.strip():  # Empty line breaks frontmatter
            content_start = i + 1
            break
        if frontmatter_pattern.match(line):
            frontmatter_lines.append(line)
        else:
            content_start = i
            break
    
    frontmatter_text = '\n'.join(frontmatter_lines)
    frontmatter = yaml.safe_load(frontmatter_text) if frontmatter_text else {}
    
    content = '\n'.join(lines[content_start:])
    return content, frontmatter



def tabs_to_spaces(s):
    return s.replace('\t', '    ')
def _toggle_comment(text: str, filetype: str) -> str:
    """
    Toggle comments in code text based on the file type.
    Adds a comment if the text is not commented, removes the comment if it is.
    Preserves indentation and handles both single-line and block comments.
    
    Args:
        text (str): The text to toggle comments for
        filetype (str): The programming language/file type (e.g., 'python', 'javascript')
        
    Returns:
        str: The text with comments toggled
        
    Examples:
        >>> toggle_comment("hello world", "python")
        "# hello world"
        >>> toggle_comment("# hello world", "python")
        "hello world"
        >>> toggle_comment("<div>", "html")
        "<!-- <div> -->"
    """
    # Dictionary mapping file types to their comment symbols
    comment_symbols = {
        'python': '#',
        'javascript': '//',
        'java': '//',
        'c': '//',
        'cpp': '//',
        'csharp': '//',
        'typescript': '//',
        'html': '<!--',
        'css': '/*',
        'sql': '--',
        'ruby': '#',
        'php': '//',
        'rust': '//',
        'swift': '//',
        'go': '//',
        'perl': '#',
        'r': '#',
        'matlab': '%',
        'shell': '#',
        'bash': '#',
        'powershell': '#',
        'yaml': '#',
        'toml': '#',
        'ini': ';',
        'lua': '--',
        'haskell': '--',
    }
    
    # Get the comment symbol for the given filetype, default to '#' if unknown
    symbol = comment_symbols.get(filetype.lower(), '#')
    
    # Strip whitespace from the beginning while preserving it for later
    stripped_text = text.lstrip()
    leading_space = text[:len(text) - len(stripped_text)]
    
    # Handle HTML-style comments
    if symbol == '<!--':
        if stripped_text.startswith('<!--') and stripped_text.endswith('-->'):
            # Remove HTML comment
            return leading_space + stripped_text[4:-3].strip()
        # Add HTML comment
        return leading_space + '<!-- ' + stripped_text + ' -->'
    
    # Handle CSS-style block comments
    if symbol == '/*':
        if stripped_text.startswith('/*') and stripped_text.endswith('*/'):
            # Remove CSS comment
            return leading_space + stripped_text[2:-2].strip()
        # Add CSS comment
        return leading_space + '/* ' + stripped_text + ' */'
    
    # Handle single-line comments
    if stripped_text.startswith(symbol):
        # Remove comment
        return leading_space + stripped_text[len(symbol):].lstrip()
    # Add comment
    return leading_space + symbol + ' ' + stripped_text

def toggle_comment(text: str, filetype: str) -> str:
    """
    Toggle comments for multiple lines of text while preserving empty lines.
    
    Args:
        text (str): Multi-line text to toggle comments for
        filetype (str): The programming language/file type
        
    Returns:
        str: The text with comments toggled on all non-empty lines
        
    Examples:
        >>> text = "def hello():\\n    print('world')\\n\\n    return True"
        >>> print(batch_toggle_comment(text, "python"))
        # def hello():
        #     print('world')
        
        #     return True
    """
    lines = text.splitlines()
    result = []
    
    for line in lines:
        # Preserve empty lines
        if not line.strip():
            result.append(line)
        else:
            result.append(_toggle_comment(line, filetype))
    
    return '\n'.join(result)





TEMPLATER_PATTERN = re.compile(r'''
    # ([ \t]*(?:[-*•] *)?)? # Optional leading whitespace and indentation
    ((?:^|\n)\s*(?:[-*•]\s+)?)?   
    \$                  # Literal $ symbol to start template variable
    (?:
        (\w+\(.*?\))    # Callable function with arguments
        |               # OR
        ({.*?})         # Bracket expression
        |               # OR
        (\w+)           # Simple word variable
        (,?)            # optional comma
        (?:             # Optional non-capturing group
            \[(\d+)(?::(\d+))?\]   # Bracket indexing [index] or slicing [start:end]
        )?
        (?:             # Optional non-capturing group
            :(\w+)      # Fallback value after :
        )?
    )
''', flags=re.VERBOSE)


class Templater:
    def __init__(self):
        self.scope = {}
        self.spacing = ''
    
    def replace(self, match):
        groups = match.groups()
        # print(match)
        # print(groups)
        spaces, callable_expr, bracket_expr, word, comma, start_index, end_index, fallback = groups
        self.spacing = spaces or ''
        self.comma = comma or ''
        
        try:
            if callable_expr:
                return self._handle_callable(callable_expr)
            elif bracket_expr:
                return self._handle_bracket(bracket_expr)
            elif word:
                return self._handle_word(word, start_index, end_index, fallback)
        except Exception as e:
            return fallback if fallback is not None else str(e)
        
        return ''

    def _handle_callable(self, expr):
        try:
            a, b = re.split('(?=\()', expr, maxsplit=1)
            g = self.getter(a)
            if g:
                return g + b
            return str(eval(expr, {}, self.scope))
        except Exception as e:
            return f"Error evaluating callable: {e}"

    def _handle_bracket(self, expr):
        try:
            return str(eval(expr.strip('{}'), {}, self.scope))
        except Exception as e:
            return f"Error evaluating bracket expression: {e}"
    
    def _handle_word(self, word, start_index, end_index, fallback):
        value = self.getter(word, fallback)
        if isinstance(value, (list, tuple)):
            spacing = self.spacing or '\n'
            return ''.join([f'{spacing}{item}{self.comma}' for item in value])
            prefix = ''
            # print([self.spacing])
            if self.spacing.strip().startswith('-'):
                prefix = '- '
            elif self.spacing.strip().startswith('•'):
                prefix = '• '
            indent = self.spacing.replace('-', '').replace('•', '') 
            # the indent has a newline ... thats why this works
            if not indent.startswith("\n"):
                indent = "\n" + indent
            # print()
            args = [f"{indent}{prefix}{item}" for item in value]
            # print(args) # TEMPORARY_PRINT_LOG
            return ''.join(args)

        if "\n" in self.spacing:
            spaces = self.spacing[1:]
            return  '\n' + tabs_to_spaces(textwrap.indent(str(value), spaces))
        return str(value)
        print([self.spacing])
        return self.spacing + str(value)
    
    def format(self, s, scope=None):
        self.scope = scope or {}
        self.getter = self.scope.get if isinstance(self.scope, dict) else lambda x,y = None: getattr(self.scope, x, y)
        input_text = textwrap.dedent(s).strip()
        return re.sub(TEMPLATER_PATTERN, self.replace, input_text)

templater = Templater().format

def join_text(contents):
    o = ''
    for content in contents:
        s = content.strip()
        if '\n' in s:
            if o.endswith('\n\n'):
                o += f'{s}\n\n'
            else:
                o += f'\n{s}\n\n'
        else:
            o += f'{s}\n'
    return o

def dash_split(text, delim_length=3, trim=True, filter=True):
    """
    Splits text on a delimiter of dashes spanning an entire line.
    
    Parameters:
        text (str): The input text to split.
        delim_length (int): The minimum number of dashes required to split the text.
        trim (bool | tuple): If True, trims both sides. If a tuple, the first element trims left, the second trims right.
        filter (bool): If True, filters out empty parts after processing.
    
    Returns:
        list: List of split text segments.
    """
    split_chunks = re.split(rf"^\-{{{delim_length},}}$", text, flags=re.MULTILINE)
    
    if isinstance(trim, bool):
        trim_left, trim_right = trim, trim
    else:
        trim_left, trim_right = trim
    
    def process_chunk(chunk):
        chunk = chunk.lstrip() if trim_left else chunk
        chunk = chunk.rstrip() if trim_right else chunk
        
        if filter and not chunk.strip():
            return None
        
        return chunk
    
    result_chunks = [process_chunk(chunk) for chunk in split_chunks]
    
    return [chunk for chunk in result_chunks if chunk is not None]
# __all__ = ['toggle_comment', 'templater', 'join_text', 'dash_split']

template = """
    try:
        abc 


        $expr
    except Exception as e:
        error_handler(e)
"""

# print(templater(template, {'expr': 'def foo()\n\thi\n\tbye'}))

arguments = ['hiii', 'byeee']
template =f'''
            please provide {len(arguments)} arguments separated by commas'
            ---
            - $arguments
        '''
# print(templater(template, {'arguments': arguments}))

# print(re.search(TEMPLATER_PATTERN, "- $arguments").groups())
