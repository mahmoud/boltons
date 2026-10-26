from pickle import loads, dumps
import copy
import pickle

import pytest

from boltons.namedutils import namedlist, namedtuple

Point = namedtuple('Point', 'x, y', rename=True)
MutablePoint = namedlist('MutablePoint', 'x, y', rename=True)


class TaggedPoint(MutablePoint):
    def __getstate__(self):
        return {'tag': self.tag}

    def __setstate__(self, state):
        self.tag = state['tag']


def test_namedlist():
    p = MutablePoint(x=10, y=20)

    assert p == [10, 20]
    p[0] = 11
    assert p == [11, 20]
    p.x = 12
    assert p == [12, 20]


def test_namedlist_pickle():
    p = MutablePoint(x=10, y=20)
    assert p == loads(dumps(p))


def _cyclic_namedlist():
    first = MutablePoint(None, [])
    second = MutablePoint(first, first.y)
    first.x = second
    first.y.append(first)
    return first


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
def test_namedlist_pickle_cycles(protocol):
    original = _cyclic_namedlist()
    restored = loads(dumps(original, protocol=protocol))
    assert type(restored) is MutablePoint
    assert restored is not original
    assert restored.x.x is restored
    assert restored.x.y is restored.y
    assert restored.y[0] is restored


def test_namedlist_deepcopy_cycles():
    original = _cyclic_namedlist()
    restored = copy.deepcopy(original)
    assert type(restored) is MutablePoint
    assert restored is not original
    assert restored.x.x is restored
    assert restored.x.y is restored.y
    assert restored.y is not original.y
    assert restored.y[0] is restored


def test_namedlist_shallow_copy():
    original = _cyclic_namedlist()
    restored = copy.copy(original)
    assert restored is not original
    assert restored.x is original.x
    assert restored.y is original.y


@pytest.mark.parametrize('clone', [copy.copy, copy.deepcopy, lambda p: loads(dumps(p))])
def test_namedlist_custom_state(clone):
    original = TaggedPoint(1, 2)
    original.tag = 'metadata'
    restored = clone(original)
    assert type(restored) is TaggedPoint
    assert list(restored) == [1, 2]
    assert restored.tag == 'metadata'


@pytest.mark.parametrize('typename', ['type', 'iter'])
@pytest.mark.parametrize('clone', [copy.copy, copy.deepcopy])
def test_namedlist_copy_builtin_type_names(typename, clone):
    record_type = namedlist(typename, 'x y')
    original = record_type(1, 2)
    restored = clone(original)
    assert type(restored) is record_type
    assert restored is not original
    assert list(restored) == [1, 2]


def test_namedtuple_pickle():
    p = Point(x=10, y=20)
    assert p == loads(dumps(p))


@pytest.mark.parametrize("factory", [namedtuple, namedlist])
def test_empty_field_name_raises_value_error(factory):
    # `all()` is True for the empty string, so an empty name used to pass both
    # ValueError checks and reach `name[0].isdigit()`, raising IndexError.
    with pytest.raises(ValueError):
        factory('Point', ['x', ''])


@pytest.mark.parametrize("factory", [namedtuple, namedlist])
def test_empty_type_name_raises_value_error(factory):
    with pytest.raises(ValueError):
        factory('', ['x', 'y'])


@pytest.mark.parametrize("factory", [namedtuple, namedlist])
def test_invalid_character_still_raises_value_error(factory):
    with pytest.raises(ValueError):
        factory('Point', ['x', 'y-z'])


@pytest.mark.parametrize("factory", [namedtuple, namedlist])
def test_non_identifier_alnum_name(factory):
    # '²' passes str.isalnum() but is not valid in a Python identifier
    with pytest.raises(ValueError):
        factory('T', ['value\u00b2'])
    assert factory('T', ['value\u00b2', 'b'], rename=True)._fields == ('_0', 'b')
