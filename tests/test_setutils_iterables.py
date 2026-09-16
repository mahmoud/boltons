import pytest

from boltons.setutils import IndexedSet


@pytest.mark.parametrize('operation', ['intersection', 'difference', 'symmetric_difference'])
def test_set_operations_accept_one_shot_iterators(operation):
    original = [3, 1, 4, 2]
    other = [2, 3, 5, 5]
    items = IndexedSet(original)
    result = getattr(items, operation)(iter(other))
    expected = getattr(set(original), operation)(other)
    assert set(result) == expected
    assert list(items) == original


def test_symmetric_update_deduplicates_input_and_preserves_order():
    items = IndexedSet([3, 1, 4, 2])
    items.symmetric_difference_update(iter([2, 2, 5, 5]))
    assert list(items) == [3, 1, 4, 5]


def test_symmetric_update_accepts_an_iterator_over_self():
    items = IndexedSet(range(100))
    items.symmetric_difference_update(iter(items))
    assert list(items) == []
