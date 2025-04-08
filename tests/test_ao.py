import pytest
from kevinlulee.ao import group


def test_group_with_tuples():
    items = [("a", 1), ("b", 2), ("a", 3)]
    expected = {"a": [1, 3], "b": [2]}
    assert group(items) == expected


def test_group_with_dicts_key_str():
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "veg", "name": "carrot"},
    ]
    expected = {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "veg": [{"type": "veg", "name": "carrot"}],
    }
    assert group(items, key="type") == expected


def test_group_with_dicts_key_callable():
    items = [{"k": 1}, {"k": 2}, {"k": 1}]
    expected = {1: [{"k": 1}, {"k": 1}], 2: [{"k": 2}]}
    assert group(items, key=lambda d: d["k"]) == expected


def test_group_dicts_without_key_raises():
    items = [{"x": 1}]
    with pytest.raises(ValueError):
        group(items)


def test_invalid_structure_raises():
    with pytest.raises(ValueError):
        group([("a",)])  # not a 2-element tuple
