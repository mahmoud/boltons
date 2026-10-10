from pickle import loads, dumps

import pytest

from boltons.namedutils import namedlist, namedtuple

Point = namedtuple('Point', 'x, y', rename=True)
MutablePoint = namedlist('MutablePoint', 'x, y', rename=True)


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


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
@pytest.mark.parametrize('name', ['value²', 'value½'])
def test_non_identifier_alphanumeric_field_name(factory, name):
    with pytest.raises(ValueError):
        factory('Record', ['x', name])


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
@pytest.mark.parametrize('name', ['Record²', 'Record½'])
def test_non_identifier_alphanumeric_type_name(factory, name):
    with pytest.raises(ValueError):
        factory(name, ['x'])


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
@pytest.mark.parametrize('name', ['value²', 'value½'])
def test_rename_non_identifier_alphanumeric_field_name(factory, name):
    record_type = factory('Record', ['x', name, 'α'], rename=True)
    assert record_type._fields == ('x', '_1', 'α')
    value = record_type(1, 2, 3)
    assert value.x == 1
    assert value._1 == 2
    assert value.α == 3
