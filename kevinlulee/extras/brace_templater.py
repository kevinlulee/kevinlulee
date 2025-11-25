import re
from kevinlulee.extras.line_edit import LineEdit
import kevinlulee as kx

TEMPLATER_PATTERN = re.compile(
    r"""
        (?:(\n)([ \t]+))?  # optional newline spaces
        {(\d+|[a-zA-Z]\w*(?:\.\w+(?:\(.*?\))?)*)}   # bracket containing an expr-like string
    """,
    flags=re.VERBOSE,
)

base_re = re.compile("^(?:\d+|[a-zA-Z]\w*(?:\.\w+(?:\(.*?\))?)*)$")
logic_re = re.compile(" (and|or|not) ")

TEMPLATER_PATTERN2 = re.compile(
    r"""
        (?:(\n)([ \t]+))?  # optional newline spaces
        {(.*?)}   # bracket containing an expr-like string
    """,
    flags=re.VERBOSE,
)


def remove_empty_placeholders(s):
    if "<EMPTY>" not in s:
        return s

    le = LineEdit(s)
    lines = le.findall("<EMPTY>")

    for line in lines:
        if line.prev().match(':$'):
            line.prev().delete()
            line.delete()
            line.prev().prev().delete()
        elif line.prev().match("---") and line.next().match("---"):
            if line.prev().prev().has_text():
                line.prev().prev().delete()
            line.prev().delete()
            line.next().delete()
            line.delete()
        else:
            line.delete()

    return str(le)


def brace_templater2(s, ref, recursive=False):
    def replacer(match):
        newline, ind, key_or_expr = match.groups()
        v = ref.get(key_or_expr) or eval(key_or_expr, ref)

        if v is None or v == [] or v == {}:
            return "<EMPTY>"

        if recursive and isinstance(v, str) and kx.test(v, TEMPLATER_PATTERN):
            v = re.sub(TEMPLATER_PATTERN, replacer, v)

        if isinstance(v, str):
            v = kx.trimdent(v)
        elif kx.is_array(v) and isinstance(v[0], str):
            v = kx.join_text(v)

        payload = kx.serialize_data(v)
        return kx.newline_indent(payload, ind) if newline else payload

    assert s, "empty text was provided"
    s = re.sub(TEMPLATER_PATTERN, replacer, kx.trimdent(s))
    return remove_empty_placeholders(s)


def brace_templater(s, ref, cls=None, wrap_func=None):
    """
    a simpler version of templater.
    uses {braces}.

    class objects are allowed
    the entity contained in {brace} must be an expression.
    otherwise it will not be pattern matched.

    """
    if kx.is_array(ref):
        ref = kx.array_to_dict(ref)

    elif not kx.is_dict(ref):
        ref = {"1": ref}

    if cls:
        ref["self"] = cls

    def get(expr):
        if kx.test(expr, " (and|or|not) "):
            # logic based
            keys = ref.keys()
            scope = kx.merge_dicts(dict(kx=kx), ref)
            value = eval(expr, scope)
            return value or None

        if kx.test(expr, r"\bself\b"):
            s = eval(expr, ref)
            return s

        if kx.test(expr, r"\w+\("):
            s = eval(expr)
            return s
        return ref.get(expr)

    def replacer(match):
        newline, ind, expr = match.groups()
        if kx.is_word(expr) or base_re.search(expr) or logic_re.search(expr):
            pass
        else:
            return match.group(0)

        g = get(expr)
        if g is None or g == '':
            return "<EMPTY>"
        if wrap_func:
            g = wrap_func(g)
        payload = kx.serialize_data(g)
        return kx.newline_indent(payload, ind) if newline else payload

    s = re.sub(TEMPLATER_PATTERN2, replacer, kx.trimdent(s))

    if "<EMPTY>" not in s:
        return s

    return remove_empty_placeholders(s)


# kx.pretty_print(brace_templater('''foobar\n\n\t{not kx.test(body, 'example|sample', flags = kx.re.I) and examples}''', dict(body = 'hi', examples = 'asdf\nasdf')))
# kx.pretty_print(brace_templater('''{foobar}''', dict(foobar = 'hi')))
s = """
                a


                Helpers:
                {a}
                    {a}
                        {name, alias, items}
                hi
"""
if __name__ == '__main__':
    kx.pretty_print(brace_templater(s, dict(a =None)))
