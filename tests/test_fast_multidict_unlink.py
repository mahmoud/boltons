import random

import pytest

from boltons.dictutils import FastIterOrderedMultiDict, OrderedMultiDict


@pytest.mark.parametrize('pairs, key', [
    ([('a', 1), ('b', 2), ('a', 3)], 'b'),
    ([('a', 1), ('b', 2), ('a', 3)], 'a'),
    ([('a', 1), ('b', 2), ('b', 3), ('a', 4), ('c', 5), ('b', 6)], 'b'),
    ([('a', 1), ('b', 2), ('c', 3)], 'b'),
    ([('a', 1), ('a', 2)], 'a'),
])
@pytest.mark.parametrize('operation', [
    'delete', 'set', 'popall', 'pop', 'update',
])
def test_fast_multidict_unlinks_all_values(pairs, key, operation):
    items = FastIterOrderedMultiDict(pairs)
    reference = OrderedMultiDict(pairs)

    def apply(mapping):
        if operation == 'delete':
            del mapping[key]
        elif operation == 'set':
            mapping[key] = 10
        elif operation == 'update':
            mapping.update({key: 10})
        else:
            return getattr(mapping, operation)(key)

    assert apply(items) == apply(reference)

    def check():
        assert items.items(multi=True) == reference.items(multi=True)
        assert items.items() == reference.items()
        assert items.keys() == reference.keys()
        assert list(reversed(items)) == list(reversed(reference))
        assert len(items) == len(reference)
        for k in reference:
            assert items.getlist(k) == reference.getlist(k)

    check()
    items.add(key, 11)
    reference.add(key, 11)
    check()
    while reference:
        assert items.poplast() == reference.poplast()
        check()


def test_fast_multidict_mixed_mutations_match_reference():
    rng = random.Random(20261026)
    items = FastIterOrderedMultiDict()
    reference = OrderedMultiDict()
    for _ in range(1000):
        key, value = rng.randrange(5), rng.randrange(10)
        operation = rng.choice(['add', 'set', 'delete', 'poplast',
                                'popall', 'update', 'clear'])
        for mapping in (items, reference):
            if operation == 'add':
                mapping.add(key, value)
            elif operation == 'set':
                mapping[key] = value
            elif operation == 'delete':
                if key in mapping:
                    del mapping[key]
            elif operation == 'update':
                mapping.update([(key, value), (key, value + 1)])
            elif operation == 'clear':
                mapping.clear()
            elif key in mapping:
                getattr(mapping, operation)(key)
        assert items.items(multi=True) == reference.items(multi=True)
        assert items.items() == reference.items()
        assert items.values() == reference.values()
        assert items.keys() == reference.keys()
        assert list(reversed(items)) == list(reversed(reference))
        assert items.todict(multi=True) == reference.todict(multi=True)
