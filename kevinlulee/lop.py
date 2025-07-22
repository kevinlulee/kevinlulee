from traversal.lop import LineNode, create_root
from kevinlulee.string_utils import trimdent
from kevinlulee.traverse import Element, Visitor, accumulate_text
from codefmt.yaml import yamlfmt
import re

from kevinlulee import kx

MULTILINE_FIELDS = ["desc", "notes"]

from dataclasses import dataclass
from typing import List, TypedDict


class FileTreeAttrs(TypedDict):
    desc: str
    hotkey: str
    skip: str


@dataclass
class FileTreeNode:
    path: str
    type: str
    attrs: FileTreeAttrs
    children: List["FileTreeNode"]

    def isdir(self):
        return self.type == "dir"

    def isfile(self):
        return self.type == "file"

    @property
    def name(self):
        return os.path.basename(self.path)


class FileTreeVisitor(Visitor):
    def __init__(self, root_directory="~/projects"):
        super().__init__()
        self.cwd = []
        self.root_directory = kx.os.path.expanduser(root_directory)

    def get_attribute_key(self, node):
        s = node.text.strip()
        m = kx.matchstr(s, "^([\w-]+):$")
        return m

    def get_attribute(self, node):
        s = node.text.strip()
        m = kx.matchstr(s, "^([\w-]+): +(.+)")
        return m or (None, None)

    def visit_root(self, node: LineNode):
        if node.size == 1:
            return self.visit(node.first_child)
        else:
            children = self.visit(node.children)
            return FileTreeNode(
                path="", type="dir", attrs={}, children=children
            )

    def visit_branch(self, node):
        text = node.text.strip()
        name = text

        is_file = kx.has_extension(name)
        # this is supremely important.
        # it is how you know if something is a file

        if node.ind == 0:
            name = os.path.join(self.root_directory, name)

        m = self.get_attribute_key(node)

        children = node.children
        props = {}
        other_children = []

        if m:
            if m in MULTILINE_FIELDS:
                desc = str(accumulate_text(children))
                props.update({m: desc})
            else:
                p = self.visit_each(children)
                props.update({m: kx.merge_dicts(*p)})
            return props

        elif is_file:
            self.cwd.append(name)

            for i, child in enumerate(children):
                val = self.visit(child)
                if isinstance(val, dict) and "path" not in val:
                    props.update(val)
                else:
                    remaining = children[i:]
                    props.update({"desc": str(accumulate_text(remaining))})
                    break
        else:
            # a directory
            self.cwd.append(name)
            for child in children:
                val = self.visit(child)
                if isinstance(val, dict) and "path" not in val:
                    props.update(val)
                else:
                    other_children.append(child)

        entry_type = "file" if is_file else "dir"
        entry = self.make_entry(
            name,
            entry_type,
            props,
            kx.filtered(self.visit_each(other_children)),
        )

        self.cwd.pop()
        return entry

    def visit_attr(self, node):
        s = node.text.strip()
        m = kx.matchstr(s, "^([\w-]+): +(.+)")
        if m:
            return {m[0]: m[1]}

    def visit_leaf(self, node):
        m = self.visit_attr(node)
        if m:
            return m

        name = node.text.strip()
        is_file = kx.has_extension(name)
        type = "file" if is_file else "dir"
        return self.make_entry(name, type)

    def make_entry(self, name, type, attributes={}, children=[]):
        extra = (
            [name] if type == "file" and not self.cwd[0].endswith(name) else []
        )
        attrs = kx.walk(attributes, kx.coerce_argument)
        path = "/".join(self.cwd + extra)
        return FileTreeNode(
            path=path, type=type, attrs=attrs, children=children
        )

    def visit(self, node):
        if isinstance(node, (tuple, list)):
            return self.visit_each(node)
        elif node.uid == 0:
            return self.visit_root(node)
        elif node.children:
            return self.visit_branch(node)
        else:
            return self.visit_leaf(node)


class CreateProject:
    base_directory = "~/projects/"

    def __init__(
        self,
        text,
        debug=False,
    ):
        self.debug = debug
        self.project_languages = set()  # collecting languages
        self.descriptions = {}  # accumulating descriptions
        self.hotkeys = dict(dir={}, file={})
        self.files_created = []  # Track files for fancy_filetree
        self.known_languages = ["python", "typst", "typescript"]
        processed_text = kx.remove_commented_lines(kx.trimdent(text))
        text, frontmatter = kx.extract_frontmatter(processed_text)
        frontmatter["date"] = kx.strftime()
        root_directory = os.path.join(
            self.base_directory, frontmatter.get("root") or ""
        )
        self.file_tree = FileTreeVisitor(root_directory=root_directory).visit(
            create_root(text)
        )

        self.frontmatter = frontmatter
        self.root_directory = root_directory

    def process_file(self, node: FileTreeNode):
        self.create_file(node.path)
        self.create_file_blueprint(node)

    def create_file_blueprint(self, node):
        desc = node.attrs.get("desc")

    def process_node(self, node: FileTreeNode):
        if node.attrs.get("skip"):
            return

        self.init_description(node)
        self.init_path_hotkey(node)

        if node.isdir():
            for child in node.children:
                self.process_node(child)

            if node.name in self.known_languages:
                self.project_languages.add(node.name)

            self.init_python_directory(node)
        elif node.isfile():
            self.process_file(node)

    def init_description(self, node):
        desc = node.attrs.get("desc")
        if desc:
            self.descriptions[node.path] = desc

    def init_path_hotkey(self, node):
        hotkey = node.attrs.get("hotkey")
        if hotkey:
            self.hotkeys[node.type][hotkey] = node.path

    def init_python_directory(self, node: FileTreeNode):
        validate = lambda x: kx.is_python_file(x.path)
        if all(validate(child) for child in node.children if child.isfile()):
            p = os.path.join(node.path, "__init__.py")
            self.create_file(p)

    def create_file(self, path, value=None):
        path = os.path.expanduser(path)
        if value:
            kx.writefile(path, value, debug=self.debug)
        else:
            kx.mkfile(path, debug=self.debug)
        self.files_created.append(path)

    def process_hotkeys(self):
        if self.hotkeys:
            self.create_file(self.get_path("bookmarks.json"), self.hotkeys)

    def create_readme(self):
        sb = kx.StringBuilder()
        opts = dict(quote_strings = False)
        sb.add_text(kx.parens(yamlfmt.format(self.frontmatter, opts = opts), '---'))
        sb.add_text(kx.fancy_file_tree(self.files_created))

        for k, v in self.descriptions.items():
            sb.add_text(k, bold=True)
            sb.add_text(v)

        print(sb)
        self.create_file(self.get_path("README.md"), str(sb))

    def get_path(self, file):
        return os.path.join(self.root_directory, file)

    def run(self):
        self.process_node(self.file_tree)
        self.process_hotkeys()
        self.create_readme()


if __name__ == "__main__":
    HAM_ROOT = "/home/kdog3682/projects/hammymathclass/python"
    ROOT = "/home/kdog3682/projects/hammymathclass/python/"
    TEMPLATE = """
        ---
        root: yoya
        desc: |
            attributes
            asdfasdfasdf
            ss
        ---

        python
            abc.py
                hotkey: abc
            foobar
                desc:
                    asdfasdfasdf
                notes:
                    hotkeys
                    hotkeys
                    hotkeys
                    hotkeys
                goobar.py
    """
    creator = CreateProject(TEMPLATE, debug=True)
    creator.run()
