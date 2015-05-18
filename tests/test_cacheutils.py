# -*- coding: utf-8 -*-

import string

from boltons.cacheutils import LRU, LRI


def test_popitem_should_return_a_tuple():
    cache = LRU()
    cache['t'] = 42
    assert cache.popitem() == ('t', 42)


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
    lru['hi'] = 0
    lru['bye'] = 1
    assert len(lru) == 1
    lru['bye']
    assert lru.get('hi') is None

    del lru['bye']
    assert 'bye' not in lru
    assert len(lru) == 0
    assert not lru
