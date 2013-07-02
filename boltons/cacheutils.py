# -*- coding: utf-8 -*-

from collections import deque

__all__ = ['BasicCache']


class BasicCache(dict):
    """\
    a.k.a, SizeLimitedDefaultDict.
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


def test_cache():
    import string
    bc = BasicCache(10, lambda k: k.upper())
    for char in string.letters:
        x = bc[char]
        assert x == char.upper()
    assert len(bc) == 10
