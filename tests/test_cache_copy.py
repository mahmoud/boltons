import pytest
from boltons.cacheutils import LRI, LRU


@pytest.mark.parametrize('cache_type', [LRI, LRU])
def test_copy_preserves_eviction_without_reading_source(cache_type):
    cache = cache_type(max_size=2, values=[('a', 1), ('b', 2)])
    cache['a'] = 3
    hits = cache.hit_count
    copied = cache.copy()
    assert cache.hit_count == hits
    cache['c'] = copied['c'] = 4
    assert set(cache) == set(copied) == {'a', 'c'}


@pytest.mark.parametrize('cache_type', [LRI, LRU])
def test_copy_preserves_miss_handler(cache_type):
    handler = lambda key: key.upper()
    cache = cache_type(max_size=2, on_miss=handler)
    copied = cache.copy()
    assert copied.on_miss is handler
    assert copied['a'] == 'A'
    assert 'a' not in cache
