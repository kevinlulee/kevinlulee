from pprint import pprint
from kevinlulee import group, deep_map, clip, fdfind, typstfmt, pythonfmt, real
import sys
import os
from treebloom import TreeBloomNode, TreeBloom, is_node
from kevinlulee import *


q = """
    (tagged field: (ident) @key (number) @value)
"""

q = """
    (tagged field: (ident) @key (_) @value)
"""

s = """
#let a = (abc: ahhi, def: (ghi: 1pt, jkl: 5pt, alpha: 1pt))
# let a = (abc: ahhi, def: (ghi: 111pt))
"""

s = """
    
#import "@local/typkit:0.3.0": div, patterns, nd, join
#let score-box(
  questions,
  wh: 50pt,
  size: 2.2em,
  offset: 7.5pt,
  place: none,
) = {

  if type(questions) == array {
    questions = questions.len()
  }
  let points = div(
    "points",
    align: center,
    bold: true,
    size: 0.65em,
    place: top + center,
    align: center,
    align: center,
    bold: true,
    size: 0.65em,
    place: top + center,
    bold: true,
    size: 0.65em,
    place: top + center,
  )
  let num = nd(none, questions, place: center + horizon, dy: 2.5pt, bold: true, size: 1.5em)

  div(
    abc, dee,
    join(points, num),
    radius: 2pt,
    inset: 5pt,
    stroke: black,
    bg: patterns.small-dots,
    wh: wh,
    place: place,
  )
}
"""


def collect_calls_with_tagged(self):
    call_query_str = r"""
    (
      call
        item: (ident) @iden
        (group) @group
    )
    """
    tagged_query_str = r"""
    (
      tagged
        field: (ident) @key
        (_) @val

      
    )
    """
    results = []
    pos_mapping = {}
    captures = self.query(self.root_node, call_query_str)
    for el in captures:
        iden = el.get("iden")
        group_node = el.get("group")
        child_captures = self.query(group_node, tagged_query_str)
        if not child_captures:
            continue
        child_captures = [x.get("key") for x in child_captures]
        num_pos = group_node.named_child_count - len(child_captures)
        if iden in pos_mapping:
            if pos_mapping[iden] < num_pos:
                pos_mapping[iden] = num_pos
        else:
            pos_mapping[stringify(iden)] = num_pos
        results.append(stringify((iden, child_captures)))

    return results, pos_mapping


def func(name, pos, named):
    print(pos)
    aliases = {None: [], 1: ["arg"]}
    seen = list(set(named))
    args = aliases.get(pos, ["*args"])
    print(pos)
    print(args)
    kwargs = {k: None for k in named}

    body_dict = {p: real(p) for p in named}
    quoted = lambda x: real(f'"{x}"')
    body = pythonfmt.real_decl(
        "return",
        pythonfmt.real_call("abstract", quoted(name), *args, **body_dict),
    )
    return pythonfmt.func_decl(name, *args, body=body, **kwargs)


def boom():
    print(func("abc", ["hi"]))
    clip(ts.collect_calls_with_tagged())

    ts = TreeBloom(s, "typst")
    print(collect_calls_with_tagged(ts))

    files = fdfind(dirs=["~/projects/typst/typkit/0.3.0"], exts=["typ"])

    store = []
    for file in files:
        bloom = TreeBloom(file)
        store += collect_calls_with_tagged(bloom)
    #
    #
    results = group(store, flatten_array_values=True)
    # clip(results)
    clip(results)




# stringify = lambda x: deep_map(x, lambda x: decode(x) if is_node(x) else None)


def typst_codelib(file, short = False):
    query = """
    (
  source_file
  (code
    (let 
      pattern: (call 
        item: (ident) @name
        (group) @arglist
      )
    ) @block
  )
)
    """
    file = os.path.expanduser(file)
    bloom = TreeBloom(file, "typst")
    results = bloom.query(bloom.root, query)

    def parse(result):
        name = result["name"].text
        block = result["block"].text
        arglist: TreeBloomNode = result["arglist"]

        store = []
        pos = []
        elude = None
        named = {}
        for child in arglist.children:
            match child.type:
                case "ident":
                    pos.append(child.text)
                case "tagged":
                    a, b = child.children
                    named[a.text] = dict(type = b.type, value = b.text)
                case "elude":
                    elude = child.first_child.text

        if short:
            return dict(
                name=name,
                params=dict(elude=elude, named=named, pos=pos),
            )
        return dict(
            name=name,
            params=dict(elude=elude, named=named, pos=pos),
            text=block,
        )

    if short:
        return each(results, parse)
    return dict(file = file, contents = each(results, parse), meta = dict(date = strftime(file)))


if __name__ == "__main__":
    s = """
        #let foobar(howdy, a: 123, b: 234, ..cark, ..sink) = box({
    
        })
    """
    # files = fdfind(dirs=["~/projects/typst/typkit/0.3.0"], exts=["typ"])
    files = [
        "~/projects/typst/typkit/0.3.0/src/components.typ",
        "~/projects/typst/typkit/0.3.0/src/div.typ",
        "~/projects/typst/typkit/0.3.0/src/layout.typ",
        # *fd("~/projects/typst/workbook-ui/0.1.0/src/", exts = ['typ']),
    ]
    # results = flat(each(files, typst_codelib, short = True))
    # out = '~/data/codelib/typst.json'
    # writefile(out, results)

def json_to_typst_func(data):
    name = data['name']
    params = data['params']
    named = params['named']
    pos = params['pos']
    elude = params['elude']

    args = pos

    args = each(args, lambda x: real(snake_case(x)))
    if elude:
        args
    kwargs = {}
    bridge_kwargs = {}
    for k,v in named.items():
        type = v['type']
        value = v['value']
        k = snake_case(k)
        if k == 'class': k = 'cls'
        bridge_kwargs[k] = real(k)

        val = None
        match type:

            case 'group':
                val = {}
            case 'bool':
                val = 'True' if value == 'true' else 'False'
            case 'auto':
                val = real(value)
            case 'ident':
                val = 'None'
            case 'none':
                val = 'None'
            case 'string':
                val = value
            case 'sign':
                d, u = matchstr(value, '(-\d+(?:\.\d+)?)(.*)')
                aliases = {
                    'in': 'inches'
                }
                u = aliases.get(u, u)
                val = pycall(u, real(d))
            case 'number':
                d, u = matchstr(value, '(\d+(?:\.\d+)?)(.*)')
                aliases = {
                    'in': 'inches'
                }
                if u:
                    u = aliases.get(u, u)
                    val = pycall(u, real(d))
                else:
                    val = real(d)
            case _:
                print(k, v)
                panic('not handled yet ... only none string and numbers')

        kwargs[k] = real(val)

    elude = None
    body = pythonfmt.real_decl('return', pythonfmt.call2('bridge', [snake_case(name), *args], bridge_kwargs, elude))
    return pythonfmt.func_decl2(snake_case(name), args, kwargs, body, elude)


def write_as_python():
    
    out = '~/data/codelib/typst.json'
    data = readfile(out)
    s = join_text(each(data, json_to_typst_func))
    pyout = '~/projects/hammymathclass/python/pytypst/macros.py'
    writefile(pyout, top + "\n" + s)



top = """

from pytypst.primitives import *
from kevinlulee.typstfmt import typstfmt


class bridge:
    template = '%s'
    opts = {}

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        template = getattr(self, 'template', '%s')
        v = typst.call(self.name, *self.args, **self.kwargs)
        return template % v


def box(
    *content,
    width=None,
    height=None,
    inset=None,
    outset=None,
    stroke=None,
    radius=None,
    fill=None,
    clip=None,
    align=None,
    breakable=None,
    display=None
):
    return bridge(
        "box",
        *content,
        width=width,
        height=height,
        inset=inset,
        outset=outset,
        stroke=stroke,
        radius=radius,
        fill=fill,
        clip=clip,
        align=align,
        breakable=breakable,
        display=display
    )
"""
write_as_python()
