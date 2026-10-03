import sys

import pytest

from boltons.listutils import BarrelList


def make_barrel_list(values, partitioned):
    value = BarrelList(values)
    if partitioned:
        # Include an empty barrel, as can remain after deleting its items.
        value.lists = [values[:4], [], values[4:8], values[8:]]
    return value


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('size', [0, 1, 12])
@pytest.mark.parametrize('count', [-2, 0, 1, 2, 3, False, True])
def test_inplace_repeat_matches_list(partitioned, size, count):
    reference = list(range(size))
    value = make_barrel_list(reference, partitioned)
    alias = value

    reference *= count
    value *= count

    assert value is alias
    assert type(value) is BarrelList
    assert list(value) == reference
    assert len(value) == len(reference)
    assert list(reversed(value)) == list(reversed(reference))
    value.append('after')
    reference.append('after')
    assert list(value) == reference


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('count', [-1, 0, 1, 3])
def test_inplace_repeat_index_protocol(partitioned, count):
    class Index:
        calls = 0

        def __index__(self):
            self.calls += 1
            return count

    index = Index()
    value = make_barrel_list(list(range(12)), partitioned)
    result = value.__imul__(index)

    assert result is value
    assert index.calls == 1
    assert list(value) == list(range(12)) * count


@pytest.mark.parametrize('partitioned', [False, True])
def test_inplace_repeat_converts_count_before_copying_values(partitioned):
    value = make_barrel_list(list(range(12)), partitioned)

    class Index:
        def __index__(self):
            value.append('added during conversion')
            return 2

    value *= Index()

    assert list(value) == (list(range(12)) + ['added during conversion']) * 2


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('count', [2.5, '2', None, sys.maxsize + 1, -sys.maxsize - 2])
def test_inplace_repeat_invalid_count_leaves_values_unchanged(partitioned, count):
    reference = list(range(12))
    value = make_barrel_list(reference, partitioned)

    with pytest.raises((TypeError, OverflowError)) as exc_info:
        reference *= count
    with pytest.raises(type(exc_info.value)):
        value *= count

    assert list(value) == reference == list(range(12))


@pytest.mark.parametrize('partitioned', [False, True])
def test_inplace_repeat_shares_elements_not_barrels(partitioned):
    item = []
    value = make_barrel_list([item, 'other'], partitioned)
    value *= 3

    assert len(value) == 6
    assert value[0] is value[2] is value[4] is item
    item.append('shared')
    assert list(value) == [['shared'], 'other'] * 3
    value[0] = 'replacement'
    assert value[2] is value[4] is item
    assert list(value) == ['replacement', 'other', ['shared'], 'other', ['shared'], 'other']


def test_inplace_repeat_balances_large_list():
    reference = list(range(100000))
    value = BarrelList(reference)
    value._balance_list(0)
    assert len(value.lists) > 1

    reference *= 2
    value *= 2

    assert list(value) == reference
    assert len(value.lists) > 1
    assert max(map(len, value.lists)) <= value._cur_size_limit
    assert value.pop(100000) == reference.pop(100000)
    assert list(value) == reference
