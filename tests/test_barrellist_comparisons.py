import operator

import pytest

from boltons.listutils import BarrelList


COMPARISONS = (operator.eq, operator.ne, operator.lt, operator.le,
               operator.gt, operator.ge)


def partitioned(values):
    result = BarrelList()
    result.lists = [[], values[:1], [], values[1:], []]
    return result


@pytest.mark.parametrize('compare', COMPARISONS)
@pytest.mark.parametrize('left,right', [
    ([], []), ([1], []), ([], [1]), ([1], [1]), ([1], [2]),
    ([1, 2], [1, 2]), ([1, 2], [1, 3]), ([1], [1, 2]),
    ([1, 2], [1]), ([[1], [2]], [[1], [3]]),
])
def test_comparisons_match_list(compare, left, right):
    expected = compare(left, right)
    for make_left, make_right in ((BarrelList, list), (list, BarrelList),
                                 (BarrelList, BarrelList),
                                 (partitioned, partitioned)):
        first, second = make_left(left), make_right(right)
        assert compare(first, second) is expected
        assert list(first) == left
        assert list(second) == right


@pytest.mark.parametrize('compare', COMPARISONS)
def test_comparisons_preserve_list_subclass_storage(compare):
    class DifferentIterator(list):
        def __iter__(self):
            return iter([999])

    other = DifferentIterator([1])
    assert compare(BarrelList([1]), other) is compare([1], other)


@pytest.mark.parametrize('method', ['__eq__', '__ne__', '__lt__', '__le__',
                                  '__gt__', '__ge__'])
@pytest.mark.parametrize('other', [(1,), '1', {1}, None])
def test_unsupported_comparisons_return_not_implemented(method, other):
    assert getattr(BarrelList([1]), method)(other) is NotImplemented


def test_comparison_identity_shortcut_and_errors():
    value = float('nan')
    first, second = BarrelList([value]), BarrelList([value])
    assert first == second
    assert not first != second
    assert first <= second
    assert first >= second
    with pytest.raises(TypeError):
        BarrelList([1]) < ['a']


def test_reflected_comparison_dispatch():
    class Reflected:
        def __eq__(self, other):
            return 'equal'

        def __gt__(self, other):
            return 'greater'

    assert (BarrelList([1]) == Reflected()) == 'equal'
    assert (BarrelList([1]) < Reflected()) == 'greater'
