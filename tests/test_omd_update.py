import pytest

from boltons.dictutils import FastIterOrderedMultiDict, OrderedMultiDict
from boltons.urlutils import URL, QueryParamDict
from boltons.urlutils import OrderedMultiDict as URLOrderedMultiDict


@pytest.fixture(params=[OrderedMultiDict, FastIterOrderedMultiDict,
                       URLOrderedMultiDict, QueryParamDict],
                ids=['omd', 'fast_omd', 'url_omd', 'query_params'])
def omd_type(request):
    return request.param


@pytest.fixture(params=[list, iter], ids=['list', 'iterator'])
def iterable_type(request):
    return request.param


@pytest.mark.parametrize('initial', [
    [],
    [('a', -1), ('a', -2)],
    [('a', -1), ('b', -2)],
], ids=['new_keys', 'mixed_keys', 'existing_keys'])
def test_update_repeated_keys(omd_type, iterable_type, initial):
    mapping = omd_type([('keep', 0)] + initial)
    pairs = [('a', 1), ('b', 2), ('a', 3), ('b', 4), ('a', 5)]

    assert mapping.update(iterable_type(pairs)) is None

    assert mapping.items(multi=True) == [('keep', 0)] + pairs
    assert mapping.getlist('a') == [1, 3, 5]
    assert mapping.getlist('b') == [2, 4]
    assert list(mapping) == ['keep', 'a', 'b']
    assert mapping.todict() == {'keep': 0, 'a': 5, 'b': 4}


def test_update_repeated_keys_with_keywords(omd_type, iterable_type):
    mapping = omd_type([('keep', 0)])
    pairs = [('a', 1), ('b', 2), ('a', 3), ('b', 4)]

    mapping.update(iterable_type(pairs), a=99, new=42)

    assert mapping.items(multi=True) == [
        ('keep', 0), ('b', 2), ('b', 4), ('a', 99), ('new', 42),
    ]
    assert mapping.getlist('a') == [99]


def test_url_query_update_repeated_keys():
    url = URL('https://example.com/search?keep=original&existing=old')

    url.qp.update(iter([('tag', 'python'), ('existing', 'one'),
                        ('tag', 'testing'), ('existing', 'two')]))

    assert url.to_text() == ('https://example.com/search?keep=original'
                             '&tag=python&existing=one'
                             '&tag=testing&existing=two')
