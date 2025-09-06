# test_kx.colon_dict.py
import pytest
import kevinlulee as kx


def test_basic_multiline_and_inline():
    text = (
        "a:\n"
        "line1\n"
        "\n"         # skipped because skip_empty_strings=True by default
        "line2\n"
        "b: val\n"
        "c:\n"       # empty block -> skipped
        " \n"
    )
    out = kx.colon_dict(text)
    assert out == {"a": "line1\nline2", "b": "val"}


def test_strict_inline_rejects_followup_content():
    text = "a: v\nextra line"
    with pytest.raises(ValueError):
        kx.colon_dict(text, strict=True)


def test_unrecognized_header_treated_as_content_with_allowlist():
    transformers = {
        "a": lambda x: x,
        "b": int,
    }
    text = (
        "a:\n"
        "first\n"
        "x: not-allowed-as-header\n"  # becomes content of 'a'
        "b: 2\n"
    )
    out = kx.colon_dict(text, transformers=transformers)
    assert out["a"] == "first\nx: not-allowed-as-header"
    assert out["b"] == 2


def test_strict_inline_with_disallowed_header_raises():
    transformers = {"a": lambda x: x}
    text = "a: v\nx: still content"
    with pytest.raises(ValueError):
        kx.colon_dict(text, strict=True, transformers=transformers)


def test_skip_empty_strings_false_includes_empty_block():
    text = "a:\n\n\n"  # all-blank content
    out = kx.colon_dict(text, skip_empty_strings=False)
    # Joining and strip() yields empty string
    assert "a" in out and out["a"] == ""


def test_repeated_keys_last_value_wins_by_default():
    text = "k: one\nk: two\nk:\nthree"
    out = kx.colon_dict(text)
    assert out["k"] == "three"


def test_repeated_keys_collect_with_pluralization():
    text = "k: one\nk: two\nk:\nthree"
    out = kx.colon_dict(text, allow_repeated_keys=True)
    plural_key = kx.pluralize("k")
    assert plural_key in out
    assert out[plural_key] == ["one", "two", "three"]


def test_transformers_applied():
    transformers = {"a": str.upper, "n": int}
    text = "a: hello\nn: 41\nn: 42"
    out_last = kx.colon_dict(text, transformers=transformers)
    assert out_last["a"] == "HELLO"
    assert out_last["n"] == 42

    out_all = kx.colon_dict(text, transformers=transformers, allow_repeated_keys=True)
    pkey = kx.pluralize("n")
    assert out_all[pkey] == [41, 42]


# test_colon_dict.py
import pytest
import kevinlulee as kx

# If colon_dict is in a different module file, import it accordingly.
# from your_module import colon_dict


def test_basic_block_parsing_last_wins_default():
    text = """a:
line 1
line 2
b:
hello
a:
overwrites"""
    out = colon_dict(text)
    assert out["a"] == "overwrites"
    assert out["b"] == "hello"


def test_inline_value_and_followup_content_non_strict():
    text = """title: My Doc
This is line one.
This is line two.
next:
content"""
    out = colon_dict(text, strict=False)
    # Inline value is kept, and subsequent content is appended.
    assert out["title"] == "My Doc\nThis is line one.\nThis is line two."
    assert out["next"] == "content"


def test_inline_value_and_followup_content_strict_raises():
    text = """title: My Doc
extra line"""
    with pytest.raises(ValueError):
        colon_dict(text, strict=True)


def test_skip_empty_strings_default_skips_empty_blocks():
    text = """empty:
nonempty:
data"""
    out = colon_dict(text)
    # 'empty' had no content — should be absent when skipping empties (default).
    assert "empty" not in out
    assert out["nonempty"] == "data"


def test_skip_empty_strings_false_keeps_empty_blocks():
    text = """empty:
nonempty:
"""
    out = colon_dict(text, skip_empty_strings=False)
    # Expect empty string (post-strip) to be kept.
    assert out["empty"] == ""
    assert out["nonempty"] == ""


def test_allow_repeated_keys_true_collects_list():
    text = """tag: one
tag: two
tag:
three
"""
    out = colon_dict(text, allow_repeated_keys=True)
    plural_key = kx.pluralize("tag")
    assert plural_key in out
    # Three occurrences: "one", "two", and "three"
    assert out[plural_key] == ["one", "two", "three"]


def test_transformers_apply_and_gate_headers_by_allowlist():
    # Only 'a' and 'b' are recognized as headers. 'c:' should be treated as content.
    text = """a:
alpha
c: not a header here
b: BETA"""
    transformers = {
        "a": lambda v: str(v).upper(),  # 'alpha\nc: not a header here' -> upper
        "b": lambda v: str(v).lower(),  # 'BETA' -> 'beta'
    }
    out = colon_dict(text, transformers=transformers)
    assert "a" in out and "b" in out
    assert out["a"] == "ALPHA\nC: NOT A HEADER HERE"
    assert out["b"] == "beta"


def test_transformers_unrecognized_header_at_top_is_ignored():
    # Because transformers is provided, only those keys are headers.
    # Leading "x:" is not recognized and there's no active block, so it is ignored.
    text = """x: should be ignored entirely
a: keep me"""
    transformers = {"a": lambda v: v}
    out = colon_dict(text, transformers=transformers)
    assert "a" in out and out["a"] == "keep me"
    assert "x" not in out


def test_bracketed_headers_basic_parsing():
    text = """[title] Hello
[body]
Line 1
Line 2
[title] Overwrite"""
    out = colon_dict(text)
    assert out["title"] == "Overwrite"
    assert out["body"] == "Line 1\nLine 2"


def test_bracketed_headers_inline_plus_strict_violation():
    text = """[h] inline val
more"""
    with pytest.raises(ValueError):
        colon_dict(text, strict=True)


def test_mixed_content_whitespace_preservation_and_trailing_newlines():
    text = "a:\n  line with leading spaces\n\n\nb:\nline\n\n"
    out = colon_dict(text)
    # Internal spacing within lines is preserved; blank lines are collapsed via strip at flush.
    assert out["a"] == "line with leading spaces"
    assert out["b"] == "line"


def test_multiline_blocks_and_transformer_pipeline():
    # Transformer sees the value *after* kx.coerce_argument.
    # Make the transformer robust to both strings and other types.
    text = """items:
a, b, c
count: 0042
"""
    transformers = {
        "items": lambda v: [s.strip() for s in str(v).split(",") if s.strip()],
        "count": lambda v: int(v),
    }
    out = colon_dict(text, transformers=transformers)
    assert out["items"] == ["a", "b", "c"]
    assert out["count"] == 42

