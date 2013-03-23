# -*- coding: utf-8 -*-

from collections import OrderedDict

try:
    from compat import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


__all__ = ['MultiDict', 'OrderedMultiDict']


class OrderedMultiDict(OrderedDict):
    """\
    A MultiDict that remembers original insertion order. A MultiDict
    is a dictionary that can have multiple values per key, most
    commonly useful for handling parsed query strings and inverting
    dictionaries to create a reverse index.

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.popitem('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    The implementation could be more optimal, but overall it's far
    better than other OMDs out there. Mad thanks to Mark Williams for
    getting it this far.
    """

    def __init__(self, *args, **kwargs):
        super(OrderedMultiDict, self).__init__(*args, **kwargs)
        self.__maphistory = {}

    def __delitem__(self, key):
        PREV, NEXT = 0, 1
        history = self.__maphistory.pop(key, _MISSING)
        super(OrderedMultiDict, self).__delitem__(key)
        if history is _MISSING:
            return
        for h in history:
            link_prev, link_next, key = h
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev

    def __getitem__(self, key):
        if not key in self:
            raise KeyError(key)
        return super(OrderedMultiDict, self).__getitem__(key)[0]

    def __setitem__(self, key, value):
        super(OrderedMultiDict, self).__setitem__(key, [value])

    def add(self, key, value):
        PREV, NEXT = 0, 1
        root = self._OrderedDict__root
        last = root[PREV]
        cell = [last, root, key]
        if not self.__maphistory.get(key):
            prev_cell = self._OrderedDict__map.get(key)
            self.__maphistory[key] = [prev_cell]
        last[NEXT] = root[PREV] = self._OrderedDict__map[key] = cell
        self.__maphistory[key].append(cell)
        super(OrderedDict, self).setdefault(key, []).append(value)

    def getlist(self, key):
        return super(OrderedMultiDict, self).__getitem__(key)

    def iteritems(self):
        walkers = {}
        for key in self:
            iterator = walkers.setdefault(key, iter(self.getlist(key)))
            yield (key, next(iterator))

    def items(self):
        return list(self.iteritems())

    def popitem(self, key, default=_MISSING):
        # we want __delitem__'s list manipulation without actually
        # deleting the item...
        PREV, NEXT = 0, 1
        root = self._OrderedDict__root
        if not key in self:
            if default is _MISSING:
                raise KeyError(key)
            else:
                return default
        previous_mapping = self.__maphistory.get(key)
        if previous_mapping[-1][PREV] is root:
            return self.pop(key)

        link_prev, link_next, key = self._OrderedDict__map.pop(key)
        link_prev[NEXT] = link_next
        link_next[PREV] = link_prev
        self._OrderedDict__map[key] = previous_mapping.pop()
        return self.getlist(key).pop()


MultiDict = OrderedMultiDict
