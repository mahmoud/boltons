# -*- coding: utf-8 -*-

from bisect import bisect_left
from itertools import chain, islice
from collections import MutableSet
import operator
import math

try:
    from compat import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


# TODO: del, sort, index
# TODO: sorted version
# TODO: inherit from list


class BarrelList(object):
    def __init__(self, iterable=None):
        self.lists = [[]]
        if iterable:
            self.extend(iterable)

    @property
    def _cur_size_limit(self):
        len_self = len(self)
        try:
            return max(512, int(round(len_self / math.log(len_self, 2)) / 2))
        except:
            return 512

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
            half_limit = size_limit / 2
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

    def count(self, item):
        return sum([cur.count(item) for cur in self.lists])

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
            return self.from_iterable(iter_slice)
        list_idx, rel_idx = self._translate_index(index)
        if list_idx is None:
            raise IndexError()
        return self.lists[list_idx][rel_idx]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def sort(self):
        # poor pythonist's mergesort, it's faster than sorted(self)
        # when the lists average larger than 512 items
        if len(self.lists) == 1:
            self.lists[0] = sorted(self.lists[0])
        else:
            self.lists[0] = sorted(chain(*[sorted(l) for l in self.lists]))
            self._balance_list(0)


# Tests

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
    bl = BarrelList(rands)
    bl.sort()
    print bl[:-10:-1]
    import pdb;pdb.set_trace()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
