"""String-related utilities for text manipulation and regex operations.

This module provides functions for grouping items by keys, extracting matches from
strings using regular expressions, and modifying strings based on regex patterns.

Functions:
    - group: Groups items by their first element into a dictionary.
    - matchstr: Extracts regex matches from a string, returning groups or the full match.
    - mget: Extracts the first regex match and returns the modified string and match.
"""

from typing import List, Tuple, Union, Any
import re

def group(items: List[Tuple[str, Any]]) -> dict:
    """Groups items by their first element.

    Args:
        items: A list of tuples to group. Each tuple should be of the form (key, value).

    Returns:
        A dict mapping the key to lists of grouped values.

    Raises:
        AssertionError: If input is not a list or tuple.
        ValueError: If items in list are not tuples.

    Example:
        >>> group([('a', 1), ('b', 1), ('c', 2)])
        {'a': [1], 'b': [1], 'c': [2]}
    """
    assert isinstance(items, (list, tuple)), "Input must be a list or tuple."

    result = {}
    for item in items:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("Items in the list must be tuples/lists of length 2.")
        iden, value = item
        result.setdefault(iden, []).append(value)
    return result

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
    match = re.search(reg, s, flags=flags)
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


def getindent(text: str) -> int:
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


