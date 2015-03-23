# -*- coding: utf-8 -*-
"""\
Contains fundamental cache types, including LRU (Least-recently
used) and LRI (Least-recently inserted).

Learn more about `caching algorithms on Wikipedia
<https://en.wikipedia.org/wiki/Cache_algorithms#Examples>`_.
"""
__all__ = ['LRI', 'LRU']

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


class LRU(dict):
    """\
    The ``LRU`` implements the Least-Recently Used caching strategy,
    with ``max_size`` equal to the maximum number of items to be
    cached, ``values`` as the initial values in the cache, and
    ``on_miss`` set to a callable which accepts a single argument, the
    key not present in the cache, and returns the value to be cached.

    This cache is also instrumented with statistics
    collection. ``hit_count``, ``miss_count``, and ``soft_miss_count``
    are all integer members that can be used to introspect the
    performance of the cache. ("Soft" misses are misses that did not
    raise KeyError, e.g., ``LRU.get()`` or ``on_miss`` was used to
    cache a default.

    Other than the size-limiting caching behavior and statistics,
    ``LRU`` acts like its parent class, the built-in Python dict. In
    addition to the overridden methods below, the following methods
    inherit the default behavior: ``__len__()``, ``pop()``,
    ``iterkeys()``, ``keys()``, ``__iter__()``.

    """
    def __init__(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        if max_size <= 0:
            raise ValueError('expected max_size > 0, not %r' % max_size)
        self.hit_count = self.miss_count = self.soft_miss_count = 0
        self.max_size = max_size
        root = []
        root[:] = [root, root, None, None]
        self.link_map = {}
        self.root = root
        self.lock = RLock()

        if on_miss is not None and not callable(on_miss):
            raise TypeError('expected on_miss to be a callable'
                            ' (or None), not %r' % on_miss)
        self.on_miss = on_miss

        if values:
            self.update(values)

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
        return ('%s(max_size=%r, on_miss=%r, values=%r)'
                % (cn, self.on_miss, self.max_size, val_map))

    def __missing__(self, key):
        if not self.on_miss:
            raise KeyError(key)
        ret = self.on_miss(key)
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
                return super(LRU, self).__getitem__(key)
            except KeyError:
                if self.on_miss:
                    return self.__missing__(key)
                raise
    else:
        del defaultdict


class LRI(dict):
    """\
    The LRI implements the basic Least Recently Inserted strategy to
    caching. One could also think of this as a SizeLimitedDefaultDict.

    ``on_miss`` is a callable that accepts the missing key (as opposed
    to collections.defaultdict's ``default_factory``, which accepts no
    arguments.) Also note that the LRI is not yet instrumented with
    statistics tracking (as the ``LRU`` is).

    """
    def __init__(self, max_size=DEFAULT_MAX_SIZE, values=None,
                 on_miss=None):
        super(LRI, self).__init__()
        self.max_size = max_size
        self.on_miss = on_miss
        self._queue = deque()

        if values:
            self.update(values)

    def __missing__(self, key):
        if not self.on_miss:
            raise KeyError(key)
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
                return super(LRI, self).__getitem__(key)
            except KeyError:
                return self.__missing__(key)
    else:
        del defaultdict


if __name__ == '__main__':
    def _test_lri():
        import string
        bc = LRI(10, on_miss=lambda k: k.upper())
        for char in string.letters:
            x = bc[char]
            assert x == char.upper()
        assert len(bc) == 10

    def _test_lru():
        lru = LRU(max_size=1)
        lru['hi'] = 0
        lru['bye'] = 1
        lru['bye']
        lru.get('hi')
        print lru
        del lru['bye']

        import pdb;pdb.set_trace()

    _test_lri()
    _test_lru()
