import pytest

from boltons.dictutils import OneToOne


def test_update_without_arguments_is_noop():
    relation = OneToOne({"a": 1})
    assert relation.update() is None
    assert relation == {"a": 1}
    assert relation.inv == {1: "a"}


def test_keyword_only_update_keeps_inverse_synchronized():
    relation = OneToOne({"a": 1, "b": 2})
    inverse = relation.inv
    assert relation.update(a=3, c=2) is None
    assert relation == {"a": 3, "c": 2}
    assert relation.inv is inverse
    assert inverse == {3: "a", 2: "c"}


def test_keyword_only_update_validates_before_mutating():
    relation = OneToOne({"a": 1})
    with pytest.raises(TypeError):
        relation.update(b=2, bad=[])
    assert relation == {"a": 1}
    assert relation.inv == {1: "a"}
