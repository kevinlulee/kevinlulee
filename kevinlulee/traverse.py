from __future__ import annotations
import re
from kevinlulee.ao import dict_getter, dict_setter, mapfilter
from kevinlulee.string_utils import matchstr, trimdent
from kevinlulee.validation import has_comment, is_array, test

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TextToken:
    text: str
    ind: Optional[int] = 0
    newlines: Optional[int] = 0
    type: str = "text"
    
    def __str__(self) -> str:
        return self.text



def postorder_traverse(node, callback):
    def runner(node):
        for child in node.children:
            runner(child)
        callback(node)

    runner(node)
    return node


def preorder_traverse(node, callback):
    def runner(node):
        callback(node)
        for child in node.children:
            runner(child)

    runner(node)
    return node


def traverse(node, callback, mode="post"):
    ref = {
        "post": postorder_traverse,
        "pre": preorder_traverse,
    }
    func = ref.get(mode)
    return func(node, callback)


class Element:
    def traverse(callback, key="pre"):
        return traverse(self, callback)

    def findall_descendants(self, callback):
        def runner(node):
            for child in node.children:
                if callback(child):
                    store.append(child)
                runner(child)

        store = []
        runner(self)
        return store

    def find_descendant(self, callback):
        def runner(node):
            for child in node.children:
                if callback(child):
                    return True
                else:
                    result = runner(child)
                    if result:
                        return True

        return runner(self)

    def findall_ancestors(self, callback):
        store = []
        parent = self.parent
        while not parent.is_root():
            if callback(parent):
                store.append(parent)
            parent = parent.parent
        return store

    def find_ancestor(self, callback):
        if self.parent.is_root():
            return
        if callback(self.parent):
            return self.parent
        else:
            return self.parent.find_ancestor(callback)

    @property
    def size(self):
        return len(self.children)

    def __init__(self, state=None, parent=None):
        self.type = ""
        self.children = []
        self.state = state or {}
        self.set_parent(parent)

    def set_parent(self, parent):
        if parent is None:
            self.uid = 0
            self.parent = None
        else:
            self.parent = parent
            self.uid = parent.uid + parent.size + 1
        return self

    @property
    def self_index(self):
        return self.parent.children.index(self)

    @property
    def root(self):
        return self.parent.root if self.parent else self

    @property
    def prev_sibling(self):
        if not self.parent or self.parent.size == 1:
            return None
        index = self.self_index
        return None if index == 0 else self.parent.children[index - 1]

    @property
    def next_sibling(self):
        if not self.parent:
            return None
        index = self.self_index
        return (
            self.parent.children[index + 1]
            if index + 1 < self.parent.size
            else None
        )

    @property
    def next_siblings(self):
        if not self.parent or self.parent.size == 1:
            return []
        index = self.self_index + 1
        return [self.parent.children[i] for i in range(index, self.parent.size)]

    @property
    def siblings(self):
        if not self.parent:
            return []
        return [x for x in self.parent.children if x != self]

    @property
    def num_siblings(self):
        return len(self.siblings)

    @property
    def first_child(self):
        return self.children[0] if self.children else None

    @property
    def last_child(self):
        return self.children[-1] if self.children else None

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.uid == 0

    def is_branch(self):
        return len(self.children) > 0

    def is_first_child(self):
        return self.parent.first_child == self

    def is_last_child(self):
        return self.parent.last_child == self

    def prev(self):
        return self.prev_sibling or self.parent

    def next(self):
        return self.first_child or self.next_sibling

    def append_child(self, child):
        new_child = self.create(child)
        self.children.append(new_child)
        return new_child

    def prepend_child(self, child):
        new_child = self.create(child)
        self.children.insert(0, new_child)
        return new_child

    def insert_node_before(self, ref_node, node):
        new_node = self.create(node)
        index = ref_node.self_index
        self.children.insert(index, new_node)
        return new_node

    def insert_node_after(self, ref_node, node):
        new_node = self.create(node)
        index = ref_node.self_index + 1
        self.children.insert(index, new_node)
        return new_node

    def replace_node(self, ref_node, node):
        new_node = self.create(node)
        self.children[ref_node.self_index] = new_node
        return new_node

    def replace_with(self, node):
        self.parent.children[self.self_index] = node
        node.set_parent(self.parent)

    def create(self, x):
        return self.__class__(x, self)


class Visitor:
    def run(self, ast):
        if hasattr(self, "visit_root"):
            return self.visit_root(ast)
        if ast.size == 1:
            return self.visit(ast.first_child)
        else:
            return self.visit_each(ast)

    def visit_each(self, node) -> list:
        if is_array(node):
            return [self.visit(el) for el in node]

        return [self.visit(el) for el in node.children]

    def visit(self, node):
        if node is None:
            return
        if node.is_leaf():
            return self.visit_leaf(node)
        return self.visit_branch(node)

    def visit_branch(self, node):
        panic("AbstractMethod visit_branch not implemented")

    def visit_leaf(self, node):
        panic("AbstractMethod visit_leaf not implemented")

    def create(self, text):
        return self.visit(create_root(text))


def accumulate_text(input: List[LineNode | TextToken] | LineNode):
    if isinstance(input, (list, tuple)):
        if type(input[0]) == TextToken:
            text_nodes = input
        else:
            text_nodes = [accumulate_text(el) for el in input]
        ind = text_nodes[0].ind
        newlines = text_nodes[-1].newlines
        mapper = lambda x: x.text + "\n" * (x.newlines + 1)
        text = "".join([mapper(node) for node in text_nodes]).rstrip()
        return TextToken(text=text, ind=ind, newlines=newlines)

    node = input
    offset = node.ind

    def do_node(node, offset: int):
        ind = node.ind - offset
        return " " * (ind * 4) + node.text + "\n" * (node.newlines + 1)

    def callback(child):
        # on each iteration of the callback
        # we report the current newlines
        # the very last child, will report the very last newlines
        # and that will be the newlines for this entire text chunk

        nonlocal newlines
        newlines = child.newlines

        if type(child) == LineNode and child.is_branch():
            return do_node(child, offset) + do_children(child)
        else:
            return do_node(child, offset)

    def do_children(node):
        return "".join([callback(child) for child in node.children])

    newlines = None  # will be updated in the callback
    ind = node.ind
    text = callback(node).rstrip()

    return TextToken(text=text, ind=ind, newlines=newlines)

def get_line_tokens(s):
    def callback(x):
        a, b, c = matchstr(x, "( *)(.*?)(\s*)$")
        text = b
        ind = len(a)
        assert ind % 4 == 0
        ind = ind // 4

        if has_comment(text):
            return

        newlines = max(len(c.replace(" ", "")) - 1, 0)
        return {
            "newlines": newlines,
            "text": text,
            "ind": ind,
        }

    base = re.split("(?=^ *\S)", trimdent(s), flags=re.M)[1:]
    items = mapfilter(base, callback)

    def fix(items):
        ind = items[0].get("ind")
        for item in items:
            item["ind"] = item["ind"] - ind
        return items

    return fix(items)


class LineNode(Element):
    def update(self):
        def check(child):
            return not hasattr(child, "awaiting_deletion")

        def callback(node):
            node.children = filter(node.children, check)

        return self.traverse(callback)

    def remove_child_silently(self):
        self.awaiting_deletion = True

    def enter(self):
        return self.last_child

    def exit(self, n=1):
        context = self
        for _ in range(n):
            context = context.parent
        return context

    def __init__(self, state, parent):
        super().__init__(None, parent)
        self.keys = set()
        self.assign(state)

    def test(self, regex):
        if callable(regex):
            return regex(self.text)
        return test(self.text, regex)

    def __str__(self):
        return self.text

    def get(self, *args):
        return dict_getter(self, *args)

    def assign(self, *args, **kwargs):
        if kwargs:
            for k, v in kwargs.items():
                self.set(k, v)
            return self

        arg = args[0]
        if arg == None:
            pass

        elif isinstance(arg, dict):
            for k, v in arg.items():
                self.set(k, v)
        else:
            self.keys.add(arg)
            dict_setter(self, *args)

        return self

    def get(self, k):
        if k in self.keys:
            return getattr(self, k)

    def set(self, k, v):
        setattr(self, k, v)
        self.keys.add(k)
        return self

    def data(self, *keys):
        return {
            key: getattr(self, key) for key in keys
        }

    def json(self, *fields, typed=False):
        def callback(node):
            if typed:
                if node.is_root():
                    pass
                    # the root is often a shallow container
                    # and will not have its own type.
                if not node.type:
                    return

            data = node.data(*fields)

            if node.children:
                data["children"] = mapfilter(node.children, callback)
            return data

        return callback(self)


def create_root(s):
    if not isinstance(s, str):
        return s

    tokens = get_line_tokens(s)

    current_ind = 0
    node = LineNode(None, None)
    root = node

    for token in tokens:
        ind = token.get("ind")

        if ind > current_ind:
            node = node.enter()
        elif ind < current_ind:
            n = current_ind - ind
            node = node.exit(n)

        node.append_child(token)
        current_ind = ind

    return root


def rehydrate_text(node, offset=0):
    ind = node.ind - offset
    return ind * 4 * " " + node.text + "\n" * node.newlines
