import pytest

from boltons.setutils import complement


@pytest.mark.parametrize('operand', [{2}, frozenset({2}), [2], (2,), iter([2])])
def test_finite_complement_discard_removes_operand_members(operand):
    relation = complement(complement({1, 2, 3}))
    assert relation.discard(operand) is None
    assert set(relation) == {1, 3}


def test_discard_does_not_remove_operand_as_one_element():
    nested = frozenset({2})
    relation = complement(complement({1, 2, nested}))
    relation.discard([2])
    assert set(relation) == {1, nested}


@pytest.mark.parametrize('included', [True, False])
@pytest.mark.parametrize('operand_included', [True, False])
def test_complement_discard_matches_difference(included, operand_included):
    def create(values, finite):
        return complement(complement(set(values))) if finite else complement(set(values))
    relation = create({1, 2, 3}, included)
    operand = create({2, 4}, operand_included)
    expected = relation - operand
    relation.discard(operand)
    assert relation == expected
