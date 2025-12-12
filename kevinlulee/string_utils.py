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


def get_indent(text: str, tab_width = 4) -> int:
    """
    Gets the indentation level of the first non-empty line in the text.
    Each level corresponds to 4 spaces (e.g., 0 for no indentation, 1 for 4 spaces, etc.).

    Args:
        text: The text to analyze.

    Returns:
        The indentation level (0, 1, 2, 3, or 4).
    """
    for line in text.splitlines():
        # Calculate the number of leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        # Calculate the indentation level (each level is 4 spaces)
        indent_level = leading_spaces // tab_width
        # Ensure the result is within 0–4
        return min(indent_level, tab_width)
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

# def trimdent(s):
#     return textwrap.dedent(str(s)).strip() if s else ''

def trimdent(text: str) -> str:
    """Smart trim and dedent: removes common indentation and trailing whitespace."""
    if text is None or text == '':
        return ''
    lines = str(text).splitlines()
    
    # Remove leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    
    # Remove trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()
    
    if not lines:
        return ""
    
    # Find minimum indentation (ignoring blank lines)
    min_indent = float('inf')
    for line in lines:
        if line.strip():  # Only consider non-empty lines
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)
    
    if min_indent == float('inf'):
        min_indent = 0
    
    # Remove common indentation and trailing whitespace from each line
    result = []
    for line in lines:
        if line.strip():  # Non-empty line
            result.append(line[min_indent:].rstrip())
        else:  # Blank line - preserve it as empty
            result.append("")
    
    return "\n".join(result)

def dash_case(s):
    if s.isupper():
        return s
    if len(s) == 1:
        return s
    s = re.sub(r"([a-z])([A-Z])", r"\1-\2", s)  # Convert camelCase to kebab-case
    s = re.sub(r"_+", "-", s)  # Replace underscores with dashes
    return s.lower()  # Convert to lowercase

def split(s, r="\s+", flags=0, maxsplit = 0):
    if flags == 0 and isinstance(r, str) and r.startswith('^'):
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



def tabs_to_spaces(s):
    return s.replace("\t", "    ")

def to_spaces(ind):
    return " " * int(ind) if isinstance(ind, (float, int)) else ind
def indent(s: str, indentation: int | str) -> str:
    if not indentation:
        return s

    t = tabs_to_spaces(str(s))
    prefix = to_spaces(indentation)
    lines = t.split('\n')

    store = []
    for line in lines:
        store.append(prefix + line)

    return "\n".join(store)

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
    if isinstance(s, (list, tuple)):
        return s
    
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
    if isinstance(key, str):
        if key.startswith('\n'):
            return f'{key}{s}{key}'
            
        if test(key, '^[=-]{3,}'):
            return f'{key}\n{str(s)}\n{key}'
        if test(key, '^<'):
            ckey = key.replace('<', '</')
            if newline:
                return f'{key}\n{str(s)}\n{ckey}'
            else:
                return f'{key}{str(s)}{ckey}'
            
        
    
    a, b = key if isinstance(key, (list, tuple)) else (brackets.get(key) or split_in_half(key))
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

def oxford_comma(items, conj="and", serial_comma=True):
    """
    Join a sequence with an Oxford comma.
      []                -> ""
      ["A"]             -> "A"
      ["A","B"]         -> "A and B"
      ["A","B","C"]     -> "A, B, and C"   (serial_comma=True)
                          "A, B and C"     (serial_comma=False)
    """
    items = [str(x) for x in items if str(x) != ""]
    n = len(items)
    if n == 0:
        return ""
    if n == 1:
        return items[0]
    if n == 2:
        return f"{items[0]} {conj} {items[1]}"
    if serial_comma:
        return f"{', '.join(items[:-1])}, {conj} {items[-1]}"
    else:
        return f"{', '.join(items[:-1])} {conj} {items[-1]}"

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


def remove_markdown_comments(s):
    r = r'^ *(?:\<\!--|//+) +\S.*\n*'
    return re.sub(r, '', s, flags=re.M)

def remove_comments(s):
    r = r'(^|\S) *(?:<!--|[#/]+) +\S.*$'
    return re.sub(r, r'\1', s, flags=re.M)
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
    b = r'(?<![\w\u4e00-\u9fff])' if boundary else ''
    middle = f'[{"".join(keys)}]' if all(len(k) == 1 for k in keys) else f'(?:{"|".join(keys)})'
    regex = f'{b}{middle}{b}'

    def replacer(x):
        key = x.group(0)
        return ref.get(key)
        
    return re.sub(regex, replacer, s, flags = flags)
def replacef(regex, replacement, flags = 0, count = 0):
        
    def wrapper(s):
        return re.sub(regex, replacement, s, flags = flags, count = count)

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


def highlight_alias_with_bracket(word: str, alias: str) -> str:
    """
    Highlight the first case-insensitive occurrence of `alias` in `word`.
    - If `alias` appears contiguously, wrap that substring once: [ ... ].
    - Else, treat `alias` as a subsequence and wrap each matched character.
    If no complete match, return `word` unchanged.
    """
    if not alias:
        return word

    lw, la = word.lower(), alias.lower()

    # 1) Prefer a contiguous match if present
    i = lw.find(la)
    if i != -1:
        j = i + len(alias)
        return word[:i] + f"[{word[i:j]}]" + word[j:]

    # 2) Otherwise, find the first subsequence match (greedy)
    pos = 0
    idxs = []
    for ch in la:
        k = lw.find(ch, pos)
        if k == -1:
            return word  # no complete subsequence match
        idxs.append(k)
        pos = k + 1

    match_set = set(idxs)
    return "".join(f"[{c}]" if idx in match_set else c for idx, c in enumerate(word))


def strip_quotes(s: str) -> str:
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    return s


def depluralize_arg(word):
    """
    Attempt to convert a plural word to its singular form.
    
    Args:
        word (str): The word to be depluralized
    
    Returns:
        str: The depluralized word or the word 'arg'
    """
    # Handle irregular plurals first
    irregular_plurals = {
        'children': 'child',
        'people': 'person',
        'men': 'man',
        'women': 'woman',
        'teeth': 'tooth',
        'feet': 'foot',
        'mice': 'mouse',
        'geese': 'goose'
    }
    
    if not word:
        return 
    word = word.split('.')[-1]
    # Check if the word is in irregular plurals
    if word.lower() in irregular_plurals:
        return irregular_plurals[word.lower()]
    
    # Convert to lowercase for case-insensitive processing
    original = word
    word = word.lower()
    
    # Handle words ending in 'ies'
    if word.endswith('ies'):
        # Special case for words like 'parties' -> 'party'
        return original[:-3] + 'y'
    
    # Handle words ending in 'es'
    if word.endswith(('ses', 'xes', 'ches', 'shes')):
        # Remove 'es' for words like 'classes', 'boxes', 'churches', 'dishes'
        return original[:-2]
    
    # Handle words ending in 's'
    if word.endswith('s'):
        # Remove trailing 's' for most words
        return original[:-1]
    
    return original

def escape_newlines(s):
    return re.sub("\n", '\\\\n', s)


def escape_typst_newlines(s):
    return re.sub("\n", '\\\n', s)


def trim(x):
    return x.strip() if isinstance(x, str) else x


def repeatedly_eat(text: str, pattern: str) -> tuple[str, list]:
    """
    Repeatedly consume a regex pattern from the start of a string until no more matches are found.

    Args:
        text: The input string to process
        trim: 

    Returns:
        List of all matched strings in order of appearance
        along with the remaining string

    Example:
        >>> eat_regex("abc123def456hi", r'[a-z]+\d+')
        (['abc123', 'def456'], "hi")
    """

    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    matches = []
    remaining = text.strip()

    while remaining:
        match = pattern.match(remaining)
        if not match:
            break

        m = get_match(match)
        matches.append(m)
        remaining = remaining[len(match.group(0)):]
        remaining = remaining.lstrip()
        remaining = re.sub('^,+ *', '', remaining)

    return remaining, matches 


import re

def pluralize(word: str) -> str:
    """
    A 'smart' function to calculate the plural form of a singular English noun,
    with specialized logic for words ending in '-o' based on common rules and exceptions.

    NOTE: English pluralization is highly irregular. This function covers common
    rules but will not be accurate for every word.

    Args:
        word: The singular English noun (e.g., 'hero', 'radio', 'child').

    Returns:
        The computed plural form (e.g., 'heroes', 'radios', 'children').
    """

    # 1. Handle common irregular plurals (non-rule-based)
    # This list is highly abbreviated for demonstration.
    irregular_plurals = {
        'man': 'men',
        'woman': 'women',
        'child': 'children',
        'goose': 'geese',
        'tooth': 'teeth',
        'foot': 'feet',
        'mouse': 'mice',
        'person': 'people',
        'die': 'dice',
        'quiz': 'quizzes', # The 'z' rule exception
    }
    
    # Words with the same plural and singular forms
    uncountable = ['sheep', 'series', 'species', 'deer', 'moose', 'fish', 'aircraft']

    lower_word = word.lower()

    if lower_word in uncountable:
        return word

    if lower_word in irregular_plurals:
        # Preserve capitalization of the input word (simple attempt)
        if word.istitle():
            return irregular_plurals[lower_word].capitalize()
        return irregular_plurals[lower_word]

    # 2. Handle the specific and complex '-o' rule
    if lower_word.endswith('o'):
        
        # A. Common exceptions that ADD -s (often abbreviations or foreign words)
        # These are usually preceded by a consonant, but still take -s
        o_exceptions_s = [
            'photo', 'piano', 'halo', 'solo', 'memo', 'logo', 'taco',
            'motto', 'soprano', 'folio', 'kilo', 'dynamo', 'pro',
        ]

        # B. Words ending in '-o' preceded by a VOWEL (always add -s)
        # e.g., radio, studio, kangaroo, zoo
        # We check if the second-to-last letter is a vowel (a, e, i, o, u)
        if len(lower_word) >= 2 and lower_word[-2] in 'aeiou':
            return word + 's'

        # C. Apply the 'exceptions' list
        if lower_word in o_exceptions_s:
            return word + 's'

        # D. Dual plurals (Volcano can be 'volcanos' or 'volcanoes').
        # We'll default to the historically older/more formal '-es' for these.
        o_dual_plurals = ['volcano', 'cargo', 'memento', 'mosquito', 'zero']
        if lower_word in o_dual_plurals:
            return word + 'es'


        # E. The remaining words ending in '-o' (preceded by consonant)
        # generally take '-es' (e.g., potato, hero, echo, tomato)
        return word + 'es'

    # 3. Handle other general English pluralization rules

    # Words ending in s, x, z, ch, sh add -es
    if lower_word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        # Note: 'quiz' is already handled in irregular, as it needs 'zz'
        return word + 'es'

    # Words ending in consonant + 'y' change 'y' to 'ies'
    # e.g., 'baby' -> 'babies', but 'key' -> 'keys'
    if lower_word.endswith('y') and lower_word[-2] not in 'aeiou':
        return word[:-1] + 'ies'

    # Words ending in 'f' or 'fe' change to 'ves' (e.g., leaf -> leaves)
    if lower_word.endswith(('f', 'fe')):
        if lower_word.endswith('f'):
            return word[:-1] + 'ves'
        # ends with 'fe'
        return word[:-2] + 'ves'

    # 4. Default rule: Add -s
    return word + 's'

def possibly_pluralize_unit(unit: str, num: int) -> str:
    """
    Returns the appropriate singular or plural form of a unit based on a number.
    This function "inflects" the unit based on the quantity.
    
    e.g., inflect_unit('cat', 1) -> 'cat'
    e.g., inflect_unit('cat', 5) -> 'cats'

    Args:
        unit: The singular unit noun (e.g., 'mile', 'person').
        num: The number associated with the unit.

    Returns:
        The corrected singular or plural unit string.
    """
    if num == 1:
        m = unit
    else:
        m = pluralize(unit)

    return f'{num} {m}'
