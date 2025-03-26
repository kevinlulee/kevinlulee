import re
import textwrap

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
    # ((?:^|\n)[ \t]+(?:[-*•] +)?)?   
    ((?:^|\n)[ \t]+(?:[-*•][\t ]+)?)?   
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
            return str(eval(expr, {}, self.scope))
        except Exception as e:
            return f"Error evaluating callable: {e}"

    def _handle_bracket(self, expr):
        try:
            return str(eval(expr.strip('{}'), {}, self.scope))
        except Exception as e:
            return f"Error evaluating bracket expression: {e}"
    
    def _handle_word(self, word, start_index, end_index, fallback):
        value = self.scope.get(word, fallback)
        if isinstance(value, (list, tuple)):
            return ''.join([f'{self.spacing}{item}{self.comma}' for item in value])
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

        return str(value)
    
    def format(self, s, scope=None):
        self.scope = scope or {}
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
__all__ = ['toggle_comment', 'templater', 'join_text']
