"""String-related utilities for text manipulation and regex operations.

This module provides functions for grouping items by keys, extracting matches from
strings using regular expressions, and modifying strings based on regex patterns.

Functions:
    - group: Groups items by their first element into a dictionary.
    - matchstr: Extracts regex matches from a string, returning groups or the full match.
    - mget: Extracts the first regex match and returns the modified string and match.
"""

from typing import List, Tuple, Union, Any
from kevinlulee.validation import test
import re
import textwrap


def matchstr(s: str, reg: str, flags: int = 0) -> Union[str, Tuple[str, ...], None]:
    """Extracts the string match from a regex search on a string.

    Args:
        s: The string to search within.
        reg: The regular expression pattern to search for.
        flags: Optional regex flags to modify the search behavior, e.g., re.IGNORECASE.

    Returns:
        The matched string if the regex has no groups, otherwise a tuple of captured groups.
        Returns None if no match is found.
        If the regex has a single group, returns the string of the first group.

    Example:
        >>> matchstr("The price is $10.99", r"\$(\d+\.\d+)")
        '10.99'

        >>> matchstr("Name: John, Age: 30", r"Name: (\w+), Age: (\d+)")
        ('John', '30')
    """
    if not s:
        return 
    match = re.search(reg, str(s), flags=flags)
    return get_match(match)

def get_match(match):
    
    if match:
        if match.groups():
            if len(match.groups()) == 1:
                return match.group(1)
            else:
                return match.groups()
        else:
            return match.group(0)
    else:
        return None

def mget(s: str, pattern: str, flags: int = 0) -> Tuple[str, Union[str, None]]:
    """Extracts the first match of a regular expression pattern from a string,
    returning the modified string with the matched portion removed and the matched string itself.

    Args:
        s: The input string to search within.
        pattern: The regular expression pattern to search for.
        flags: Optional regular expression flags (e.g., re.IGNORECASE, re.MULTILINE).

    Returns:
        A tuple containing:
            - The modified string with the first match of the pattern removed.
            - The matched substring if a match was found; otherwise, None.

    Example:
        >>> mget("hello world", "world")
        ('hello ', 'world')

        >>> mget("hello world", "notfound")
        ('hello world', None)

        >>> mget("Hello World", "hello", re.IGNORECASE)
        (' World', 'Hello')
    """
    match = matchstr(s, pattern, flags=flags)
    if not match:
        return s, None

    return re.sub(pattern, '', s, 1, flags=flags), match


def get_indent(text: str) -> int:
    """
    Gets the indentation level of the first non-empty line in the text.
    Each level corresponds to 4 spaces (e.g., 0 for no indentation, 1 for 4 spaces, etc.).

    Args:
        text: The text to analyze.

    Returns:
        The indentation level (0, 1, 2, 3, or 4).
    """
    for line in text.splitlines():
        if line.strip():  # Check if the line is not empty
            # Calculate the number of leading spaces
            leading_spaces = len(line) - len(line.lstrip())
            # Calculate the indentation level (each level is 4 spaces)
            indent_level = leading_spaces // 4
            # Ensure the result is within 0–4
            return min(indent_level, 4)
    return 0  # Default to 0 if all lines are empty



def capitalize(s):
    if not s:
        return s
    return s[0].upper() + s[1:]

def uncapitalize(s):
    return s[0].lower() + s[1:]


def snake_case(s):
    if "_" in s:
        return s
    s = re.sub("(?<=[a-z])(?=[A-Z])", "_", s)
    s = re.sub("\W+", "_", s)
    s = s.lower()
    return s

def trimdent(s):
    return textwrap.dedent(str(s)).strip() if s else ''


def dash_case(s):
    if len(s) == 1:
        return s
    s = re.sub(r"([a-z])([A-Z])", r"\1-\2", s)  # Convert camelCase to kebab-case
    s = re.sub(r"_+", "-", s)  # Replace underscores with dashes
    return s.lower()  # Convert to lowercase

def split(s, r="\s+", flags=0, maxsplit = 0):
    if flags == 0 and r.startswith('^'):
        flags = re.M
    base = re.split(r, str(s).strip(), flags=flags, maxsplit = maxsplit)
    items = [s.strip() for s in base if s.strip()]
    return items

def split_once(s, r="\s+"):
    a = split(s, r, maxsplit=1)
    return a + [""] if len(a) ==  1 else a


def testf(x, flags=0, anti=0, key=0):
    if not x:
        return None
    fn = x

    if isinstance(x, (int, float)):
        fn = lambda s: s == x
    elif isinstance(x, str):
        regex = re.compile(x)
        fn = lambda s: test(s, regex, flags=flags)
            
    elif isinstance(x, re.Pattern):
        fn = lambda s: test(s, x, flags=flags)

    elif isinstance(x, (list, tuple)):
        fn = lambda s: s in x

    if anti and key:
        return lambda x: not fn(x[key])
    elif anti:
        return lambda x: not fn(x)
    elif key:
        return lambda x: fn(x[key])
    else:
        return fn

def camel_case(s):
    parts = split(s, r"[\W_]+")
    return uncapitalize("".join([capitalize(part) for part in parts]))

def pascal_case(s):
    if not s: return ''
    return capitalize(camel_case(s))



def add_quotes(s):
    if s[0].isalpha():
        return f'"{s}"'
    else:
        return s




def to_spaces(ind):
    return " " * int(ind) if isinstance(ind, (float, int)) else ind
def indent(s: str, ind: int) -> str:
    if not ind:
        return s
    return textwrap.indent(str(s), to_spaces(ind))

def newline_indent(s, ind = 4):
    indented = indent(s, ind)
    return "\n" + indented.rstrip()

def split_in_half(s):
    """
    Splits a string exactly in half.
    
    Args:
        s (str): Input string with even number of characters
        
    Returns:
        tuple: Two strings of equal length
        
    Raises:
        ValueError: If string length is odd
    """
    if len(s) % 2 != 0:
        raise ValueError("String must have even number of characters")
    
    mid = len(s) // 2
    return s[:mid], s[mid:]

def parens(s, key = '()', newline = False, ind = 4, leading_newline = False):
    brackets = {
        "()": ("(", ")"),
        "[]": ("[", "]"),
        "[[]]": ("[[", "]]"),
        "{}": ("{", "}"),
        '"': ('"', '"'),
        '""': ('"', '"'),
        "'": ("'", "'"),
        "''": ("'", "'"),
        ":": (":", ""),
        "'''": ("'''", "'''"),
        '"""': ('"""', '"""'),
        "``": ("`", "`"),
        "```": ("```", "```"),
        "": ("", ""),
        "$": ("$", "$"),
        "$$$": ("$$$", "$$$"),
        "---": ("---\n", "\n---"),
        "```": ("```", "```"),
        "({})": ("({", "})"),
        "([])": ("([", "])"),
    }
    a, b = brackets.get(key) or split_in_half(key)
    if newline:
        top_newline = "\n" if leading_newline and "\n" in s else ''
        return a + top_newline + newline_indent(s, ind) + "\n" + b
    return a + str(s) + b



def quotify(s):
    if s.startswith('"'):
        return s
    return f'"{s}"'



def uncomment(s, filetype = None):
    r = '^( *)(?:#+|//+|"|--+) +'
    return re.sub(r, lambda x: x.group(1), s, flags=re.M)



def prefix_join(prefix, key, delimiter = '_'):
    if not key:
        return ''
    prefix = "" if not prefix else prefix + delimiter
    return prefix + key

def suffix_join(key, suffix, delimiter = '_'):
    if suffix:
        return f'{key}{delimiter}{suffix}'
    else:
        return key



def pluralize(s):
    return s if s.endswith("s") else s + "s"

def count_words(text: str, include_emojis: bool = True) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        include_emojis: Whether to include emojis in word count
        
    Returns:
        Number of words
    """
    if not text:
        return 0
    
    # Remove emojis if not including them
    if not include_emojis:
        # Remove emojis using regex (basic emoji pattern)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+", re.UNICODE)
        text = emoji_pattern.sub(r'', text)
    
    # Split by whitespace and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)
def count_sentences(text: str) -> int:
    """
    Count sentences in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of sentences
    """
    if not text:
        return 0
    
    # Split by sentence endings and filter out empty strings
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    return len(sentences)


def oxford_or(names):
    """
    sam, bob, or galpha
    """
    s = ''
    names = list(names)
    max = len(names) - 1
    for i, name in enumerate(names):
        if i == 0:
            pass
        elif i == max:
            s+= ', '
        else:
            s+= ', or'
        s+= name

    return s


def remove_quotes(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    elif s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    else:
        return s


def remove_commented_lines(s, filetype=None):
    r = '^( *)(?:#+|//+|") *.*'
    return re.sub(r, "", s, flags=re.M)



def match_case(original, replacement):
        if original.isupper():
            return replacement.upper()
        elif original[0].isupper():
            return replacement.capitalize()
        else:
            return replacement

def get_number_from_string(text):
    """Extract the first number (int or float) from a string."""
    # Look for numbers (including decimals and negative numbers)
    match = re.search(r"-?\d+\.?\d*", text)
    if match:
        num_str = match.group()
        # Convert to int if it's a whole number, otherwise float
        if "." in num_str:
            return float(num_str)
        else:
            return int(num_str)
    return None


def escape_quotes(s, quote_type = '"', num_backslashes = 1):
    quotes = {
        '"': '"',
        '""': '"',
        "'": "'",
        "''": "''",
    }
    quote_type = quotes[quote_type]
    backslashes = '\\' * (num_backslashes + 1)
    return re.sub(quote_type, backslashes + quote_type, s)


def mgetall(s, regex, flags = 0):
    # string_utils
    matches = []
    
    def replacer(match):
        matches.append(get_match(match))
        return ''
        
    result = re.sub(regex, replacer, s.strip(), flags=flags).strip()
    return result, matches

def re_wrap(iterable, template=""):
    ref = {
        "": "(?:$1)",
        "start": "^(?:$1)\\b",
        "b": "\\b(?:$1)\\b",
        "bc": "\\b($1)\\b",
    }
    s = ref.get(template, template)
    keys = list(iterable)

    def replacer(x):
        key = x.group(0)
        start, end = x.span()
        prev = s[start - 1] if s and start > 0 else None
        # next = s[end + 1] if s and end < length else None
        if prev == "[":
            assert all(len(key) == 1 for key in keys)
            return "".join(keys)
        else:
            symbols = [re.escape(key) for key in keys]
            return "|".join(symbols)
        
    length = len(s)
    return re.sub("\$1", replacer, s)



def dreplace(s, ref, boundary = True, flags = 0):
    keys = list(ref)
    b = '\\b' if boundary else ''
    middle = f'[{"".join(keys)}]' if all(len(k) == 1 for k in keys) else f'(?:{"|".join(keys)})'
    regex = f'{b}{middle}{b}'

    def replacer(x):
        key = x.group(0)
        return ref.get(key)
        
    return re.sub(regex, replacer, s, flags = flags)
def replacef(regex, replacement, flags = 0):
        
    def wrapper(s):
        return re.sub(regex, replacement, s, flags = flags)

    return wrapper


def remove_starting_slash(s):
    return re.sub('^/', '', str(s))
def remove_ending_slash(s):
    return re.sub('/$', '', str(s))

def get_words(s):
    return re.findall('\\b[a-zA-Z]\w+', s)


def regex_word_boundary(s: str):
    a = s[0]
    b = s[-1]
    _boundary_pat = re.compile(r"[_\W]")
    boundary_start = re.search(_boundary_pat, s[0])
    boundary_end = re.search(_boundary_pat, s[-1])
    a = "" if boundary_start else "(?:(?<=[\s\W])|^)"
    b = "" if boundary_end else "(?:(?=[\s\W])|$)"
    # s = re.sub('(?<=[a-z])(?=[a-z])', '_?', s)
    return a + s + b
