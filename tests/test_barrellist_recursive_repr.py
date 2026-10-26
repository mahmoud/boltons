import pytest

from boltons.listutils import BarrelList


class CustomBarrelList(BarrelList):
    pass


@pytest.mark.parametrize('cls', [BarrelList, CustomBarrelList])
def test_self_referential_repr(cls):
    items = cls()
    items.append(items)
    assert repr(items) == '%s([...])' % cls.__name__
    assert len(items) == 1
    assert items[0] is items


def test_mutually_recursive_repr():
    first, second = BarrelList(), BarrelList()
    first.append(second)
    second.append(first)
    assert repr(first) == 'BarrelList([BarrelList([...])])'


def test_recursion_through_builtin_list():
    inner = []
    items = BarrelList([inner])
    inner.append(items)
    assert repr(items) == 'BarrelList([[...]])'


def test_shared_acyclic_values_are_not_suppressed():
    child = BarrelList([1])
    assert repr(BarrelList([child, child])) == (
        'BarrelList([BarrelList([1]), BarrelList([1])])')


def test_repr_guard_is_cleared_after_element_error():
    class Broken:
        def __repr__(self):
            raise ValueError('broken repr')

    items = BarrelList([Broken()])
    with pytest.raises(ValueError, match='broken repr'):
        _ = repr(items)
    items[0] = 1
    assert repr(items) == 'BarrelList([1])'


@pytest.mark.parametrize('values', [[], [1, 2], ['a', None], [[1], [2]]])
def test_nonrecursive_repr_is_unchanged(values):
    assert repr(BarrelList(values)) == 'BarrelList(%r)' % values
