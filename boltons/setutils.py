# -*- coding: utf-8 -*-

from bisect import bisect_left, insort
from itertools import ifilter, chain
from collections import MutableSet

_MISSING = object()

# TODO: .sort(), .reverse()
# TODO: slicing
# TODO: in-place set operations
# TODO: better exception messages


class IndexedSet(MutableSet):
    """\
    IndexedSet maintains insertion order and uniqueness of inserted
    elements. It's a hybrid type, mostly like an OrderedSet, but also
    list-like, in that it supports indexing and slicing.


    >>> x = IndexedSet(range(4) + range(8))
    >>> x
    IndexedSet([0, 1, 2, 3, 4, 5, 6, 7])
    >>> x - set(range(2))
    IndexedSet([2, 3, 4, 5, 6, 7])
    >>> x[-1]
    7
    """
    def __init__(self, other=None):
        self.item_index_map = dict()
        self.item_list = []
        self.dead_indices = []
        if other:
            self.update(other)

    def _compact(self):
        ded = self.dead_indices
        if not ded:
            return
        items = self.item_list
        skip, ded_index = 1, 1
        for i in range(ded[0], len(items) - len(ded)):
            while i + skip == ded[ded_index]:
                skip += 1
                ded_index += 1
            items[i] = items[i + skip]
        del items[-len(ded):]
        self.dead_indices = []

    def _cull(self):
        ded = self.dead_indices
        if not ded:
            return
        items = self.item_list
        if not self.item_index_map:
            self.dead_indices = []
            self.item_list = []
        elif len(ded) > 8 and len(ded) > len(items) / 2:
            self._compact()
        elif ded[-1] == len(items) - 1:  # get rid of dead right hand side
            num_dead = 1
            while ded[-num_dead] == ded[-(num_dead + 1)] - 1:
                num_dead += 1
            del ded[-num_dead:]
            del items[-num_dead:]

    #common operations
    def __len__(self):
        return len(self.item_index_map)

    def __contains__(self, item):
        return item in self.item_index_map

    def __iter__(self):
        return ifilter(lambda e: e is not _MISSING, iter(self.item_list))

    def __reversed__(self):
        return ifilter(lambda e: e is not _MISSING, reversed(self.item_list))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    #set operations
    def remove(self, item):  # O(1) + (amortized O(n) cull)
        try:
            dead_index = self.item_index_map.pop(item)
            insort(self.dead_indices, dead_index)
            self.item_list[dead_index] = _MISSING
            self._cull()
        except KeyError:
            raise #TODO: good message

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def add(self, item):
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

    def update(self, other):
        for o in other:
            self.add(o)

    def isdisjoint(self, other):
        iim = self.item_index_map
        for k in other:
            if k in iim:
                return False
        return True

    def issubset(self, other):
        if len(other) < len(self):
            return False
        for k in self.item_index_map:
            if k not in other:
                return False
        return True

    def issuperset(self, other):
        if len(other) > len(self):
            return False
        iim = self.item_index_map
        for k in other:
            if k not in iim:
                return False
        return True

    def union(self, *others):
        return IndexedSet(chain(self, *others))

    def intersection(self, *others):
        if len(others) == 1:
            other = others[0]
            return IndexedSet(k for k in self if k in other)
        ret = IndexedSet()
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                ret.add(k)
        return ret

    def difference(self, *others):
        if len(others) == 1:
            other = others[0]
            return IndexedSet(k for k in self if k not in other)
        ret = IndexedSet()
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                ret.add(k)
        return ret

    def symmetric_difference(self, *others):
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    __or__  = union
    __and__ = intersection
    __sub__ = difference
    __xor__ = symmetric_difference

    #list operations
    def __getitem__(self, index):  # TODO: support slicing
        if index < 0:
            index += len(self)
        real_index = index + bisect_left(self.dead_indices, index)
        try:
            return self.item_list[real_index]
        except IndexError:
            raise #TODO: message

    def pop(self, index=None):  # O(1) + (amortized O(n) cull)
        item_index_map = self.item_index_map
        len_self = len(item_index_map)
        if index is None or index == -1 or index == len_self:
            ret = self.item_list.pop()
            del item_index_map[ret]
        else:
            if index < 0:
                index += len_self
            real_index = index + bisect_left(self.dead_indices, index)
            insort(self.dead_indices, real_index)
            del item_index_map[self.item_list[real_index]]
            self.item_list[real_index] = _MISSING
        self._cull()
        return ret

    def count(self, x):
        if x in self.item_index_map:
            return 1
        return 0
