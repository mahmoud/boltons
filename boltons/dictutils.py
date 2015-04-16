# -*- coding: utf-8 -*-
"""Python has a very powerful mapping type at its core: the :class:`dict`
type. While versatile and featureful, the :class:`dict` prioritizes
simplicity and performance. As a result, it does not retain the order
of item insertion [1]_, nor does it store multiple values per key. It
is a fast, unordered 1:1 mapping.

The :class:`OrderedMultiDict` contrasts to the built-in :class:`dict`,
as a relatively maximalist, ordered 1:n subtype of
:class:`dict`. Virtually every feature of :class:`dict` has been
retooled to be intuitive in the face of this added
complexity. Additional methods have been added, such as
:class:`collections.Counter`-like functionality.

A prime advantage of the :class:`OrderedMultiDict` (OMD) is its
non-destructive nature. Data can be added to an :class:`OMD` without being
rearranged or overwritten. The property can allow the developer to
work more freely with the data, as well as make more assumptions about
where input data will end up in the output, all without any extra
work.

One great example of this is the :meth:`OMD.inverted()` method, which
returns a new OMD with the values as keys and the keys as values. All
the data and the respective order is still represented in the inverted
form, all from an operation which would be outright wrong and reckless
with a built-in :class:`dict` or :class:`collections.OrderedDict`.

The OMD has been performance tuned to be suitable for a wide range of
usages, including as a basic unordered MultiDict. Special
thanks to `Mark Williams`_ for all his help.

.. [1] As of 2015, `basic dicts on PyPy are ordered
   <http://morepypy.blogspot.com/2015/01/faster-more-memory-efficient-and-more.html>`_.
.. _Mark Williams: https://github.com/markrwilliams
"""

from collections import KeysView, ValuesView, ItemsView

try:
    from itertools import izip
except ImportError:
    izip = zip  # Python 3

try:
    from typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


__all__ = ['MultiDict', 'OMD', 'OrderedMultiDict']

try:
    profile
except NameError:
    profile = lambda x: x


class OrderedMultiDict(dict):
    """A MultiDict is a dictionary that can have multiple values per key
    and the OrderedMultiDict (OMD) is a MultiDict that retains
    original insertion order. Common use cases include:

      * handling query strings parsed from URLs
      * inverting a dictionary to create a reverse index (values to keys)
      * stacking data from multiple dictionaries in a non-destructive way

    The OrderedMultiDict constructor is identical to the built-in
    :class:`dict`, and overall the API is constitutes an intuitive
    superset of the built-in type:

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd.get('a')
    3
    >>> omd.getlist('a')
    [1, 3]

    Some non-:class:`dict`-like behaviors also make an appearance,
    such as support for :func:`reversed`:

    >>> list(reversed(omd))
    ['b', 'a']

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the most recent value added. ``omd['a']`` refers to ``3``, not
    ``1``.

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

    Note that calling :func:`dict` on an OMD results in a dict of keys
    to *lists* of values:

    >>> from pprint import pprint as pp  # ensuring proper key ordering
    >>> omd = OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> pp(dict(omd))
    {'a': [1, 3], 'b': [2]}

    Note that modifying those lists will modify the OMD. If you want a
    safe-to-modify or flat dictionary, use :meth:`OrderedMultiDict.todict()`.

    >>> pp(omd.todict())
    {'a': 3, 'b': 2}
    >>> pp(omd.todict(multi=True))
    {'a': [1, 3], 'b': [2]}

    With ``multi=False``, items appear with the keys in to original
    insertion order, alongside the most-recently inserted value for
    that key.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

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

    def add(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        self_insert = self._insert
        values = super(OrderedMultiDict, self).setdefault(k, [])
        self_insert(k, v)
        values.append(v)

    def addlist(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        self_insert = self._insert
        values = super(OrderedMultiDict, self).setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
            values.extend(v)

    def get(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super(OrderedMultiDict, self).get(k, [default])[-1]

    def getlist(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super(OrderedMultiDict, self).__getitem__(k)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def clear(self):
        "Empty the dictionary."
        super(OrderedMultiDict, self).clear()
        self._clear_ll()

    def setdefault(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super(OrderedMultiDict, self).__contains__(k):
            self[k] = [] if default is _MISSING else [default]
        return default

    def copy(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    @classmethod
    def fromkeys(cls, keys, default=None):
        """Create a dictionary from a list of keys, with all the values
        set to *default*, or ``None`` if *default* is not set.
        """
        return cls([(k, default) for k in keys])

    def update(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
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

    def update_extend(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
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
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        return self.popall(k, default)[-1]

    def popall(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        if super(OrderedMultiDict, self).__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super(OrderedMultiDict, self).pop(k)
        return super(OrderedMultiDict, self).pop(k, default)

    def poplast(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
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
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
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
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
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
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def todict(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return dict([(k, self.getlist(k)) for k in self])
        return dict([(k, self[k]) for k in self])

    def sorted(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the s ort key of
             each element. The callable should expect an **item**
             (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(), key=key, reverse=reverse))

    def inverted(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=True))

    def counts(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super(OrderedMultiDict, self).__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def keys(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def values(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def items(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
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


# A couple of convenient aliases
OMD = OrderedMultiDict
MultiDict = OrderedMultiDict


class FastIterOrderedMultiDict(OrderedMultiDict):
    """An OrderedMultiDict backed by a skip list.  Iteration over keys
    is faster and uses constant memory but adding duplicate key-value
    pairs is slower. Brainchild of Mark Williams.
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

if __name__ == '__main__':
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
