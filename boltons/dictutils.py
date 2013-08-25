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
        self._maphistory = {}

    def __delitem__(self, key):
        PREV, NEXT = 0, 1
        history = self._maphistory.pop(key, _MISSING)
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
        if not self._maphistory.get(key):
            prev_cell = self._OrderedDict__map.get(key)
            self._maphistory[key] = [prev_cell]
        last[NEXT] = root[PREV] = self._OrderedDict__map[key] = cell
        self._maphistory[key].append(cell)
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
        prev_mapping = self._maphistory.get(key)
        if prev_mapping[-1][PREV] is root:
            return self.pop(key)

        link_prev, link_next, key = self._OrderedDict__map.pop(key)
        link_prev[NEXT] = link_next
        link_next[PREV] = link_prev
        self._OrderedDict__map[key] = prev_mapping.pop()
        return self.getlist(key).pop()


MultiDict = OrderedMultiDict


# Tests follow

OMD = OrderedMultiDict

_ITEMSETS = [[],
             [('a', 1), ('b', 2), ('c', 3)],
             [('A', 'One'), ('A', 'One'), ('A', 'One')],
             [('Z', -1), ('Y', -2), ('Y', -2)]]


def test_dict_init():
    x = dict(_ITEMSETS[1])
    y = OMD(x)

    assert x['a'] == 1
    assert x['b'] == 2
    assert x['c'] == 3

    assert len(x) == 3
    assert x.get_list('a') == ['a']
    assert x == y


def test_to_dict():
    omd = OMD(_ITEMSETS[2])
    assert len(omd) == 1
    assert d['A'] == 'One'

    d = dict(omd)
    assert len(d) == 1
    assert d['A'] == 'One'


def test_eq():
    omd = OMD(_ITEMSETS[3])
    assert omd == omd
    assert not (omd != omd)

    omd2 = OMD(_ITEMSETS[3])
    assert omd == omd2
    assert omd2 == omd
    assert not (omd != omd2)

    d = dict(_ITEMSETS[3])
    assert d == omd
    omd3 = OMD(d)
    assert omd != omd3


def test_copy():
    for itemset in _ITEMSETS:
        omd = OMD(itemset)
        omd_c = omd.copy()
        assert omd == omd_c
        if omd_c:
            omd_c.pop(itemset[0][0])
            assert omd != omd_c
    return


def test_update():
    omd = OMD(_ITEMSETS[1])
    omd2 = OMD({'a': 10})
    omd.update(omd2)
    assert omd['a'] == 10
    assert omd.getlist('a') == [10]

    omd2_c.pop('a')
    assert omd2 != omd2_c
