import importlib.util

import pytest

from boltons import urlutils
from boltons.dictutils import FastIterOrderedMultiDict, OrderedMultiDict
from boltons.urlutils import QueryParamDict

_spec = importlib.util.spec_from_file_location(
    'standalone_urlutils', urlutils.__file__)
_standalone = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_standalone)
CLASSES = [OrderedMultiDict, FastIterOrderedMultiDict, QueryParamDict,
           _standalone.OrderedMultiDict, _standalone.QueryParamDict]


@pytest.mark.parametrize('cls', CLASSES)
@pytest.mark.parametrize('pairs', [
    [], [('a', 1)], [('a', 1), ('a', 2)],
    [('a', 1), ('b', 2), ('a', 3)],
    [('a', 1), ('b', 2), ('b', 3), ('c', 4)],
    [(None, None), ('a', []), (None, [1])],
])
def test_popitem_matches_dict_and_preserves_multidict_state(cls, pairs):
    items = cls(pairs)
    reference = dict(pairs)
    remaining = list(pairs)
    while reference:
        expected = reference.popitem()
        assert items.popitem() == expected
        key = expected[0]
        remaining = [(k, v) for k, v in remaining if k != key]
        assert items.items(multi=True) == remaining
        assert len(items) == len(reference)
        assert items.keys() == list(reference)
        for k in reference:
            assert items.getlist(k) == [v for rk, v in remaining if rk == k]
    with pytest.raises(KeyError):
        items.popitem()
    assert items.items(multi=True) == []
    items.add('new', 1)
    items.add('new', 2)
    assert items.getlist('new') == [1, 2]
    assert items.poplast('new') == 2
    assert items.popitem() == ('new', 1)
    assert items.items(multi=True) == []


def test_query_serialization_after_popitem():
    url = urlutils.URL('https://example.com/?a=1&b=2&a=3')
    assert url.query_params.popitem() == ('b', '2')
    assert url.to_text() == 'https://example.com/?a=1&a=3'
