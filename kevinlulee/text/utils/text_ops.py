import kevinlulee as kx

def format_row_items(rows, separator=" ", alignment="<"):
    """
    Format a list of tuples into aligned columns and return as a string.
    
    Args:
        rows: List of tuples containing row data
        separator: String to separate columns (default: " ")
        alignment: Alignment for columns ("<" left, ">" right, "^" center)
    
    Returns:
        Formatted string with aligned columns
    """
    if not rows:
        return ""
    
    # Calculate maximum width for each column
    col_widths = []
    max_cols = max(len(row) for row in rows)
    
    for col_idx in range(max_cols):
        max_width = 0
        for row in rows:
            if col_idx < len(row):
                max_width = max(max_width, len(str(row[col_idx])))
        col_widths.append(max_width)
    
    # Format each row
    formatted_rows = []
    for row in rows:
        formatted_cols = []
        for col_idx, item in enumerate(row):
            if col_idx < len(col_widths):
                width = col_widths[col_idx]
                formatted_cols.append(f"{str(item):{alignment}{width}}")
            else:
                formatted_cols.append(str(item))
        formatted_rows.append(separator.join(formatted_cols))
    
    return formatted_rows


# Example usage:
if __name__ == "__main__":
    # Sample data
    data = [
        ("Name", "Age", "City", "Salary"),
        ("Alice", 25, "New York", 75000),
        ("Bob", 30, "Los Angeles", 82000),
        ("Charlie", 22, "Chicago", 68000),
        ("Diana", 28, "Miami", 71500)
    ]
    
    

def format_field_items(entries: list[tuple[str, str]], aligned_colons = True):
    """
    Format a list of (key, value) tuples with aligned keys and proper indentation.
    
    Args:
        entries: List of tuples like [('foobar', 'hi\nbye'), ('abc', 'hiiiiiii')]
    
    Returns:
        Formatted string with aligned keys and indented multi-line values
    """
    if not entries:
        return ""
    
    # Find the maximum key length for alignment
    max_key_length = max(len(key) for key, _ in entries)
    
    store = []
    for key, value in entries:
        result = []
        # Split value into lines
        lines = kx.serialize_data(value).split('\n')
        
        # First line: key + colon + first line of value
        if aligned_colons:
            offset = 1
            spaces = ' ' * (max_key_length - len(key) + offset)
            delimiter = f'{spaces}: '
        else:
            spaces = ' ' * (max_key_length - len(key) + 1)
            offset = 0
            delimiter = f':{spaces}'

        body_indent = ' ' * (max_key_length + 2 + offset)  # +2 for colon and space
        for i, line in enumerate(lines):
            if i == 0:
                result.append(f'{key}{delimiter}{line}')
            else:
                result.append(f"{body_indent}{line}")
        
        s = '\n'.join(result)
        store.append(s)

    return kx.join_text(store)


def format_list_items(items, ind = 2, delimiter = '-'):
    
    store = []
    gap = ' '
    body_indent = ' ' * (len(delimiter) + len(gap))
    for item in items:
        lines = item.split('\n')
        result = []
        for i, line in enumerate(lines):
            if i == 0:
                result.append(f'{delimiter}{gap}{line}')
            else:
                result.append(f"{body_indent}{line}")

        s = '\n'.join(result)
        store.append(s)

    return kx.indent(kx.join_text(store), ind)


def format_numbered_items(items, ind = 2, start = 1):
    
    store = []
    gap = ' '
    for i, item in enumerate(items):
        n = i + start
        delimiter = str(n) + '.'
        body_indent = ' ' * (len(delimiter) + len(gap))
        lines = item.split('\n')
        result = []
        for i, line in enumerate(lines):
            if i == 0:
                result.append(f'{delimiter}{gap}{line}')
            else:
                result.append(f"{body_indent}{line}")

        s = '\n'.join(result)
        store.append(s)

    return kx.indent(kx.join_text(store), ind)
# Example usage
if __name__ == "__main__":
    # Test data
    entries = [
        ("foobar", "hi\nbye"),
        ("abc", "hiiiiiii"),
        ("longer_key", "single line"),
        ("x", "multi\nline\nvalue\nhere")
    ]
    
    print(format_field_items(entries))
    print("\n" + "="*40 + "\n")
    
    # Your specific example
    specific_entries = [
    'hiias\ndd',
    'hii\nbye',
    'sdf',
    'sdf',
    ]
    
    print(format_list_items(specific_entries))
    print(format_numbered_items(list('abcde')))


