from bisect import bisect_left, insort
from itertools import ifilter


class IndexedSet(object):
    """
    IndexedSet maintains insertion order and uniqueness of inserted
    elements. It's a hybrid type, mostly like an OrderedSet, but also
    list-like, in that it supports indexing and slicing.


    >>> IndexedSet(range(4) + range(6))
    [0, 1, 2, 3, 4, 5]
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

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r)' % (cn, list(self))

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
        self.item_index_map[item] = len(self.item_list)
        self.item_list.append(item)

    def update(self, other):  # O(n)
        for item in other:
            self.add(item)

    #TODO: a bunch of set operators
    #general scheme: add all of the "others" items to the right

    #list operations
    def __getitem__(self, key):
        if key < 0:
            key += len(self)
        phy_key = bisect_left(self.dead_indices, key)
        try:
            return self.item_list[phy_key]
        except IndexError:
            raise #TODO: message

    def pop(self, index=None):  # O(1) + (amortized O(n) cull)
        if index is None or index == -1 or index == len(self):
            ret = self.item_list.pop()
            del self.item_index_map[ret]
        else:
            if index < 0:
                index += len(self)  # TODO: not len(self) (extra fxn call)?
            phy_index = index + bisect_left(self.dead_indices, index)
            insort(self.dead_indices, phy_index)
            del self.items[self.item_list[phy_index]]
            self.item_list[phy_index] = _MISSING
        self._cull()
        return ret



_MISSING = object()
