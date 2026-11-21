from pickle import loads, dumps

import pytest

from boltons.namedutils import namedlist, namedtuple

Point = namedtuple('Point', 'x, y', rename=True)
MutablePoint = namedlist('MutablePoint', 'x, y', rename=True)


@pytest.mark.parametrize('fields', ['self', 'self value', 'value self'])
@pytest.mark.parametrize('rename', [False, True])
def test_namedlist_self_field(fields, rename):
    record_type = namedlist('Record', fields, rename=rename)
    values = dict((field, i) for i, field in enumerate(fields.split()))
    record = record_type(**values)
    assert list(record) == list(values.values())
    assert record._asdict() == values
    assert record.self == values['self']
    record.self = 10
    assert record._asdict()['self'] == 10
    assert record._replace(self=20).self == 20
    assert record_type._make(record).self == 10
    assert 'self=10' in repr(record)


def test_namedlist_internal_receiver_field_is_renamed():
    record_type = namedlist('Record', ['_self', 'value'], rename=True)
    assert record_type._fields == ('_0', 'value')
    assert record_type(1, value=2) == [1, 2]


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
