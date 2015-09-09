# -*- coding: utf-8 -*-

from boltons.dictutils import OMD

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
    _rng_redun = list(range(size//redun)) * redun
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
        # first, test all items made the jump
        assert len(omd.items(multi=True)) == len(iomd.items(multi=True))

        for val in omd.values():
            assert val in iomd  # all values present as keys


def test_poplast():
    for items in _ITEMSETS[1:]:
        omd = OMD(items)
        assert omd.poplast() == items[-1][-1]


def test_pop():
    omd = OMD()
    omd.add('even', 0)
    omd.add('odd', 1)
    omd.add('even', 2)

    assert omd.pop('odd') == 1
    assert omd.pop('odd', 99) == 99
    try:
        omd.pop('odd')
        import pdb;pdb.set_trace()
        assert False
    except KeyError:
        pass

    assert len(omd) == 1
    assert len(omd.items(multi=True)) == 2


def test_pop_all():
    omd = OMD()
    omd.add('even', 0)
    omd.add('odd', 1)
    omd.add('even', 2)

    assert omd.popall('odd') == [1]
    assert len(omd) == 1
    try:
        omd.popall('odd')
        assert False
    except KeyError:
        pass
    assert omd.popall('odd', None) is None

    assert omd.popall('even') == [0, 2]
    assert len(omd) == 0
    assert omd.popall('nope', None) is None


def test_reversed():
    try:
        from collections import OrderedDict
    except:
        # skip on python 2.6
        return
    for items in _ITEMSETS:
        omd = OMD(items)
        od = OrderedDict(items)
        for ik, ok in zip(reversed(od), reversed(omd)):
            assert ik == ok

    r100 = range(100)
    omd = OMD(zip(r100, r100))
    for i in r100:
        omd.add(i, i)
    r100 = list(reversed(r100))
    assert list(reversed(omd)) == r100

    omd = OMD()
    assert list(reversed(omd)) == list(reversed(omd.keys()))
    for i in range(20):
        for j in range(i):
            omd.add(i, i)
    assert list(reversed(omd)) == list(reversed(omd.keys()))


def test_setdefault():
    omd = OMD()
    empty_list = []
    x = omd.setdefault('1', empty_list)
    assert x is empty_list
    y = omd.setdefault('2')
    assert y is None
    assert omd.setdefault('1', None) is empty_list
