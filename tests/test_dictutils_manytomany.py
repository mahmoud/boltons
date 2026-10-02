import pytest

from boltons.dictutils import ManyToMany


def _assert_pairs(mapping, pairs):
    assert set(mapping.iteritems()) == pairs
    assert set(mapping.inv.iteritems()) == {(value, key) for key, value in pairs}
    assert set(mapping) == {key for key, value in pairs}
    assert set(mapping.inv) == {value for key, value in pairs}
    assert mapping.inv.inv is mapping


@pytest.mark.parametrize('mutate_source', [False, True])
@pytest.mark.parametrize('inverse', [False, True])
@pytest.mark.parametrize('operation', ['add', 'remove'])
def test_many_to_many_copy_is_independent(mutate_source, inverse, operation):
    pairs = {('a', 1), ('b', 2)}
    source = ManyToMany(pairs)
    copied = ManyToMany(source)
    changed, unchanged = (source, copied) if mutate_source else (copied, source)

    if operation == 'add':
        if inverse:
            changed.inv.add(1, 'c')
            expected = pairs | {('c', 1)}
        else:
            changed.add('a', 3)
            expected = pairs | {('a', 3)}
    else:
        if inverse:
            changed.inv.remove(1, 'a')
        else:
            changed.remove('a', 1)
        expected = pairs - {('a', 1)}

    _assert_pairs(changed, expected)
    _assert_pairs(unchanged, pairs)


@pytest.mark.parametrize(
    'initial',
    [
        [],
        [('a', 3)],
        [('c', 1)],
        [('a', 3), ('c', 1)],
    ],
)
def test_many_to_many_update_is_independent(initial):
    pairs = {('a', 1), ('b', 2)}
    source = ManyToMany(pairs)
    target = ManyToMany(initial)
    assert target.update(source) is None
    expected = pairs | set(initial)
    _assert_pairs(target, expected)

    source.add('a', 4)
    source.inv.add(1, 'd')
    _assert_pairs(target, expected)

    target.add('b', 5)
    target.inv.add(2, 'e')
    _assert_pairs(target, expected | {('b', 5), ('e', 2)})
    _assert_pairs(source, pairs | {('a', 4), ('d', 1)})


@pytest.mark.parametrize('pairs', [[], [('a', 1), ('a', 2), ('b', 2)]])
def test_many_to_many_self_update(pairs):
    mapping = ManyToMany(pairs)
    mapping.update(mapping)
    _assert_pairs(mapping, set(pairs))


def test_many_to_many_copy_preserves_items():
    key, value = object(), object()
    source = ManyToMany([(key, value)])
    copied = ManyToMany(source)
    copied_key, copied_value = next(copied.iteritems())
    assert copied_key is key
    assert copied_value is value
