import pytest

from boltons.setutils import IndexedSet


@pytest.mark.parametrize('method', ['issubset', 'issuperset'])
@pytest.mark.parametrize('factory', [
    list, tuple, iter, set, frozenset, IndexedSet, dict.fromkeys,
])
@pytest.mark.parametrize('values, other_values', [
    ([], []),
    ([], [1, 1]),
    ([1], []),
    ([1], [1, 1]),
    ([1, 3], [3, 1, 3]),
    ([1, 3], [1, 1]),
    ([1, 3], [1, 2, 3]),
    ([1, 3], [3, 2]),
])
def test_relations_match_builtin_sets(method, factory, values, other_values):
    items = IndexedSet(values)
    expected = getattr(set(values), method)(other_values)

    assert getattr(items, method)(factory(other_values)) is expected
    assert list(items) == values


@pytest.mark.parametrize('method', ['issubset', 'issuperset'])
def test_relations_accept_one_shot_generators(method):
    items = IndexedSet([1, 3])
    other = (value for value in [3, 1, 3])

    assert getattr(items, method)(other) is True
    assert list(items) == [1, 3]


def test_issuperset_stops_at_first_missing_value():
    def values():
        yield 2
        raise AssertionError('the remaining input should not be consumed')

    assert IndexedSet([1]).issuperset(values()) is False
