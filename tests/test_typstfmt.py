from kevinlulee.typstfmt import typstfmt

def test_format_primitives():
    assert typstfmt.format(None) == "none"
    assert typstfmt.format(True) == "true"
    assert typstfmt.format(False) == "false"
    assert typstfmt.format("hello") == '"hello"'
    assert typstfmt.format("$math$") == "$math$"
    assert typstfmt.format("`code`") == "`code`"

def test_format_list():
    assert typstfmt.format([1, 2]) == '(1, 2)'
    assert typstfmt.format(["one"]) == '("one",)'

def test_format_dict_simple():
    assert typstfmt.format({"width": "100px"}) == '(width: 100px)'

def test_format_dict_coerce_int():
    assert typstfmt.format({"width": 12}, coerce=True) == '(width: 12pt)'

def test_format_dict_coerce_rotate():
    assert typstfmt.format({"rotate": 30}, coerce=True) == '(rotate: 30deg)'

def test_format_dict_coerce_fill_color():
    assert typstfmt.format({"fill": "red"}, coerce=True) == '(fill: red)'

def test_decl():
    assert typstfmt.decl("x", 123) == "let x = 123"
    assert typstfmt.decl("y", 123, toplevel=True) == "#let y = 123"

def test_call_no_kwargs():
    assert typstfmt.call("foo", 1, 2, coerce=False) == "foo(1, 2)"

def test_call_with_kwargs_and_coerce():
    result = typstfmt.call("draw", width=100, height="42px", coerce=True)
    assert result == "draw(width: 100pt, height: 42px)"

def test_call_toplevel():
    result = typstfmt.call("draw", 1, a=2, toplevel=True, coerce=False)
    assert result == "#draw(1, a: 2)"

def test_comment_and_include():
    assert typstfmt.comment("note") == "// note"
    assert typstfmt.include("file.typ") == 'include "file.typ"'
    assert typstfmt.include("main.typ", toplevel=True) == '#include "main.typ"'

