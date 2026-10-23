import pytest

from boltons.dictutils import ManyToMany


@pytest.mark.parametrize('inverse', [False, True])
@pytest.mark.parametrize('invalid_value', [[], {}, set()])
def test_add_unhashable_value_preserves_relation(inverse, invalid_value):
    relation = ManyToMany([('existing', 'value')])
    target = relation.inv if inverse else relation
    before = set(relation.iteritems())
    before_inverse = set(relation.inv.iteritems())
    with pytest.raises(TypeError):
        target.add('new', invalid_value)
    assert set(relation.iteritems()) == before
    assert set(relation.inv.iteritems()) == before_inverse
    assert set(relation) == {'existing'}
    assert set(relation.inv) == {'value'}
    assert 'new' not in target


@pytest.mark.parametrize('inverse', [False, True])
def test_add_valid_edge_stays_synchronized(inverse):
    relation = ManyToMany()
    target = relation.inv if inverse else relation
    target.add('key', 'value')
    target.add('key', 'value')
    assert target['key'] == frozenset(['value'])
    assert target.inv['value'] == frozenset(['key'])
