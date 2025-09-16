# test_deep_merge.py
from copy import deepcopy
from typing import Any
import pytest
from kevinlulee.extras.deep_merge import deep_merge

def test_none_behavior():
    assert deep_merge(None, {"a": 1}) == {"a": 1}
    assert deep_merge({"a": 1}, None) == {"a": 1}
    assert deep_merge(None, None) is None


def test_empty_containers():
    assert deep_merge({}, {}) == {}
    assert deep_merge([], []) == []
    assert deep_merge((), ()) == ()
    assert deep_merge(set(), set()) == set()


def test_dict_union_and_recursive_merge():
    a = {"x": 1, "y": {"z": [1, 2], "k": {"m": 1}}, "only_a": 10}
    b = {"y": {"z": [None, 3, 4], "k": {"m": 2, "n": 3}}, "only_b": 20}
    out = deep_merge(a, b)
    assert out == {
        "x": 1,
        "y": {"z": [1, 3, 4], "k": {"m": 2, "n": 3}},
        "only_a": 10,
        "only_b": 20,
    }


# def test_list_indexwise_merge_and_append():
#     a = [1, {"a": 1}, [1, 2]]
#     b = [2, {"a": [None, 2]}, [None, None, 3]]
#     out = deep_merge(a, b)
#     assert out == [2, {"a": [1, 2]}, [1, 2, 3]]
#
#     # Different lengths, extra items appended from longer side
#     assert deep_merge([1], [None, 2, 3]) == [1, 2, 3]
#     assert deep_merge([1, 2, 3], [None, None]) == [1, 2, 3]


def test_tuple_merge_keeps_type():
    a = (1, (2, 3))
    b = (None, (4,))
    out = deep_merge(a, b)
    assert isinstance(out, tuple)
    assert out == (1, (4, 3))


def test_set_union():
    assert deep_merge({1, 2}, {2, 3}) == {1, 2, 3}
    assert deep_merge(set(), {1}) == {1}


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 20, 20),  # scalar override
        (True, False, False),
        ("a", "b", "b"),
        ({"k": 1}, [1, 2], [1, 2]),  # type mismatch at top level
        ([1, 2], {"k": 1}, {"k": 1}),
        ({"a": {"b": 1}}, {"a": [1, 2]}, {"a": [1, 2]}),  # type mismatch deep
        ([1, 2], (3, 4), (3, 4)),  # list vs tuple -> b wins
        ((1, 2), [3, 4], [3, 4]),  # tuple vs list -> b wins
    ],
)
def test_type_mismatch_b_overrides(a, b, expected):
    assert deep_merge(a, b) == expected


def test_immutability_inputs_not_mutated():
    a = {"x": [{"y": 1}], "s": {1, 2}, "t": (1, 2), "d": {"k": 1}}
    b = {"x": [{"y": 2, "z": [9]}], "s": {2, 3}, "t": (3,), "d": {"k": 7}}
    a_snapshot = deepcopy(a)
    b_snapshot = deepcopy(b)

    _ = deep_merge(a, b)

    assert a == a_snapshot
    assert b == b_snapshot


def test_result_has_no_shared_references_with_inputs():
    a = {"lst": [{"n": 1}], "inner": {"v": [1, 2]}}
    b = {"lst": [{"n": 2}], "inner": {"v": [None, 3, 4]}}
    out = deep_merge(a, b)

    # Mutate output and ensure inputs unchanged
    out["lst"][0]["n"] = 999
    out["inner"]["v"][0] = -1
    assert a["lst"][0]["n"] == 1
    assert a["inner"]["v"] == [1, 2]

    # Also ensure some obvious non-aliasing at container level
    assert out["lst"] is not a["lst"]
    assert out["inner"] is not a["inner"]
    assert out["inner"]["v"] is not a["inner"]["v"]


def test_complex_nested_mix():
    a = {
        "cfg": {
            "path": "/a",
            "flags": [True, {"opt": {"a": 1}}, {"list": [1, 2]}],
            "nums": (1, 2),
            "tags": {"x", "y"},
        }
    }
    b = {
        "cfg": {
            "path": None,  # keep from a
            "flags": [False, {"opt": {"a": None, "b": 2}}, {"list": [None, 3, 4]}],
            "nums": (None, 3, 4),
            "tags": {"y", "z"},
        }
    }
    out = deep_merge(a, b)
    assert out == {
        "cfg": {
            "path": "/a",
            "flags": [False, {"opt": {"a": 1, "b": 2}}, {"list": [1, 3, 4]}],
            "nums": (1, 3, 4),
            "tags": {"x", "y", "z"},
        }
    }


def test_docstring_example():
    assert deep_merge({"x": 1, "y": {"z": [1, 2]}}, {"y": {"z": [None, 3, 4]}}) == {
        "x": 1,
        "y": {"z": [1, 3, 4]},
    }

