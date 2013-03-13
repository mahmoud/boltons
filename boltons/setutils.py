# -*- coding: utf-8 -*-

from bisect import insort, bisect
from itertools import chain, islice
from collections import MutableSet

_MISSING = object()
_COMPACTION_FACTOR = 10

# TODO: better exception messages
# TODO: inherit from set()
# TODO: raise exception on non-set params?
# TODO: technically reverse operators should probably reverse the
# order of the 'other' inputs and put self last (to try and maintain
# insertion order)


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
        dead_indices = self.dead_indices
        if not dead_indices:
            return
        items, index_map = self.item_list, self.item_index_map
        for i, item in enumerate(self):
            items[i] = item
            index_map[item] = i
        del items[-len(dead_indices):]
        del dead_indices[:]

    def _cull(self):
        ded = self.dead_indices
        if not ded:
            return
        items = self.item_list
        if not self.item_index_map:
            del self.dead_indices[:]
            del self.item_list[:]
        elif len(ded) > 8 and len(ded) > len(items) / _COMPACTION_FACTOR:
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
        return (item for item in self.item_list if item is not _MISSING)

    def __reversed__(self):
        item_list = self.item_list
        return (item for item in reversed(item_list) if item is not _MISSING)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, IndexedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    @classmethod
    def from_iterable(cls, it):
        return cls(it)

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

    def clear(self):
        del self.item_list[:]
        del self.dead_indices[:]
        self.item_index_map.clear()

    def add(self, item):
        if item not in self.item_index_map:
            self.item_index_map[item] = len(self.item_list)
            self.item_list.append(item)

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
        return self.from_iterable(chain(self, *others))

    def iter_intersection(self, *others):
        for k in self:
            for other in others:
                if k not in other:
                    break
            else:
                yield k
        return

    def intersection(self, *others):
        #if len(others) == 1:  # TODO: uncomment for optimization after testing
        #    other = others[0]
        #    return self.from_iterable(k for k in self if k not in other)
        return self.from_iterable(self.iter_intersection(*others))

    def iter_difference(self, *others):
        for k in self:
            for other in others:
                if k in other:
                    break
            else:
                yield k
        return

    def difference(self, *others):
        return self.from_iterable(self.iter_difference(*others))

    def symmetric_difference(self, *others):
        ret = self.union(*others)
        return ret.difference(self.intersection(*others))

    __or__  = __ror__  = union
    __and__ = __rand__ = intersection
    __sub__ = __rsub__ = difference
    __xor__ = __rxor__ = symmetric_difference

    # in-place set operations
    def update(self, *others):
        if not others:
            return  # raise?
        elif len(others) == 1:
            other = others[0]
        else:
            other = chain(others)
        for o in other:
            self.add(o)

    def intersection_update(self, *others):
        for val in self.difference(*others):
            self.discard(val)

    def difference_update(self, *others):
        if self in others:
            self.clear()
        for val in self.intersection(*others):
            self.discard(val)

    def symmetric_difference_update(self, other):  # note singular 'other'
        if self is other:
            self.clear()
        for val in other:
            if val in self:
                self.discard(val)
            else:
                self.add(val)

    def __ior__(self, *others):
        self.update(*others)
        return self

    def __iand__(self, *others):
        self.intersection_update(*others)
        return self

    def __isub__(self, *others):
        self.difference_update(*others)
        return self

    def __ixor__(self, *others):
        self.symmetric_difference_update(*others)
        return self

    def iter_slice(self, start, stop, step=None):
        iterable = self
        if start is not None:
            start = start + bisect(self.dead_indices, start)
        if stop is not None:
            stop = stop + bisect(self.dead_indices, stop)
        if step is not None and step < 0:
            step = -step
            iterable = reversed(self)
        return islice(iterable, start, stop, step)

    #list operations
    def __getitem__(self, index):
        try:
            start, stop, step = index.start, index.stop, index.step
        except AttributeError:
            pass
        else:
            iter_slice = self.iter_slice(start, stop, step)
            return self.from_iterable(iter_slice)
        if index < 0:
            index += len(self)
        skip = bisect(self.dead_indices, index)
        real_index = index + skip
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
            skip = bisect(self.dead_indices, index)
            insort(self.dead_indices, index)
            real_index = index + skip
            ret = self.item_list[real_index]
            self.item_list[real_index] = _MISSING
            del item_index_map[ret]
        self._cull()
        return ret

    def count(self, x):
        if x in self.item_index_map:
            return 1
        return 0

    def reverse(self):
        reversed_list = list(reversed(self))
        self.item_list[:] = reversed_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

    def sort(self):
        sorted_list = sorted(self)
        if sorted_list == self.item_list:
            return
        self.item_list[:] = sorted_list
        for i, item in enumerate(self.item_list):
            self.item_index_map[item] = i
        del self.dead_indices[:]

if __name__ == '__main__':
    zero2nine = IndexedSet(range(10))
    five2nine = zero2nine & IndexedSet(range(5, 15))
    x = IndexedSet(five2nine)
    x |= set([10])
    print zero2nine, five2nine, x, x[-1]
    print zero2nine ^ five2nine
    print x[:3], x[2:4:-1]

    try:
        hundo = IndexedSet(xrange(1000))
        print hundo.pop(), hundo.pop()
        print hundo.pop(499), hundo.pop(499),
        print [hundo[i] for i in range(500, 505)]
        print 'hundo has', len(hundo), 'items'
        while len(hundo) > 600:
            dead_idx_count = len(hundo.dead_indices)
            hundo.pop(0)
            new_dead_idx_count = len(hundo.dead_indices)
            if new_dead_idx_count < dead_idx_count:
                print 'culled', dead_idx_count - new_dead_idx_count, 'indexes'
        print 'hundo has', len(hundo), 'items'
        print 'hundo has', new_dead_idx_count, 'dead indices'
        print 'exposing _MISSING:', any([hundo[i] is _MISSING for i in range(len(hundo))])
        #hundo &= IndexedSet(range(500, 503))
        #print hundo
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
    import pdb;pdb.set_trace()
