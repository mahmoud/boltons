import pytest

from boltons.dictutils import OneToOne


@pytest.mark.parametrize("inverse", [False, True])
@pytest.mark.parametrize("outer", [list, iter])
def test_update_accepts_one_shot_pairs(inverse, outer):
    mapping = OneToOne({"old": 0})
    target = mapping.inv if inverse else mapping
    pairs = [("a", 1), ("b", 2)]
    target.update(outer(iter(pair) for pair in pairs))
    assert target["a"] == 1
    assert target["b"] == 2
    assert target.inv[1] == "a"
    assert target.inv[2] == "b"
    assert target.inv.inv is target


@pytest.mark.parametrize("bad_pair", [("a",), ("a", 1, 2), ("a", [])])
def test_invalid_iterator_pair_does_not_mutate(bad_pair):
    mapping = OneToOne({"old": 0})
    with pytest.raises((ValueError, TypeError)):
        mapping.update([iter(("new", 1)), iter(bad_pair)])
    assert dict(mapping) == {"old": 0}
    assert dict(mapping.inv) == {0: "old"}
