import gc
import weakref

import pytest

from boltons.listutils import BarrelList


@pytest.mark.parametrize('size', [0, 1, 10, 30000])
def test_barrel_list_clear(size):
    reference = list(range(size))
    value = BarrelList(reference)
    value._balance_list(0)
    if size == 30000:
        assert len(value.lists) > 1

    assert value.clear() is reference.clear()
    assert list(value) == reference
    assert len(value) == 0
    assert not value
    with pytest.raises(IndexError):
        value[0]
    with pytest.raises(IndexError):
        value.pop()

    # Clearing an empty list repeatedly must leave it usable.
    assert value.clear() is None
    value.append(2)
    value.insert(0, 1)
    value.extend([3, 4])
    value[1] = 20
    del value[2]
    assert list(value) == [1, 20, 4]
    assert value.pop() == 4
    assert len(value) == 2


@pytest.mark.parametrize('advance_iterator', [False, True])
def test_barrel_list_clear_releases_items(advance_iterator):
    class Item:
        pass

    value = BarrelList([Item(), Item()])
    references = [weakref.ref(item) for item in value]
    iterator = iter(value)
    if advance_iterator:
        next(iterator)

    value.clear()
    gc.collect()

    assert all(reference() is None for reference in references)
    assert list(iterator) == []
