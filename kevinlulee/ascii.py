import kevinlulee as kx

# 2025-05-16 aicmp: add an option to allow separator lines to be shown or not
class TableFormatter:
    def __init__(self, data, keys=None, padding=3, center_header=True, show_pipes=False, left_aligned=True, left_padding_first_col=0, right_padding_last_col=0):
        kx.assert_array(data)
        self.data = data
        self.keys = keys
        self.padding = padding
        self.center_header = center_header
        self.show_pipes = show_pipes
        self.left_aligned = left_aligned
        self.left_padding_first_col = left_padding_first_col
        self.right_padding_last_col = right_padding_last_col
        self.outer_pipe = ''

    def get_keys(self, data):
        if isinstance(data, dict):
            return list(data.keys())
        else:
            result = []
            for key, value in data.__dict__.items():
                if isinstance(value, (str, int, float)):
                    result.append(key)
            return result
    
    def get_field_value(self, row, col):
        if isinstance(row, dict):
            return row.get(col, '')
        else:
            return getattr(row, col, '')

    def get_column_widths(self, columns):
        col_widths = {col: len(col) for col in columns}
        
        for el in self.data:
            for col in columns:
                width = len(str(self.get_field_value(el, col)))
                col_widths[col] = max(col_widths[col], width)
                
        return col_widths
    
    def format_header(self, columns, col_widths):
        pipe = "|" if self.show_pipes else ""
        # pipe = ' '
        
        header_parts = []
        for i, col in enumerate(columns):
            left_pad = self.left_padding_first_col if i == 0 else self.padding
            right_pad = self.right_padding_last_col if i == len(columns) - 1 else self.padding
            
            if self.center_header:
                header_parts.append(f"{' ' * left_pad}{col:^{col_widths[col]}}{' ' * right_pad}")
            else:
                header_parts.append(f"{' ' * left_pad}{col:<{col_widths[col]}}{' ' * right_pad}")
        
        header = self.outer_pipe + (pipe if self.show_pipes else "").join(header_parts) + self.outer_pipe
        return header
    
    def format_rows(self, columns, col_widths):
        pipe = "|" if self.show_pipes else ""
        
        rows = []
        for row in self.data:
            row_parts = []
            for i, col in enumerate(columns):
                left_pad = self.left_padding_first_col if i == 0 else self.padding
                right_pad = self.right_padding_last_col if i == len(columns) - 1 else self.padding
                
                value = str(self.get_field_value(row, col))
                if self.left_aligned:
                    row_parts.append(f"{' ' * left_pad}{value:<{col_widths[col]}}{' ' * right_pad}")
                else:
                    row_parts.append(f"{' ' * left_pad}{value:^{col_widths[col]}}{' ' * right_pad}")
            
            formatted_row = self.outer_pipe + (pipe if self.show_pipes else "").join(row_parts) +self.outer_pipe 
            rows.append(formatted_row)
        return rows

    def format(self):
        if not self.data:
            return ''
            
        columns = self.keys or self.get_keys(self.data[0])
        col_widths = self.get_column_widths(columns)

        # Calculate total widths including padding
        total_widths = {}
        for i, col in enumerate(columns):
            left_pad = self.left_padding_first_col if i == 0 else self.padding
            right_pad = self.right_padding_last_col if i == len(columns) - 1 else self.padding
            total_widths[col] = col_widths[col] + left_pad + right_pad

        pipe = "-" if self.show_pipes else ""
        separator_char = '-'
        separator = self.outer_pipe + pipe.join(separator_char * width for width in total_widths.values()) + self.outer_pipe

        header = self.format_header(columns, col_widths)
        rows = self.format_rows(columns, col_widths)
        table = [separator, header, separator, *rows, separator]

        return "\n".join(table)

# 2025-05-16 aicmp: add in the params from table formatter
def table(data, keys=None, padding=2, center_header=False, **kwargs) -> str:
    """
    data is a list of dictionaries or class objects

    if keys are not provided, keys are gathered from the first element
    class objects will

    a thin wrapper around TableFormatter
    """
    formatter = TableFormatter(data, keys, padding, center_header, **kwargs)
    return formatter.format()

def shorten(s, max_lines=17, padding=(1, 1)):
    padding_above, padding_below = padding

    lines = s.strip().split('\n')
    length = len(lines)
    
    effective_max_lines = max_lines - padding_above - padding_below - 1
    
    if length <= max_lines:
        return s
    else:
        first_chunk_size = effective_max_lines // 2
        last_chunk_size = effective_max_lines - first_chunk_size
        first_lines = lines[:first_chunk_size]
        last_lines = lines[-last_chunk_size:]
        
        a = [''] * padding_above
        b = [''] * padding_below
        c = [f'... {length - effective_max_lines} lines hidden ...']
        out = first_lines + a + c + b + last_lines
        return "\n".join(out)


def side_by_side(
    a,
    b,
    padding=1,
    max_width=80,
    separator="|",
    prefix=None,
    headers=None,
    dotted_starting_spaces=False,
    title=None,
):
    """
    Display two chunks of text side by side, with auto-width adjustment and padding.
    Raises ValueError if the total width exceeds the maximum width.

    :param a: First chunk of text
    :param b: Second chunk of text
    :param padding: Number of spaces for padding (default 1)
    :param max_width: Maximum total width, including separator (default 80)
    :raises ValueError: If the total width exceeds max_width
    """

    # Split the texts into lines and trim whitespace
    def fix(a):
        a = kx.trimdent(kx.serialize_data(a))
        a = [line.rstrip() for line in a.split("\n")]
        return a

    lines1 = fix(a)
    lines2 = fix(b)

    if headers:
        lines1.insert(0, hr(5))
        lines2.insert(0, hr(5))
        lines1.insert(0, headers[0])
        lines2.insert(0, headers[1])
    # Determine the maximum line length for each text
    max_len1 = max((len(line) for line in lines1), default=0)
    max_len2 = max((len(line) for line in lines2), default=0)

    # Calculate total width including padding and separator
    pad_left, pad_right = (padding, padding) if is_number(padding) else padding
    prefix = prefix + " " if prefix else ""
    total_width = max_len1 + max_len2 + 3 + pad_left + pad_right + len(prefix)

    # Early guard clause: check if total width exceeds max_width
    if total_width > max_width:
        s = ""
        if title:
            s += title
            s += "\n"
        if headers:
            s += headers[0] + ":\n"
        s += fence(a)
        s += "\n"
        if headers:
            s += headers[1] + ":\n"
        s += fence(b)
        return s

    # Determine the maximum number of lines
    max_lines = max(len(lines1), len(lines2))

    # Pad the shorter text with empty lines
    lines1 += [""] * (max_lines - len(lines1))
    lines2 += [""] * (max_lines - len(lines2))

    pad_left = " " * pad_left
    pad_right = " " * pad_right
    store = []
    for line1, line2 in zip(lines1, lines2):
        padded_line1 = f"{line1:<{max_len1}}"
        padded_line2 = f"{line2:<{max_len2}}"
        s = f"{padded_line1}{pad_left}{separator}{pad_right}{prefix}{padded_line2}"
        store.append(s)
    if title:
        w = len(store[0])
        store.insert(0, hr(w))
        store.insert(0, centered(title, w))
        store.insert(0, hr(w))
    return "\n".join(store)


# Sample calls
data1 = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "San Francisco"},
    {"name": "Charlie", "age": 22, "city": "Chicago"}
]


if __name__ == '__main__':
    print(table(data1, show_pipes = True))

    # long_text = "\n".join([f"Line {i}" for i in range(1, 101)])
    # shortened = shorten(long_text, max_lines=10)

