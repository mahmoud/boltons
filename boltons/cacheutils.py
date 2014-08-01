# -*- coding: utf-8 -*-

import itertools
from collections import deque

try:
    from _thread import RLock
except:
    class RLock(object):
        'Dummy reentrant lock for builds without threads'
        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass


__all__ = ['BasicCache']


class BasicCache(dict):
    """\
    a.k.a, SizeLimitedDefaultDict. LRI/Least Recently Inserted.
    """
    def __init__(self, size, on_miss):
        super(BasicCache, self).__init__()
        self.size = size
        self.on_miss = on_miss
        self._queue = deque()

    def __missing__(self, key):
        ret = self.on_miss(key)
        self[key] = ret
        self._queue.append(key)
        if len(self._queue) > self.size:
            old = self._queue.popleft()
            del self[old]
        return ret

    try:
        from collections import defaultdict
    except ImportError:
        # no defaultdict means that __missing__ isn't supported in
        # this version of python, so we define __getitem__
        def __getitem__(self, key):
            try:
                return super(BasicCache, self).__getitem__(key)
            except KeyError:
                return self.__missing__(key)
    else:
        del defaultdict


PREV, NEXT, KEY, RESULT = range(4)   # names for the link fields


class LRU(dict):
    # TODO: corner cases size=0, size=None
    def __init__(self, max_size=128, on_miss=None):
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        self._id_gen = itertools.count()
        root = []
        root[:] = [root, root, None, None]
        self.root = root
        self.lock = RLock()

    def __setitem__(self, key, value):
        with self.lock:
            # TODO: check for already-inserted?
            root = self.root
            if len(self) <= self.max_size:
                # to the front of the queue
                last = root[PREV]
                link = [last, root, key, value]
                last[NEXT] = root[PREV] = link
                super(LRU, self).__setitem__(key, link)
            else:
                # Use the old root to store the new key and result.
                oldroot = root
                oldroot[KEY] = key
                oldroot[RESULT] = value
                # Empty the oldest link and make it the new root.
                # Keep a reference to the old key and old result to
                # prevent their ref counts from going to zero during the
                # update. That will prevent potentially arbitrary object
                # clean-up code (i.e. __del__) from running while we're
                # still adjusting the links.
                root = oldroot[NEXT]
                oldkey, oldresult = root[KEY], root[RESULT]
                root[KEY] = root[RESULT] = None
                # Now update the cache dictionary.
                super(LRU, self).__delitem__(oldkey)
                # Save the potentially reentrant cache[key] assignment
                # for last, after the root and links have been put in
                # a consistent state.
                super(LRU, self).__setitem__(key, oldroot)
        return

    def __getitem__(self, key):
        with self.lock:
            try:
                link = super(LRU, self).__getitem__(key)
            except KeyError:
                self.miss_count += 1
                raise
            root = self.root
            if link is not None:
                # Move the link to the front of the circular queue
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = root[PREV]
                last[NEXT] = root[PREV] = link
                link[PREV] = last
                link[NEXT] = root
                self.hit_count += 1
                return result

        # TODO: on_miss/defaulting


def test_basic_cache():
    import string
    bc = BasicCache(10, lambda k: k.upper())
    for char in string.letters:
        x = bc[char]
        assert x == char.upper()
    assert len(bc) == 10


def test_lru_cache():
    lru = LRU()
    lru['hi'] = 5
    print lru['hi']


if __name__ == '__main__':
    test_lru_cache()
