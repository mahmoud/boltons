import pytest

from boltons.dictutils import ManyToMany


def assert_pairs(relation, expected):
    assert set(relation.iteritems()) == expected
    assert set(relation.inv.iteritems()) == {(value, key) for key, value in expected}


@pytest.mark.parametrize('inverse', [False, True])
@pytest.mark.parametrize('pairs, expected', [
    (
        [('old', 'a'), ('new', 'b'), ('other', 'c')],
        {('new', 'a'), ('new', 'b'), ('other', 'c')},
    ),
    (
        [('old', 'a'), ('old', 'shared'), ('new', 'shared'), ('new', 'b'), ('other', 'shared')],
        {('new', 'a'), ('new', 'shared'), ('new', 'b'), ('other', 'shared')},
    ),
    (
        [('old', 'a'), ('new', 'a')],
        {('new', 'a')},
    ),
    (
        [('old', 'a'), ('other', 'b')],
        {('new', 'a'), ('other', 'b')},
    ),
])
def test_manytomany_replace_merges_existing_target(pairs, expected, inverse):
    if inverse:
        relation = ManyToMany((value, key) for key, value in pairs)
        assert relation.inv.replace('old', 'new') is None
        expected = {(value, key) for key, value in expected}
    else:
        relation = ManyToMany(pairs)
        assert relation.replace('old', 'new') is None

    assert_pairs(relation, expected)
    for key, value in list(expected):
        relation.remove(key, value)
    assert_pairs(relation, set())
    assert not relation
    assert not relation.inv


@pytest.mark.parametrize('key, newkey', [('old', 'old'), (1, True), (None, None)])
def test_manytomany_replace_same_key(key, newkey):
    pairs = {(key, 'a'), (key, 'b'), ('other', 'a')}
    relation = ManyToMany(pairs)
    assert relation.replace(key, newkey) is None
    assert_pairs(relation, pairs)


@pytest.mark.parametrize('pairs', [[], [('new', 'a'), ('other', 'b')]])
def test_manytomany_replace_missing_key(pairs):
    relation = ManyToMany(pairs)
    assert relation.replace('missing', 'new') is None
    assert_pairs(relation, set(pairs))


def test_manytomany_replace_unhashable_target_preserves_relation():
    pairs = {('old', 'a'), ('other', 'b')}
    relation = ManyToMany(pairs)
    with pytest.raises(TypeError):
        relation.replace('old', [])
    assert_pairs(relation, pairs)
