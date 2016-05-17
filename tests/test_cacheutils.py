# -*- coding: utf-8 -*-

import string

from boltons.cacheutils import LRU, LRI, cached


class CountingCallable(object):
    def __init__(self):
        self.call_count = 0

    def __call__(self, *a, **kw):
        self.call_count += 1
        return self.call_count


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


def test_lru_basic():
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
    SIZE = 2
    lru = LRU(max_size=SIZE)
    for i in [0, 0, 1, 1, 2, 2]:
        lru[i] = i
        assert _test_linkage(lru._anchor, SIZE + 1), 'linked list invalid'


def test_lru_with_dupes_2():
    "From Issue #55, h/t github.com/mt"
    SIZE = 3
    lru = LRU(max_size=SIZE)
    keys = ['A', 'A', 'B', 'A', 'C', 'B', 'D', 'E']
    for i, k in enumerate(keys):
        lru[k] = 'HIT'
        assert _test_linkage(lru._anchor, SIZE + 1), 'linked list invalid'

    return


def _test_linkage(dll, max_count=10000, prev_idx=0, next_idx=1):
    """A function to test basic invariants of doubly-linked lists (with
    links made of Python lists).

    1. Test that the list is not longer than a certain length
    2. That the forward links (indicated by `next_idx`) correspond to
    the backward links (indicated by `prev_idx`).

    The `dll` parameter is the root/anchor link of the list.
    """
    start = cur = dll
    i = 0
    prev = None
    while 1:
        if i > max_count:
            raise Exception("did not return to anchor link after %r rounds"
                            % max_count)
        if prev is not None and cur is start:
            break
        prev = cur
        cur = cur[next_idx]
        if cur[prev_idx] is not prev:
            raise Exception('prev_idx does not point to prev at i = %r' % i)
        i += 1

    return True


def test_callable_cache():
    lru = LRU()
    get_lru = lambda: lru

    inner_func = CountingCallable()
    func = cached(get_lru)(inner_func)

    assert inner_func.call_count == 0
    func()
    assert inner_func.call_count == 1
    func()
    assert inner_func.call_count == 1

    lru.clear()

    func()
    assert inner_func.call_count == 2
    func()
    assert inner_func.call_count == 2
    return
