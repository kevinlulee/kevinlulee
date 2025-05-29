from __future__ import annotations
import kevinlulee as kx
import yaml

NEWLINE = "NEWLINE"


class StringBuilder:
    def __init__(self, label_template="[%s]"):
        self.content = []
        self.label_template = label_template

    def add(self, text, label=None, wrap_with_dashes=False, dash_delimiter = '-'):
        if not text:
            return self

        text = kx.trimdent(text)
        if wrap_with_dashes:
            text = kx.bar(60, dash_delimiter) + "\n" + text + "\n" + kx.bar(60, dash_delimiter)

        if label:
            label = self.label_template % label
            text = f"{label}\n{text}"

        self.content.append(text)
        return self

    def newline(self, soft=False):
        if soft:
            if self.content:
                if self.content[-1] == NEWLINE:
                    return
                elif self.content[-1].endswith("\n"):
                    return
            else:
                self.content.append("\n")
        else:
            self.content.append("\n")
        return self

    def to_str(self):
        def runner(contents):
            o = ""
            for content in contents:
                if content == NEWLINE:
                    o += "\n"
                    continue

                elif isinstance(content, (list, tuple)):
                    s = runner(content)

                else:
                    s = str(content)

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

        return runner(self.content).strip()

    def __str__(self):
        return self.to_str()

    def section(self, name):
        return SectionContext(self, name)

class MarkdownBuilder(StringBuilder):
    def __init__(self):
        super().__init__()
        self.frontmatter = {}

    def add_frontmatter(self, **kwargs):
        self.frontmatter.update(kwargs)

    def to_str(self):
        if self.frontmatter:
            yaml_str = yaml.dump(
                self.frontmatter,
                default_flow_style=False,  # use block style (not inline)
                sort_keys=False,  # preserve dict order
                indent=2,  # control indentation
                width=60,  # max line width before wrapping
            ).strip()
            s = kx.bar(3) + "\n" + yaml_str + "\n" + kx.bar(3)
            self.content.insert(0, s)

        return super().to_str()


class SectionContext(StringBuilder):
    def __init__(
        self,
        builder: StringBuilder,
        name=None,
        label_template=None,
        wrap_with_dashes=False,
    ):
        super().__init__(
            label_template=label_template or builder.label_template
        )
        self.builder = builder
        self.name = name
        self.wrap_with_dashes = wrap_with_dashes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.content:
            s = kx.indent(self.to_str(), 2)
            self.builder.add(
                s, label=self.name, wrap_with_dashes=self.wrap_with_dashes
            )


# m = MarkdownBuilder()
# m.add('hi')
# m.add_frontmatter(asd = 1)
# with m.section('foo') as sub:
#     sub.add('hi')
#     with sub.section('boo') as subsub:
#         subsub.add('hi')
# print(m)
