import importlib.util

import pytest

from boltons import urlutils
from boltons.dictutils import FastIterOrderedMultiDict, OrderedMultiDict
from boltons.urlutils import QueryParamDict

# urlutils also supports being copied into a project as a standalone module.
_spec = importlib.util.spec_from_file_location(
    'standalone_urlutils', urlutils.__file__)
_standalone = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_standalone)
CLASSES = [OrderedMultiDict, FastIterOrderedMultiDict, QueryParamDict,
           _standalone.OrderedMultiDict, _standalone.QueryParamDict]


@pytest.mark.parametrize('cls', CLASSES)
@pytest.mark.parametrize('method', ['update', 'update_extend'])
def test_keyword_only_updates(cls, method):
    items = cls([('a', 1), ('b', 2), ('a', 3)])
    assert getattr(items, method)() is None
    assert items.items(multi=True) == [('a', 1), ('b', 2), ('a', 3)]

    assert getattr(items, method)(a=4, c=5) is None
    expected = ([('b', 2), ('a', 4), ('c', 5)] if method == 'update'
                else [('a', 1), ('b', 2), ('a', 3), ('a', 4), ('c', 5)])
    assert items.items(multi=True) == expected
    assert items.getlist('a') == ([4] if method == 'update' else [1, 3, 4])
    assert items['c'] == 5


@pytest.mark.parametrize('cls', CLASSES)
@pytest.mark.parametrize('method', ['update', 'update_extend'])
@pytest.mark.parametrize('self_source', [False, True])
def test_keywords_follow_positional_updates(cls, method, self_source):
    initial = [('a', 1), ('b', 2), ('a', 3)]
    items = cls(initial)
    source = items if self_source else [('a', 6), ('c', 7), ('a', 8)]
    source_pairs = initial if self_source else list(source)

    assert getattr(items, method)(source, a=9, d=10) is None
    if method == 'update':
        expected = [('b', 2)]
        if not self_source:
            expected.append(('c', 7))
        expected.extend([('a', 9), ('d', 10)])
    else:
        expected = initial + source_pairs + [('a', 9), ('d', 10)]
    assert items.items(multi=True) == expected
    assert items.getlist('a') == [v for k, v in expected if k == 'a']


def test_query_parameter_keyword_updates_serialize():
    from boltons.urlutils import URL

    url = URL('https://example.com/?tag=a&tag=b')
    url.query_params.update_extend(tag='c', page='1')
    assert url.to_text() == 'https://example.com/?tag=a&tag=b&tag=c&page=1'
    url.query_params.update(url.query_params, tag='d')
    assert url.to_text() == 'https://example.com/?page=1&tag=d'
