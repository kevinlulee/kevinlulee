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

