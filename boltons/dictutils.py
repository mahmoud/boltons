# -*- coding: utf-8 -*-

from collections import KeysView, ValuesView, ItemsView
from itertools import izip

try:
    from compat import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY = 0, 1, 2


__all__ = ['MultiDict', 'OrderedMultiDict']

try:
    profile
except NameError:
    profile = lambda x: x


class OrderedMultiDict(dict):
    """\
    A MultiDict that remembers original insertion order. A MultiDict
    is a dictionary that can have multiple values per key, most
    commonly useful for handling parsed query strings and inverting
    dictionaries to create a reverse index.

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd['a']
    3

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the last value added. ``omd['a']`` refers to ``3``, not ``1``.

    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.poplast('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    Note that dict()-ifying the OMD results in a dict of keys to
    _lists_ of values:

    >>> dict(OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]))
    {'a': [1, 3], 'b': [2]}

    If you want a flat dictionary, use ``get_flattened()``.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).get_flattened()
    {'a': 3, 'b': 2}

    The implementation could be more optimal, but overall it's far
    better than other OMDs out there. Mad props to Mark Williams for
    all his help.
    """
    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (name, len(args)))
        super(OrderedMultiDict, self).__init__()

        self._clear_ll()
        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)

    def _clear_ll(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            self._map = {}
            self.root = []
        self._map.clear()
        self.root[:] = [self.root, self.root, None]

    @profile
    def _insert(self, k):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    @profile
    def add(self, k, v, multi=False):
        self_insert = self._insert
        if multi:
            for v in vs:
                self_insert(k)
            super(OrderedMultiDict, self).setdefault(k, []).extend(v)
        else:
            self_insert(k)
            super(OrderedMultiDict, self).setdefault(k, []).append(v)

    def getlist(self, k):
        return super(OrderedMultiDict, self).__getitem__(k)[:]

    def popnth(self, k, idx):  # pop_single?
        self._remove(k, idx)
        values = super(OrderedMultiDict, self).__getitem__(k)
        v = values.pop(idx)
        if not values:
            super(OrderedMultiDict, self).__delitem__(k)
        return v

    def poplast(self, k):  # could default pop_single to -1
        return self.popnth(k, idx=-1)

    def clear(self):
        super(OrderedMultiDict, self).clear()
        self._clear_ll()

    def get(self, k, default=[None], multi=False):
        ret = super(OrderedMultiDict, self).get(k, default)
        return ret[:] if multi else ret[-1]

    def setdefault(self, k, default=_MISSING):
        if not super(OrderedMultiDict, self).__contains__(k):
            self[k] = [] if default is _MISSING else [default]
        return default

    def copy(self):
        return self.__class__(self.items(multi=True))

    def get_flattened(self, ordered=False):
        return dict([(k, self[k]) for k in self])

    @classmethod
    def fromkeys(cls, keys, default=None):
        return cls([(k, default) for k in keys])

    def update(self, E, **F):
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif hasattr(E, 'keys'):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen_add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def update_extend(self, E, **F):  # upsert?
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def __setitem__(self, k, v):
        if super(OrderedMultiDict, self).__contains__(k):
            self._remove_all(k)
        self._insert(k)
        super(OrderedMultiDict, self).__setitem__(k, [v])

    def __getitem__(self, k):
        return super(OrderedMultiDict, self).__getitem__(k)[-1]

    def __delitem__(self, k):
        super(OrderedMultiDict, self).__delitem__(k)
        self._remove_all(k)

    def __eq__(self, other):
        if self is other:
            return True
        elif len(other) != len(self):
            return False
        elif isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            for (selfk, selfv), (otherk, otherv) in izip(selfi, otheri):
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def popall(self, k, default=_MISSING):
        if super(OrderedMultiDict, self).__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super(OrderedMultiDict, self).pop(k)
        return super(OrderedMultiDict, self).pop(k, default)

    def pop(self, k, default=_MISSING):
        return self.popall(k, default)[-1]

    def _remove(self, k, idx):
        values = self._map[k]
        cell = values.pop(idx)
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not len(values):
            del self._map[k]

    def _remove_all(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def iteritems(self, multi=False):
        if multi:
            indices = {}
            for k in self.iterkeys(multi=True):
                idx = indices.setdefault(k, 0)
                yield k, self.getlist(k)[idx]
                indices[k] += 1
        else:
            for k in self:
                yield k, self[k]

    def items(self, multi=False):
        return list(self.iteritems(multi))

    def iterkeys(self, multi=False):
        if multi:
            curr = self.root[NEXT]
            while curr is not self.root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            for k in self.iterkeys(multi=True):
                if k not in yielded:
                    yielded.add(k)
                    yield k

    def itervalues(self, multi=False):
        for k in self.iterkeys(multi):
            yield self[k]

    def keys(self, multi=False):
        return list(self.iterkey(multi))

    def values(self, multi=False):
        return list(self.itervalues(multi))

    def __iter__(self):
        return iter(self.iterkeys())

    def __reversed__(self):
        curr = self.root[PREV]
        while curr is not self.root:
            yield curr[KEY]
            curr = curr[PREV]

    def __repr__(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return '%s([%s])' % (cn, kvs)

    def viewkeys(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(self)

    def viewvalues(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(self)

    def viewitems(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(self)


MultiDict = OrderedMultiDict


# Tests follow

OMD = OrderedMultiDict

_ITEMSETS = [[],
             [('a', 1), ('b', 2), ('c', 3)],
             [('A', 'One'), ('A', 'One'), ('A', 'One')],
             [('Z', -1), ('Y', -2), ('Y', -2)]]


def test_dict_init():
    d = dict(_ITEMSETS[1])
    omd = OMD(d)

    assert omd['a'] == 1
    assert omd['b'] == 2
    assert omd['c'] == 3

    assert len(omd) == 3
    assert omd.getlist('a') == [1]
    assert omd == d


def test_to_dict():
    omd = OMD(_ITEMSETS[2])
    assert len(omd) == 1
    assert omd['A'] == 'One'

    d = dict(omd)
    assert len(d) == 1
    assert d['A'] == ['One', 'One', 'One']

    flat = omd.get_flattened()
    assert flat['A'] == 'One'


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

    omd2_c = omd2.copy()
    omd2_c.pop('a')
    assert omd2 != omd2_c


def test_clear():
    for itemset in _ITEMSETS:
        omd = OMD(itemset)
        omd.clear()
        assert len(omd) == 0
        assert not omd
        omd.clear()
        assert not omd
        omd['a'] = 22
        assert omd
        omd.clear()
        assert not omd


def test_types():
    import collections
    omd = OMD()
    assert isinstance(omd, dict)
    assert isinstance(omd, collections.MutableMapping)


def test_flattened():
    for itemset in _ITEMSETS:
        omd = OMD(itemset)
        d = dict(itemset)

        flat = omd.get_flattened()
        assert flat == d
