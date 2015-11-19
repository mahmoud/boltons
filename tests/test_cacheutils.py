# -*- coding: utf-8 -*-

import string

from boltons.cacheutils import LRU, LRI


def test_lru_add():
    cache = LRU(max_size=3)
    for i in range(4):
        cache[i] = i
    assert len(cache) == 3
    assert 0 not in cache


def test_lri():
    bc = LRI(10, on_miss=lambda k: k.upper())
    for char in string.ascii_letters:
        x = bc[char]
        assert x == char.upper()
    assert len(bc) == 10


def test_lru():
    lru = LRU(max_size=1)
    repr(lru)                   # sanity

    lru['hi'] = 0
    lru['bye'] = 1
    assert len(lru) == 1
    lru['bye']
    assert lru.get('hi') is None

    del lru['bye']
    assert 'bye' not in lru
    assert len(lru) == 0
    assert not lru

    try:
        lru.pop('bye')
    except KeyError:
        pass
    else:
        assert False

    default = object()
    assert lru.pop('bye', default) is default

    try:
        lru.popitem()
    except KeyError:
        pass
    else:
        assert False

    lru['another'] = 1
    assert lru.popitem() == ('another', 1)

    lru['yet_another'] = 2
    assert lru.pop('yet_another') == 2

    lru['yet_another'] = 3
    assert lru.pop('yet_another', default) == 3

    lru['yet_another'] = 4
    lru.clear()
    assert not lru

    lru['yet_another'] = 5
    second_lru = LRU(max_size=1)
    assert lru.copy() == lru

    second_lru['yet_another'] = 5
    assert second_lru == lru
    assert lru == second_lru

    lru.update(LRU(max_size=2, values=[('a', 1),
                                       ('b', 2)]))
    assert len(lru) == 1
    assert 'yet_another' not in lru

    lru.setdefault('x', 2)
    assert dict(lru) == {'x': 2}
    lru.setdefault('x', 3)
    assert dict(lru) == {'x': 2}

    assert lru != second_lru
    assert second_lru != lru


def test_lru_with_dupes():
    lru = LRU(max_size=2)
    for i in [0, 0, 1, 1, 2, 2]:
        lru[i] = i
