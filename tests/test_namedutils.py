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


@pytest.mark.parametrize("factory", [namedtuple, namedlist])
def test_non_identifier_alnum_name(factory):
    # '²' passes str.isalnum() but is not valid in a Python identifier
    with pytest.raises(ValueError):
        factory('T', ['value\u00b2'])
    assert factory('T', ['value\u00b2', 'b'], rename=True)._fields == ('_0', 'b')


@pytest.mark.parametrize('factory', [namedtuple, namedlist])
@pytest.mark.parametrize('typename, compiled_name', [('Ｐoint', 'Point'), ('Klass', 'Klass')])
def test_normalized_type_names(factory, typename, compiled_name, monkeypatch):
    record_type = factory(typename, ['x', 'y'])
    assert record_type.__name__ == compiled_name
    point = record_type(x=1, y=2)
    assert (point.x, point.y) == (1, 2)
    assert tuple(point) == (1, 2)
    # The class statement stores its normalized spelling in the namespace.
    monkeypatch.setitem(globals(), compiled_name, record_type)
    restored = loads(dumps(point))
    assert type(restored) is record_type
    assert (restored.x, restored.y) == (1, 2)
