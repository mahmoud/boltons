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

PREV, NEXT, KEY, VALUE = range(4)   # names for the link fields
DEFAULT_MAX_SIZE = 128
_MISSING = object()


__all__ = ['BasicCache', 'LRU', 'DefaultLRU']


# TODO: rename to LRI?
# TODO: on_miss to default_factory
class BasicCache(dict):
    """\
    a.k.a, SizeLimitedDefaultDict. LRI/Least Recently Inserted.

    `on_miss` is a callable that accepts the missing key (as opposed
    to default_factory which accepts no arguments.
    """
    def __init__(self, on_miss, max_size=DEFAULT_MAX_SIZE):
        super(BasicCache, self).__init__()
        self.max_size = max_size
        self.on_miss = on_miss
        self._queue = deque()

    def __missing__(self, key):
        ret = self.on_miss(key)
        self[key] = ret
        self._queue.append(key)
        if len(self._queue) > self.max_size:
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


class LRU(dict):
    def __init__(self, max_size=DEFAULT_MAX_SIZE, values=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        root = []
        root[:] = [root, root, None, None]
        self.link_map = {}
        self.root = root
        self.lock = RLock()

        if values:
            self.update(values)

    # inherited methods: __len__, pop, iterkeys, keys, __iter__
    # TODO: fromkeys()?

    def __setitem__(self, key, value):
        with self.lock:
            root = self.root
            if len(self) < self.max_size:
                # to the front of the queue
                last = root[PREV]
                link = [last, root, key, value]
                last[NEXT] = root[PREV] = link
                self.link_map[key] = link
                super(LRU, self).__setitem__(key, value)
            else:
                # Use the old root to store the new key and result.
                oldroot = root
                oldroot[KEY] = key
                oldroot[VALUE] = value
                # prevent ref counts going to zero during update
                root = oldroot[NEXT]
                oldkey, oldresult = root[KEY], root[VALUE]
                root[KEY] = root[VALUE] = None
                # Now update the cache dictionary.
                del self.link_map[oldkey]
                super(LRU, self).__delitem__(oldkey)
                self.link_map[key] = oldroot
                super(LRU, self).__setitem__(key, value)
        return

    def __getitem__(self, key):
        with self.lock:
            try:
                link = self.link_map[key]
            except KeyError:
                self.miss_count += 1
                raise
            root = self.root
            # Move the link to the front of the queue
            link_prev, link_next, _key, value = link
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev
            last = root[PREV]
            last[NEXT] = root[PREV] = link
            link[PREV] = last
            link[NEXT] = root
            self.hit_count += 1
            return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count += 1
            return default

    def __delitem__(self, key):
        with self.lock:
            link = self.link_map.pop(key)
            super(LRU, self).__delitem__(key)
            link[PREV][NEXT], link[NEXT][PREV] = link[NEXT], link[PREV]

    def pop(self, key, default=_MISSING):
        # NB: hit/miss counts are bypassed for pop()
        try:
            ret = super(LRU, self).__getitem__(key)
            del self[key]
        except KeyError:
            if default is _MISSING:
                raise KeyError(key)
            ret = default
        return ret

    def popitem(self):
        with self.lock:
            link = self.link_map.popitem()
            super(LRU, self).__delitem__(link[KEY])
            link[PREV][NEXT], link[NEXT][PREV] = link[NEXT], link[PREV]

    def clear(self):
        with self.lock:
            self.root = [self.root, self.root, None, None]
            self.link_map.clear()
            super(LRU, self).clear()

    def copy(self):
        return self.__class__(max_size=self.max_size, values=self)

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self.soft_miss_count += 1
            self[key] = default
            return default

    def update(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        setitem = self.__setitem__
        if callable(getattr(E, 'keys', None)):
            for k in E.keys():
                setitem(k, E[k])
        else:
            for k, v in E:
                setitem(k, v)
        for k in F:
            setitem(k, F[k])
        return

    def __eq__(self, other):
        if self is other:
            return True
        if len(other) != len(self):
            return False
        return other == self

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        cn = self.__class__.__name__
        val_map = super(LRU, self).__repr__()
        return '%s(max_size=%r, values=%r)' % (cn, self.max_size, val_map)


class DefaultLRU(LRU):
    """\
    Like a defaultdict, but for the LRU cache. If set, the
    `default_factory` is called on misses and assigned to the missing
    key.
    """
    def __init__(self, default_factory=None, *args, **kwargs):
        if default_factory is not None and not callable(default_factory):
            raise TypeError('expected default_factory to be a callable'
                            ' (or None), not %r' % default_factory)
        self.default_factory = default_factory
        super(DefaultLRU, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if not self.default_factory:
            raise KeyError(key)
        ret = self.default_factory()
        self.soft_miss += 1
        self[key] = ret
        return ret

    try:
        from collections import defaultdict
    except ImportError:
        # no defaultdict means that __missing__ isn't supported in
        # this version of python, so we define __getitem__
        def __getitem__(self, key):
            try:
                return super(DefaultLRU, self).__getitem__(key)
            except KeyError:
                if self.default_factory:
                    return self.__missing__(key)
                raise
    else:
        del defaultdict


def test_basic_cache():
    import string
    bc = BasicCache(10, lambda k: k.upper())
    for char in string.letters:
        x = bc[char]
        assert x == char.upper()
    assert len(bc) == 10


def test_lru_cache():
    lru = LRU(max_size=1)
    lru['hi'] = 0
    lru['bye'] = 1
    lru['bye']
    lru.get('hi')
    print lru
    del lru['bye']

    import pdb;pdb.set_trace()


if __name__ == '__main__':
    test_lru_cache()
