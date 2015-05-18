from boltons.cacheutils import LRU


class TestLRU:

    def test_popitem_should_return_a_tuple(self):
        cache = LRU()
        cache['t'] = 42
        assert cache.popitem() == ('t', 42)
