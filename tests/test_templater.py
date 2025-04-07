from pathlib import Path
from kevinlulee import templater, trimdent
import pytest

test_cases = [
    {
        "desc": "Simple variable substitution",
        "template": "Hello $name",
        "ref": {"name": "Alice"},
        "expected": "Hello Alice"
    },
    {
        "desc": "Bullet list with hyphens",
        "template": "- $items",
        "ref": {"items": ["a", "b", "c"]},
        "expected": "- a\n- b\n- c"
    },
    {
        "desc": "Multiline hyphen list",
        "template": """
            - $items
        """,
        "ref": {"items": ["x", "y"]},
        "expected": "- x\n- y"
    },
    {
        "desc": "Dot list format",
        "template": """
            • $items
            foobar
        """,
        "ref": {"items": ["apple", "banana"]},
        "expected": "• apple\n• banana\nfoobar"
    },
    {
        "desc": "Simple bracket math expression",
        "template": "Sum: ${1 + 2 + 3}",
        "ref": {},
        "expected": "Sum: 6"
    },
    {
        "desc": "Bracket expression using scope vars",
        "template": "Total: ${$a + $b}",
        "ref": {"a": 4, "b": 7},
        "expected": "Total: 11"
    },
    {
        "desc": "List with comma suffix (no terminal comma)",
        "template": "- $things,",
        "ref": {"things": ["red", "green"]},
        "expected": "- red,\n- green"
    },
    {
        "desc": "Multiline spacing preserved in bullet list",
        "template": """
            - $items
        """,
        "ref": {"items": ["alpha", "beta"]},
        "expected": "- alpha\n- beta"
    },
    {
        "desc": "Inline list without bullet is not allowed",
        "template": "$list",
        "ref": {"list": ["one", "two"]},
        "exception": True,
    },
    {
        "desc": "Variable with newline spacing will be trimdented",
        "template": "\n  $message",
        "ref": {"message": "hello"},
        "expected": "hello"
    },
    {
        "desc": "two variables on subsequent lines",
        "template": "$hello\n$farewell",
        "ref": {"hello": "hello", "farewell": "farewell"},
        "expected": "hello\nfarewell"
    },
    {
        "desc": "two variables on subsequent lines will be trimdented",
        "template": "\n  $hello\n  $farewell",
        "ref": {"hello": "hello", "farewell": "farewell"},
        "expected": "hello\nfarewell"
    },
    {
        "desc": "two variables on subsequent lines with different indent",
        "template": "\n  $hello\n    $farewell",
        "ref": {"hello": "hello", "farewell": "farewell"},
        "expected": "hello\n  farewell"
    },
    {
        "desc": "object return not allowed. only lists and strings",
        "template": "$abc",
        "ref": {"abc": {'alpha': 1}},
        "exception": True
    },
]


def run(case):
    return templater(trimdent(case["template"]), case["ref"])

@pytest.mark.parametrize("case", test_cases, ids=[case["desc"] for case in test_cases])
def test_templater_cases(case):
    if case.get("exception"):
        with pytest.raises(Exception): 
            run(case)
    else:
        assert run(case) == case['expected']

