import operator

import pytest

from boltons.listutils import BarrelList


def make_barrel_list(items, partitioned):
    value = BarrelList(items)
    if partitioned:
        value.lists = [[], list(items[:2]), [], list(items[2:]), []]
    return value


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('items', [[], [3], [5, -1, 2, -1, 0]])
@pytest.mark.parametrize(
    'options',
    [
        {},
        {'key': None},
        {'reverse': True},
        {'key': abs},
        {'key': abs, 'reverse': True},
    ],
)
def test_sort_options_match_list(items, partitioned, options):
    value = make_barrel_list(items, partitioned)

    assert value.sort(**options) is None
    assert list(value) == sorted(items, **options)
    assert len(value) == len(items)


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('reverse', [False, True])
def test_key_is_called_once_per_item_and_sort_is_stable(partitioned, reverse):
    items = [
        {'rank': 2, 'name': 'first'},
        {'rank': 1, 'name': 'second'},
        {'rank': 2, 'name': 'third'},
        {'rank': 1, 'name': 'fourth'},
        {'rank': 2, 'name': 'fifth'},
    ]
    value = make_barrel_list(items, partitioned)
    calls = []

    def key(item):
        calls.append(item)
        return item['rank']

    assert value.sort(key=key, reverse=reverse) is None
    assert [id(item) for item in calls] == [id(item) for item in items]
    expected = sorted(items, key=operator.itemgetter('rank'), reverse=reverse)
    assert [id(item) for item in value] == [id(item) for item in expected]


@pytest.mark.parametrize('partitioned', [False, True])
def test_falsey_callable_key(partitioned):
    class Key:
        def __bool__(self):
            return False

        def __call__(self, item):
            return -item

    value = make_barrel_list([1, 3, 2], partitioned)
    value.sort(key=Key())
    assert list(value) == [3, 2, 1]


@pytest.mark.parametrize('partitioned', [False, True])
def test_key_exception_propagates_without_losing_items(partitioned):
    items = [3, 1, 2]
    value = make_barrel_list(items, partitioned)

    def key(item):
        if item == 1:
            raise ValueError('key failed')
        return item

    with pytest.raises(ValueError, match='key failed'):
        value.sort(key=key)
    assert list(value) == items


@pytest.mark.parametrize('partitioned', [False, True])
def test_sort_options_are_keyword_only(partitioned):
    value = make_barrel_list([3, 1, 2], partitioned)
    with pytest.raises(TypeError):
        value.sort(abs)
    assert list(value) == [3, 1, 2]


@pytest.mark.parametrize(
    'options',
    [
        {'reverse': True},
        {'key': abs},
        {'key': abs, 'reverse': True},
    ],
)
def test_sort_options_with_balanced_storage(options):
    items = list(range(-15000, 15000))
    value = BarrelList(items)
    value._balance_list(0)
    assert len(value.lists) > 1

    assert value.sort(**options) is None
    assert list(value) == sorted(items, **options)
    assert len(value.lists) > 1
    assert sum(len(part) for part in value.lists) == len(items)
