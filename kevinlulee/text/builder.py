from __future__ import annotations

from kevinlulee.ao import flat
from kevinlulee.serialize_ops import serialize_data
from kevinlulee.string_utils import parens, trimdent
from kevinlulee.text_tools import join_text
from kevinlulee.validation import exists

from kevinlulee.text.utils.text_ops import (
    format_field_items,
    format_list_items,
    format_numbered_items,
    format_row_items,
)


class StringBuilder:
    def __init__(self, newlines = True):
        self.content = []
        self.newlines = newlines
        self.wrappers = []

    def add(self, type, value):
        if exists(value):
            self.content.append((type, value))

        return self

    def wrap(self, delimiter="---"):
        self.wrappers.append(lambda x: parens(x, delimiter))

    def newline(self):
        self.add('text', '\n')
    def add_text(self, text, bold = False):
        base = trimdent(text) if isinstance(text, str) else serialize_data(text)
        s = f'** {base} **' if bold else base
        return self.add("text", s)

    def add_field(self, key, value):
        if exists(value):
            if isinstance(value, str):
                value = trimdent(value)
            
            self.add("field", (key, value))
        return self

    def add_row(self, *values):
        return self.add("row", flat(values))

    def add_bullet(self, value):
        return self.add("bullet", value)

    def add_section(self, section: StringBuilderSection):
        return self.add("section", section)

    def bullets(self, delimiter="-", ind=2, title=None):
        return BulletSection(self, delimiter=delimiter, ind=ind, title=title)

    def numbered(self, **kwargs):
        return NumberSection(self, **kwargs)

    def pre_process(self):
        """Group adjacent items of the same type (bullet or field)"""
        if not self.content:
            return []

        processed = []
        i = 0

        while i < len(self.content):
            item_type, value = self.content[i]

            if item_type in ["bullet", "field", "row"]:
                # Collect all adjacent items of the same type
                group = [value]
                j = i + 1

                while j < len(self.content) and self.content[j][0] == item_type:
                    group.append(self.content[j][1])
                    j += 1

                processed.append((item_type + "_group", group))
                i = j
            else:
                processed.append((item_type, value))
                i += 1

        return processed

    def get_formatted_contents(self):
        processed = self.pre_process()
        result = []

        for item_type, value in processed:
            if item_type == "text":
                result.append(str(value))
            elif item_type == "bullet_group":
                formatted = self.format_bullet_group(value)
                result.append(formatted)
            elif item_type == "field_group":
                formatted = self.format_field_items(value)
                result.append(formatted)
            elif item_type == "section":
                result.append(value.to_str()) 
                # str(value) does not preserve indentation
                # must use value.to_str()  

            elif item_type == "row_group":
                formatted = self.format_row_group(value)
                result.extend(formatted)

        return result

    def to_str(self):
        result = self.get_formatted_contents()
        value = self.join(result)
        for wrapper in self.wrappers:
            value = wrapper(value)
        return value

    def format_field_items(self, value):
        return format_field_items(value)

    def format_bullet_group(self, value):
        return format_list_items(value)

    def format_row_group(self, value):
        return format_row_items(value)

    def join(self, items):
        return join_text(items) if self.newlines else "\n".join(items)

    __str__ = to_str


class NumberSection(StringBuilder):
    def __init__(
        self,
        parent: StringBuilder,
        title = None,
        template="1. ",
        ind=2,
    ):
        super().__init__()
        self.parent = parent
        self.template = template
        self.ind = ind
        self.title = title if title else ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.parent.add_section(self)

    def to_str(self):
        result = [self.title]

        elements = self.format_number_group(self.get_formatted_contents())
        result.append(elements)

        return "\n".join(result)

    def format_number_group(self, bullets):
        # Use BulletSection's delimiter and indentation
        return format_numbered_items(
            bullets
        )
class BulletSection(StringBuilder):
    def __init__(
        self,
        parent: StringBuilder,
        delimiter="-",
        ind=2,
        title=None,
        title_delimiter=":",
    ):
        super().__init__()
        self.parent = parent
        self.delimiter = delimiter
        self.ind = ind
        self.title = title
        self.title_delimiter = title_delimiter

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.parent.add_section(self)

    def to_str(self):
        result = []

        if self.title:
            result.append(str(self.title) + self.title_delimiter)

        elements = self.format_bullet_group(self.get_formatted_contents())
        result.append(elements)

        return "\n".join(result)

    def format_bullet_group(self, bullets):
        # Use BulletSection's delimiter and indentation
        return format_list_items(
            bullets, delimiter=self.delimiter, ind=self.ind
        )


def example():
    """
    a really cool example of nested sections
    """
    sb = StringBuilder()

    # Add plain text
    sb.add_text(
        """
        This is a simple description.
        It supports multiline strings.
    """
    )

    # Add key-value fields
    sb.add_field("Author", "Kevin Lu")
    sb.add_field("Version", "1.0")

    # Add a row
    sb.add_row("IDasdasd", "Name", "Status")
    sb.add_row("ID", "Nalphasdasdme", "Statusasdasd")

    # Add bullets
    # sb.add_bullet("First item")
    # sb.add_bullet("Second item")

    # Add a nested bullet section
    with sb.bullets(title="Features", delimiter="*") as b:
        b.add_text("Easy to use")
        b.add_text("Flexible API")
        b.add_text("Supports nesting")

        section = StringBuilder()
        section.add_text("This is a nested section.")
        section.add_field("NestedKey", "NestedValue")
        section.add_field("NestedKeys", "NestedValue")
        section.add_field("NestedasdasKey", "NestedValue")
        section.wrap()
        b.add_section(section)

    # Add another section
    section = StringBuilder()
    section.add_text("This is a nested section.")
    section.add_field("NestedKey", "NestedValue")
    section.add_field("NestedKeys", "NestedValue")
    section.add_field("NestedasdasKey", "NestedValue")
    section.wrap()
    sb.add_section(section)

    # Output the final formatted string
    return sb


if __name__ == "__main__":
    print(example())


