# -*- coding: utf-8 -*-
"""Python's builtin :class:`list` is a very fast and efficient
sequence type, but it could be better for certain access patterns,
such as non-sequential insertion into a large lists. ``listutils``
provides a pure-Python solution to this problem.

For utilities for working with iterables and lists, check out
:mod:`iterutils`. For the a :class:`list`-based version of
:class:`collections.namedtuple`, check out :mod:`namedutils`.
"""

from __future__ import print_function, division

import operator
from math import log as math_log
from itertools import chain, islice

try:
    from typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()

try:
    xrange
except NameError:
    # Python 3 compat
    xrange = range

# TODO: expose splaylist?
__all__ = ['BList', 'BarrelList']


# TODO: keep track of list lengths and bisect to the right list for
# faster getitem (and slightly slower setitem and delitem ops)

class BarrelList(list):
    """The ``BarrelList`` is a :class:`list` subtype backed by many
    dynamically-scaled sublists, to provide better scaling and random
    insertion/deletion characteristics. It is a subtype of the builtin
    :class:`list` and has an identical API, supporting indexing,
    slicing, sorting, etc. If application requirements call for
    something more performant, consider the `blist module available on
    PyPI`_.

    The name comes by way of Kurt Rose, who said it reminded him of
    barrel shifters. Not sure how, but it's BList-like, so the name
    stuck. BList is of course a reference to `B-trees`_.

    Args:
        iterable: An optional iterable of initial values for the list.

    >>> blist = BList(xrange(100000))
    >>> blist.pop(50000)
    50000
    >>> len(blist)
    99999
    >>> len(blist.lists)  # how many underlying lists
    8
    >>> slice_idx = blist.lists[0][-1]
    >>> blist[slice_idx:slice_idx + 2]
    BarrelList([11637, 11638])

    Slicing is supported and works just fine across list borders,
    returning another instance of the BarrelList.

    .. _blist module available on PyPI: https://pypi.python.org/pypi/blist
    .. _B-trees: https://en.wikipedia.org/wiki/B-tree

    """

    _size_factor = 1520
    "This size factor is the result of tuning using the tune() function below."

    def __init__(self, iterable=None):
        self.lists = [[]]
        if iterable:
            self.extend(iterable)

    @property
    def _cur_size_limit(self):
        len_self, size_factor = len(self), self._size_factor
        return int(round(size_factor * math_log(len_self + 2, 2)))

    def _translate_index(self, index):
        if index < 0:
            index += len(self)
        rel_idx, lists = index, self.lists
        for list_idx in range(len(lists)):
            len_list = len(lists[list_idx])
            if rel_idx < len_list:
                break
            rel_idx -= len_list
        if rel_idx < 0:
            return None, None
        return list_idx, rel_idx

    def _balance_list(self, list_idx):
        if list_idx < 0:
            list_idx += len(self.lists)
        cur_list, len_self = self.lists[list_idx], len(self)
        size_limit = self._cur_size_limit
        if len(cur_list) > size_limit:
            half_limit = size_limit // 2
            while len(cur_list) > half_limit:
                next_list_idx = list_idx + 1
                self.lists.insert(next_list_idx, cur_list[-half_limit:])
                del cur_list[-half_limit:]
            return True
        return False

    def insert(self, index, item):
        if len(self.lists) == 1:
            self.lists[0].insert(index, item)
            self._balance_list(0)
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            self.lists[list_idx].insert(rel_idx, item)
            self._balance_list(list_idx)
        return

    def append(self, item):
        self.lists[-1].append(item)

    def extend(self, iterable):
        self.lists[-1].extend(iterable)

    def pop(self, *a):
        lists = self.lists
        if len(lists) == 1 and not a:
            return self.lists[0].pop()
        index = a and a[0]
        if index == () or index is None or index == -1:
            ret = lists[-1].pop()
            if len(lists) > 1 and not lists[-1]:
                lists.pop()
        else:
            list_idx, rel_idx = self._translate_index(index)
            if list_idx is None:
                raise IndexError()
            ret = lists[list_idx].pop(rel_idx)
            self._balance_list(list_idx)
        return ret

    def iter_slice(self, start, stop, step=None):
        iterable = self  # TODO: optimization opportunities abound
        # start_list_idx, stop_list_idx = 0, len(self.lists)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is not None and step < 0:
            step = -step
            start, stop = -start, -stop - 1
            iterable = reversed(self)
        if start < 0:
            start += len(self)
            # start_list_idx, start_rel_idx = self._translate_index(start)
        if stop < 0:
            stop += len(self)
            # stop_list_idx, stop_rel_idx = self._translate_index(stop)
        return islice(iterable, start, stop, step)

    def del_slice(self, start, stop, step=None):
        if step is not None and abs(step) > 1:  # punt
            new_list = chain(self.iter_slice(0, start, step),
                             self.iter_slice(stop, None, step))
            self.lists[0][:] = new_list
            self._balance_list(0)
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        start_list_idx, start_rel_idx = self._translate_index(start)
        stop_list_idx, stop_rel_idx = self._translate_index(stop)
        if start_list_idx is None:
            raise IndexError()
        if stop_list_idx is None:
            raise IndexError()

        if start_list_idx == stop_list_idx:
            del self.lists[start_list_idx][start_rel_idx:stop_rel_idx]
        elif start_list_idx < stop_list_idx:
            del self.lists[start_list_idx + 1:stop_list_idx]
            del self.lists[start_list_idx][start_rel_idx:]
            del self.lists[stop_list_idx][:stop_rel_idx]
        else:
            assert False, ('start list index should never translate to'
                           ' greater than stop list index')

    __delslice__ = del_slice

    @classmethod
    def from_iterable(cls, it):
        return cls(it)

    def __iter__(self):
        return chain(*self.lists)

    def __reversed__(self):
        return chain.from_iterable(reversed(l) for l in reversed(self.lists))

    def __len__(self):
        return sum([len(l) for l in self.lists])

    def __contains__(self, item):
        for cur in self.lists:
            if item in cur:
                return True
        return False

    def __getitem__(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            iter_slice = self.iter_slice(start, stop, step)
            ret = self.from_iterable(iter_slice)
            return ret
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def __delitem__(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            self.del_slice(start, stop, step)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        del self.lists[list_idx][rel_idx]

    def __setitem__(self, index, item):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            index = operator.index(index)
        else:
            if len(self.lists) == 1:
                self.lists[0][index] = item
            else:
                tmp = list(self)
                tmp[index] = item
                self.lists[:] = [tmp]
            self._balance_list(0)
            return
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        self.lists[list_idx][rel_idx] = item

    def __getslice__(self, start, stop):
        iter_slice = self.iter_slice(start, stop, 1)
        return self.from_iterable(iter_slice)

    def __setslice__(self, start, stop, sequence):
        if len(self.lists) == 1:
            self.lists[0][start:stop] = sequence
        else:
            tmp = list(self)
            tmp[start:stop] = sequence
            self.lists[:] = [tmp]
        self._balance_list(0)
        return

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def sort(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists' average length is greater than 512.
        if len(self.lists) == 1:
            self.lists[0].sort()
        else:
            for li in self.lists:
                li.sort()
            tmp_sorted = sorted(chain.from_iterable(self.lists))
            del self.lists[:]
            self.lists[0] = tmp_sorted
            self._balance_list(0)

    def reverse(self):
        for cur in self.lists:
            cur.reverse()
        self.lists.reverse()

    def count(self, item):
        return sum([cur.count(item) for cur in self.lists])

    def index(self, item):
        len_accum = 0
        for cur in self.lists:
            try:
                rel_idx = cur.index(item)
                return len_accum + rel_idx
            except ValueError:
                len_accum += len(cur)
        raise ValueError('%r is not in list' % (item,))


BList = BarrelList


class SplayList(list):
    """Like a `splay tree`_, the SplayList facilitates moving higher
    utility items closer to the front of the list for faster access.

    .. _splay tree: https://en.wikipedia.org/wiki/Splay_tree
    """

    def shift(self, item_index, dest_index=0):
        if item_index == dest_index:
            return
        item = self.pop(item_index)
        self.insert(dest_index, item)

    def swap(self, item_index, dest_index):
        self[dest_index], self[item_index] = self[item_index], self[dest_index]


# Tests and tuning
if __name__ == '__main__':
    def test_splay():
        splay = SplayList(xrange(10))
        splay.swap(0, 9)
        assert splay[0] == 9
        assert splay[-1] == 0

        splay.shift(-2)
        assert splay[0] == 8
        assert splay[-1] == 0
        assert len(splay) == 10

    def main():
        import os

        bl = BarrelList()
        bl.insert(0, 0)
        bl.insert(1, 1)
        bl.insert(0, -1)
        bl.extend(range(100000))
        bl._balance_list(0)
        bl.pop(50000)

        rands = [ord(i) * x for i, x in zip(os.urandom(1024), range(1024))]
        bl2 = BarrelList(rands)
        bl2.sort()
        print(bl2[:10])
        print(bl2[:-10:-1])

        bl3 = BarrelList(range(int(1e5)))
        for i in range(10000):
            bl3.insert(0, bl3.pop(len(bl3) // 2))

        del bl3[10:5000]
        bl3[:20:2] = range(0, -10, -1)
        import pdb;pdb.set_trace()

    _TUNE_SETUP = """\

    from listutils import BarrelList
    bl = BarrelList()
    bl._size_factor = %s
    bl.extend(range(int(%s)))
    """

    def tune():
        from collections import defaultdict
        import gc
        from timeit import timeit
        data_size = 1e5
        old_size_factor = size_factor = 512
        all_times = defaultdict(list)
        min_times = {}
        step = 512
        while abs(step) > 4:
            gc.collect()
            for x in range(3):
                tottime = timeit('bl.insert(0, bl.pop(len(bl)//2))',
                                 _TUNE_SETUP % (size_factor, data_size),
                                 number=10000)
                all_times[size_factor].append(tottime)
            min_time = round(min(all_times[size_factor]), 3)
            min_times[size_factor] = min_time
            print(size_factor, min_time, step)
            if min_time > (min_times[old_size_factor] + 0.002):
                step = -step // 2
            old_size_factor = size_factor
            size_factor += step
        print(tottime)

    try:
        tune()  # main()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
