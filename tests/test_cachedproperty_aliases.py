import importlib.util

import pytest

from boltons import cacheutils, urlutils


@pytest.mark.parametrize('descriptor', [
    cacheutils.cachedproperty, urlutils.cachedproperty,
])
@pytest.mark.parametrize('value', [None, False, 0, '', [], {'a': 1}])
@pytest.mark.parametrize('alias_first', [False, True])
def test_aliases_share_cached_value(descriptor, value, alias_first):
    class Example:
        calls = 0

        @descriptor
        def canonical(self):
            self.calls += 1
            return value

        alias = canonical

    obj = Example()
    first = 'alias' if alias_first else 'canonical'
    second = 'canonical' if alias_first else 'alias'
    assert getattr(obj, first) is value
    assert getattr(obj, second) is value
    assert obj.alias is value
    assert obj.calls == 1
    del obj.canonical
    assert obj.alias is value
    assert obj.calls == 2
    assert Example.canonical is Example.alias


_spec = importlib.util.spec_from_file_location(
    'standalone_urlutils', urlutils.__file__)
_standalone = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_standalone)


@pytest.mark.parametrize('cls', [urlutils.URL, _standalone.URL])
@pytest.mark.parametrize('alias_first', [False, True])
def test_query_alias_preserves_edits(cls, alias_first):
    url = cls('https://example.com/?tag=a&tag=b')
    params = url.qp if alias_first else url.query_params
    params.add('tag', 'c')
    assert url.qp is params
    url.qp['page'] = '1'
    assert url.query_params is params
    assert url.qp.getlist('tag') == ['a', 'b', 'c']
    assert url.to_text() == 'https://example.com/?tag=a&tag=b&tag=c&page=1'
    assert url.qp is params


def test_explicit_query_cache_replacement_and_invalidation():
    url = urlutils.URL('https://example.com/?a=1')
    replacement = urlutils.QueryParamDict([('b', '2')])
    url.query_params = replacement
    assert url.qp is replacement
    assert url.to_text() == 'https://example.com/?b=2'
    del url.query_params
    assert url.qp['a'] == '1'
    assert url.query_params is url.qp
