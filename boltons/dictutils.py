# -*- coding: utf-8 -*-

from collections import KeysView, ValuesView, ItemsView
from itertools import izip

try:
    from compat import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


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

    If you want a flat dictionary, use ``todict()``.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).todict()
    {'a': 3, 'b': 2}

    With ``multi=False``, items appear with the keys according to
    original/earliest insertion order, but with the most recently
    inserted value.
    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

    Mad props to Mark Williams for all his help.

    """
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super(OrderedMultiDict, self).__init__()

        self._clear_ll()
        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)

    def _clear_ll(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def _insert(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def add(self, k, v, multi=False):
        self_insert = self._insert
        values = super(OrderedMultiDict, self).setdefault(k, [])
        if multi:
            for subv in v:
                self_insert(k, subv)
            values.extend(v)
        else:
            self_insert(k, v)
            values.append(v)

    def getlist(self, k):
        return super(OrderedMultiDict, self).__getitem__(k)[:]

    def clear(self):
        super(OrderedMultiDict, self).clear()
        self._clear_ll()

    def get(self, k, default=None, multi=False):
        ret = super(OrderedMultiDict, self).get(k, [default])
        return ret[:] if multi else ret[-1]

    def setdefault(self, k, default=_MISSING):
        if not super(OrderedMultiDict, self).__contains__(k):
            self[k] = [] if default is _MISSING else [default]
        return default

    def copy(self):
        return self.__class__(self.items(multi=True))

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
            seen_add = seen.add
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
        self._insert(k, v)
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

    def pop(self, k, default=_MISSING):
        return self.popall(k, default)[-1]

    def popall(self, k, default=_MISSING):
        if super(OrderedMultiDict, self).__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super(OrderedMultiDict, self).pop(k)
        return super(OrderedMultiDict, self).pop(k, default)

    def poplast(self, k=_MISSING, default=_MISSING):
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                raise KeyError('empty %r' % type(self))
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super(OrderedMultiDict, self).__getitem__(k)
        v = values.pop()
        if not values:
            super(OrderedMultiDict, self).__delitem__(k)
        return v

    def _remove(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def _remove_all(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def iteritems(self, multi=False):
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def iterkeys(self, multi=False):
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def itervalues(self, multi=False):
        for k, v in self.iteritems(multi=multi):
            yield v

    def todict(self, ordered=False):
        return dict([(k, self[k]) for k in self])

    def inverted(self):
        return self.__class__((v, k) for k, v in self.iteritems())

    def counts(self):
        """
        Returns an OMD because Counter/OrderedDict may not be
        available, and neither Counter nor dict maintain order.
        """
        super_getitem = super(OrderedMultiDict, self).__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def keys(self, multi=False):
        return list(self.iterkeys(multi=multi))

    def values(self, multi=False):
        return list(self.itervalues(multi=multi))

    def items(self, multi=False):
        return list(self.iteritems(multi=multi))

    def __iter__(self):
        return self.iterkeys()

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super(OrderedMultiDict, self).__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
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


class FastIterOrderedMultiDict(OrderedMultiDict):
    """\ An OrderedMultiDict backed by a skip list.  Iteration over keys
    is faster and uses constant memory but adding duplicate key-value
    pairs is slower.
    """
    def _clear_ll(self):
        # TODO: always reset objects? (i.e., no else block below)
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root,
                        None, None,
                        self.root, self.root]

    def _insert(self, k, v):
        root = self.root
        empty = []
        cells = self._map.setdefault(k, empty)
        last = root[PREV]

        if cells is empty:
            cell = [last, root,
                    k, v,
                    last, root]
            # was the last one skipped?
            if last[SPREV][SNEXT] is root:
                last[SPREV][SNEXT] = cell
            last[NEXT] = last[SNEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)
        else:
            # if the previous was skipped, go back to the cell that
            # skipped it
            sprev = last[SPREV] if not (last[SPREV][SNEXT] is last) else last
            cell = [last, root,
                    k, v,
                    sprev, root]
            # skip me
            last[SNEXT] = root
            last[NEXT] = root[PREV] = root[SPREV] = cell
            cells.append(cell)

    def _remove(self, k):
        cells = self._map[k]
        cell = cells.pop()
        if not cells:
            del self._map[k]
            cell[PREV][SNEXT] = cell[SNEXT]

        if cell[PREV][SPREV][SNEXT] is cell:
            cell[PREV][SPREV][SNEXT] = cell[NEXT]
        elif cell[SNEXT] is cell[NEXT]:
            cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]

    def _remove_all(self, k):
        cells = self._map.pop(k)
        while cells:
            cell = cells.pop()
            if cell[PREV][SPREV][SNEXT] is cell:
                cell[PREV][SPREV][SNEXT] = cell[NEXT]
            elif cell[SNEXT] is cell[NEXT]:
                cell[SPREV][SNEXT], cell[SNEXT][SPREV] = cell[SNEXT], cell[SPREV]

            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        cell[PREV][SNEXT] = cell[SNEXT]

    def iteritems(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY], curr[VALUE]
            curr = curr[next_link]

    def iterkeys(self, multi=False):
        next_link = NEXT if multi else SNEXT
        root = self.root
        curr = root[next_link]
        while curr is not root:
            yield curr[KEY]
            curr = curr[next_link]

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        while curr is not root:
            if curr[SPREV][SNEXT] is not curr:
                curr = curr[SPREV]
                if curr is root:
                    break
            yield curr[KEY]
            curr = curr[PREV]


# Tests follow

OMD = OrderedMultiDict

_ITEMSETS = [[],
             [('a', 1), ('b', 2), ('c', 3)],
             [('A', 'One'), ('A', 'One'), ('A', 'One')],
             [('Z', -1), ('Y', -2), ('Y', -2)],
             [('a', 1), ('b', 2), ('a', 3), ('c', 4)]]


def test_dict_init():
    d = dict(_ITEMSETS[1])
    omd = OMD(d)

    assert omd['a'] == 1
    assert omd['b'] == 2
    assert omd['c'] == 3

    assert len(omd) == 3
    assert omd.getlist('a') == [1]
    assert omd == d


def test_todict():
    omd = OMD(_ITEMSETS[2])
    assert len(omd) == 1
    assert omd['A'] == 'One'

    d = dict(omd)
    assert len(d) == 1
    assert d['A'] == ['One', 'One', 'One']

    flat = omd.todict()
    assert flat['A'] == 'One'

    for itemset in _ITEMSETS:
        omd = OMD(itemset)
        d = dict(itemset)

        flat = omd.todict()
        assert flat == d


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


def test_multi_correctness():
    size = 100
    redun = 5

    _rng = range(size)
    _rng_redun = range(size/redun) * redun
    _pairs = zip(_rng_redun, _rng)

    omd = OMD(_pairs)
    for multi in (True, False):
        vals = [x[1] for x in omd.iteritems(multi=multi)]
        strictly_ascending = all([x < y for x, y in zip(vals, vals[1:])])
        assert strictly_ascending
    return


def test_kv_consistency():
    for itemset in _ITEMSETS:
        omd = OMD(itemset)

        for multi in (True, False):
            items = omd.items(multi=multi)
            keys = omd.keys(multi=multi)
            values = omd.values(multi=multi)

            assert keys == [x[0] for x in items]
            assert values == [x[1] for x in items]
    return


def test_update_basic():
    omd = OMD(_ITEMSETS[1])
    omd2 = OMD({'a': 10})
    omd.update(omd2)
    assert omd['a'] == 10
    assert omd.getlist('a') == [10]

    omd2_c = omd2.copy()
    omd2_c.pop('a')
    assert omd2 != omd2_c


def test_update():
    for first, second in zip(_ITEMSETS, _ITEMSETS[1:]):
        omd1 = OMD(first)
        omd2 = OMD(second)
        ref1 = dict(first)
        ref2 = dict(second)

        omd1.update(omd2)
        ref1.update(ref2)
        assert omd1.todict() == ref1

        omd1_repr = repr(omd1)
        omd1.update(omd1)
        assert omd1_repr == repr(omd1)


def test_update_extend():
    for first, second in zip(_ITEMSETS, _ITEMSETS[1:] + [[]]):
        omd1 = OMD(first)
        omd2 = OMD(second)
        ref = dict(first)
        orig_keys = set(omd1)

        ref.update(second)
        omd1.update_extend(omd2)
        for k in omd2:
            assert len(omd1.getlist(k)) >= len(omd2.getlist(k))

        assert omd1.todict() == ref
        assert orig_keys <= set(omd1)


def test_invert():
    for items in _ITEMSETS:
        omd = OMD(items)
        iomd = omd.inverted()
        assert len(omd) == len(iomd)
        assert len(omd.items()) == len(iomd.items())

        for val in omd.values():
            assert val in iomd


def test_poplast():
    for items in _ITEMSETS[1:]:
        omd = OMD(items)
        assert omd.poplast() == items[-1][-1]


def test_reversed():
    from collections import OrderedDict
    for items in _ITEMSETS:
        omd = OMD(items)
        od = OrderedDict(items)
        for ik, ok in zip(reversed(od), reversed(omd)):
            assert ik == ok

    r100 = range(100)
    omd = OMD(zip(r100, r100))
    for i in r100:
        omd.add(i, i)
    r100.reverse()
    assert list(reversed(omd)) == r100
