from collections import UserDict
from types import MappingProxyType

import pytest

from boltons.dictutils import OneToOne


class KeysMapping:
    def __init__(self, pairs):
        self.data = dict(pairs)

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self.data[key]


def _mapping(inverse):
    if inverse:
        return OneToOne({1: 'a', 2: 'b'}).inv
    return OneToOne({'a': 1, 'b': 2})


def _check(mapping, expected):
    assert dict(mapping) == expected
    assert dict(mapping.inv) == {value: key for key, value in expected.items()}
    assert len(mapping) == len(mapping.inv)
    assert mapping.inv.inv is mapping


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
@pytest.mark.parametrize('updates, expected', [
    ({}, {'a': 1, 'b': 2}),
    ({'c': 3}, {'a': 1, 'b': 2, 'c': 3}),
    ({'a': 3}, {'a': 3, 'b': 2}),
    ({'c': 2}, {'a': 1, 'c': 2}),
    ({'a': 2, 'b': 1}, {'a': 2, 'b': 1}),
    ({'c': 1, 'd': 1}, {'b': 2, 'd': 1}),
    ({None: (3, 4)}, {'a': 1, 'b': 2, None: (3, 4)}),
])
def test_onetoone_inplace_union(inverse, updates, expected):
    mapping = original = _mapping(inverse)
    original_inverse = mapping.inv

    mapping |= updates

    assert mapping is original
    assert mapping.inv is original_inverse
    _check(mapping, expected)


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
@pytest.mark.parametrize('make_other', [
    list, tuple, iter, lambda pairs: (pair for pair in pairs),
    lambda pairs: UserDict(dict(pairs)),
    lambda pairs: MappingProxyType(dict(pairs)),
    KeysMapping, OneToOne,
])
def test_onetoone_inplace_union_inputs(inverse, make_other):
    mapping = _mapping(inverse)
    other = make_other([('c', 2), ('d', 3)])

    mapping |= other

    _check(mapping, {'a': 1, 'c': 2, 'd': 3})


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
@pytest.mark.parametrize('make_other', [
    list, tuple, iter, lambda pairs: (pair for pair in pairs),
])
def test_onetoone_inplace_union_repeated_pairs(inverse, make_other):
    mapping = _mapping(inverse)

    mapping |= make_other([('a', 1), ('b', 2), ('a', 2)])

    # Converting the pairs to dict first would incorrectly leave {'b': 2}.
    _check(mapping, {'a': 2})


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
def test_onetoone_inplace_union_iterator_pairs(inverse):
    mapping = _mapping(inverse)

    mapping |= (iter(pair) for pair in [('a', 1), ('b', 2), ('a', 2)])

    _check(mapping, {'a': 2})


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
@pytest.mark.parametrize('use_inverse', [False, True])
def test_onetoone_inplace_union_alias(inverse, use_inverse):
    mapping = _mapping(inverse)
    other = mapping.inv if use_inverse else mapping

    mapping |= other

    expected = {'a': 1, 'b': 2}
    if use_inverse:
        expected.update({1: 'a', 2: 'b'})
    assert other is (mapping.inv if use_inverse else mapping)
    _check(mapping, expected)


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
@pytest.mark.parametrize('other, error', [
    (None, TypeError),
    (42, TypeError),
    ({'c': 3, 'd': []}, TypeError),
    ([('c', 3), ('d', [])], TypeError),
    ([('c', 3), ([], 4)], TypeError),
    ([('c', 3), ('d',)], ValueError),
    ([('c', 3), ('d', 4, 5)], ValueError),
])
def test_onetoone_inplace_union_invalid_input(inverse, other, error):
    mapping = _mapping(inverse)

    with pytest.raises(error):
        mapping |= other

    _check(mapping, {'a': 1, 'b': 2})


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
def test_onetoone_inplace_union_broken_iterator(inverse):
    def pairs():
        yield 'c', 3
        raise RuntimeError('input failed')

    mapping = _mapping(inverse)

    with pytest.raises(RuntimeError, match='input failed'):
        mapping |= pairs()

    _check(mapping, {'a': 1, 'b': 2})


@pytest.mark.parametrize('inverse', [False, True], ids=['forward', 'inverse'])
def test_onetoone_inplace_union_followed_by_mutations(inverse):
    mapping = _mapping(inverse)
    mapping |= {'a': 3, 'c': 2}

    mapping.inv[2] = 'd'
    assert mapping.pop('a') == 3
    mapping['e'] = 4
    del mapping.inv[4]

    _check(mapping, {'d': 2})


def test_onetoone_inplace_union_empty_subclass():
    class Mapping(OneToOne):
        pass

    mapping = original = Mapping()
    original_inverse = mapping.inv

    mapping |= iter([('a', 1)])

    assert mapping is original
    assert mapping.inv is original_inverse
    assert isinstance(mapping, Mapping)
    assert isinstance(mapping.inv, Mapping)
    _check(mapping, {'a': 1})
