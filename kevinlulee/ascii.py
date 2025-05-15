class TableFormatter:
    def __init__(self, data, keys=None, padding=1, center_header=True):
        self.data = data
        self.keys = keys
        self.padding = padding
        self.center_header = center_header

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

    def format(self):
        if not self.data:
            return ''
            
        data = self.data
        columns = self.keys or self.get_keys(data[0] if isinstance(data, list) else data)
        col_widths = {col: len(col) for col in columns}
        
        for el in data:
            for col in columns:
                width = len(str(self.get_field_value(el, col)))
                col_widths[col] = max(col_widths[col], width)

        # Add padding to column widths
        total_widths = {col: width + (self.padding * 2) for col, width in col_widths.items()}

        d = '-'
        separator = d + d.join("-" * width for width in total_widths.values()) + d

        # Create the header

        if self.center_header:
            header = (
                "|"
                + "|".join(
                    f"{' ' * self.padding}{col:^{col_widths[col]}}{' ' * self.padding}"
                    for col in columns
                )
                + "|"
            )
        else:
            header = (
                "|"
                + "|".join(
                    f"{' ' * self.padding}{col:<{col_widths[col]}}{' ' * self.padding}"
                    for col in columns
                )
                + "|"
            )

        # Create the rows
        rows = []
        for row in data:
            formatted_row = (
                "|"
                + "|".join(
                    f"{' ' * self.padding}{str(self.get_field_value(row, col)):<{col_widths[col]}}{' ' * self.padding}"
                    for col in columns
                )
                + "|"
            )
            rows.append(formatted_row)

        # Combine all parts
        table = [separator, header, separator, *rows, separator]

        return "\n".join(table)

def table(data, keys=None, padding=3, center_header=False):
    formatter = TableFormatter(data, keys, padding, center_header)
    return formatter.format()

# Sample calls
data1 = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "San Francisco"},
    {"name": "Charlie", "age": 22, "city": "Chicago"}
]

if __name__ == '__main__':
    print(table(data1))
