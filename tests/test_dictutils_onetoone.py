import pytest

from boltons.dictutils import OneToOne


@pytest.mark.parametrize('source_type', [dict, list, tuple, iter])
@pytest.mark.parametrize('pairs', [[], [('a', 1)], [('a', 1), ('b', 2)]])
def test_update_preserves_all_pairs(source_type, pairs):
    mapping = OneToOne({'existing': 0})
    inverse = mapping.inv

    result = mapping.update(source_type(pairs), extra=3)

    expected = dict(pairs, existing=0, extra=3)
    assert result is None
    assert mapping == expected
    assert mapping.inv is inverse
    assert inverse == {value: key for key, value in expected.items()}
    assert inverse.inv is mapping


def test_update_generator():
    mapping = OneToOne()
    mapping.update((str(value), value) for value in range(3))

    assert mapping == {'0': 0, '1': 1, '2': 2}
    assert mapping.inv == {0: '0', 1: '1', 2: '2'}


def test_update_inverse_iterator():
    mapping = OneToOne({'a': 1})
    mapping.inv.update(iter([(1, 'b'), (2, 'c')]))

    assert mapping == {'b': 1, 'c': 2}
    assert mapping.inv == {1: 'b', 2: 'c'}


def test_update_iterator_conflicts_and_keywords():
    mapping = OneToOne({'a': 0, 'b': 1})
    mapping.update(iter([('c', 1), ('a', 2), ('d', 2)]), c=3)

    assert mapping == {'c': 3, 'd': 2}
    assert mapping.inv == {3: 'c', 2: 'd'}


@pytest.mark.parametrize('source_type', [list, iter])
@pytest.mark.parametrize('invalid_pair', [([], 3), ('c', [])])
def test_update_validates_all_pairs_before_mutating(source_type, invalid_pair):
    mapping = OneToOne({'existing': 0})

    with pytest.raises(TypeError):
        mapping.update(source_type([('a', 1), ('b', 2), invalid_pair]))

    assert mapping == {'existing': 0}
    assert mapping.inv == {0: 'existing'}


def test_update_validates_keywords_before_mutating():
    mapping = OneToOne({'existing': 0})

    with pytest.raises(TypeError):
        mapping.update(iter([('a', 1)]), invalid=[])

    assert mapping == {'existing': 0}
    assert mapping.inv == {0: 'existing'}
