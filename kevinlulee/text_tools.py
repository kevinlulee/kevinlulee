import re
import yaml
import textwrap
from .ao import to_array
from .templater import templater


def bracket_wrap(
    items,
    bracket_type: str = "()",
    indent: int = 4,
    delimiter=", ",
    newlines=False,
) -> str:
    brackets = {
        "()": ("(", ")"),
        "[]": ("[", "]"),
        "[[]]": ("[[", "]]"),
        "{}": ("{", "}"),
        '"': ('"', '"'),
        "'": ("'", "'"),
        ":": (":", ""),
        "'''": ("'''", "'''"),
        '"""': ('"""', '"""'),
        "``": ("`", "`"),
        "```": ("```", "```"),
        "({})": ("({", "})"),
        "([])": ("([", "])"),
    }

    if newlines and delimiter == ", ":
        delimiter = ",\n"
    open_bracket, close_bracket = brackets[bracket_type]
    text = delimiter.join(str(el) for el in to_array(items))
    if not text:
        return open_bracket + close_bracket
    if re.search("^[\(\{\[]\n", text):
        return open_bracket + text + close_bracket
    # print([indented_text, ending_newline])
    if newlines:
        indented_text = textwrap.indent(text, " " * indent)
        ending_newline = "" if indented_text.endswith("\n") else "\n"
        return f"{open_bracket}\n{indented_text}{ending_newline}{close_bracket}"
    else:
        return open_bracket + text + close_bracket

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
    frontmatter_pattern = re.compile(r"^\s*\w+:|^\s+-")

    lines = text.split("\n")
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

    frontmatter_text = "\n".join(frontmatter_lines)
    frontmatter = yaml.safe_load(frontmatter_text) if frontmatter_text else {}

    content = "\n".join(lines[content_start:])
    return content, frontmatter


def tabs_to_spaces(s):
    return s.replace("\t", "    ")


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
        "python": "#",
        "javascript": "//",
        "java": "//",
        "c": "//",
        "cpp": "//",
        "csharp": "//",
        "typescript": "//",
        "html": "<!--",
        "css": "/*",
        "sql": "--",
        "ruby": "#",
        "php": "//",
        "rust": "//",
        "swift": "//",
        "go": "//",
        "perl": "#",
        "r": "#",
        "matlab": "%",
        "shell": "#",
        "bash": "#",
        "powershell": "#",
        "yaml": "#",
        "toml": "#",
        "ini": ";",
        "lua": "--",
        "haskell": "--",
    }

    # Get the comment symbol for the given filetype, default to '#' if unknown
    symbol = comment_symbols.get(filetype.lower(), "#")

    # Strip whitespace from the beginning while preserving it for later
    stripped_text = text.lstrip()
    leading_space = text[: len(text) - len(stripped_text)]

    # Handle HTML-style comments
    if symbol == "<!--":
        if stripped_text.startswith("<!--") and stripped_text.endswith("-->"):
            # Remove HTML comment
            return leading_space + stripped_text[4:-3].strip()
        # Add HTML comment
        return leading_space + "<!-- " + stripped_text + " -->"

    # Handle CSS-style block comments
    if symbol == "/*":
        if stripped_text.startswith("/*") and stripped_text.endswith("*/"):
            # Remove CSS comment
            return leading_space + stripped_text[2:-2].strip()
        # Add CSS comment
        return leading_space + "/* " + stripped_text + " */"

    # Handle single-line comments
    if stripped_text.startswith(symbol):
        # Remove comment
        return leading_space + stripped_text[len(symbol) :].lstrip()
    # Add comment
    return leading_space + symbol + " " + stripped_text


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

    return "\n".join(result)


def join_text(*contents):
    def runner(contents):
        o = ""
        for content in contents:
            if isinstance(content, (list, tuple)):
                s = runner(content)
            else:
                s = content

            if not s:
                continue

            if "\n" in s:
                if o.endswith("\n\n"):
                    o += f"{s}\n\n"
                else:
                    o += f"\n{s}\n\n"
            else:
                o += f"{s}\n"
        return o

    contents = contents[0] if len(contents) == 1 else contents
    return runner(contents)


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
    split_chunks = re.split(
        rf"^\-{{{delim_length},}}$", text, flags=re.MULTILINE
    )

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


def strcall(name, args, kwargs, max_length=80):
    a = len(args)
    k = len(kwargs)

    s = name + bracket_wrap(args + kwargs, bracket_type="()", newlines=False)
    if a + k == 1:
        return s
    if len(s) < max_length and not "\n" in s:
        return s

    s = name + bracket_wrap(args + kwargs, bracket_type="()", newlines=True)
    return s



