from boltons.iterutils import first


isbool = lambda x: isinstance(x, bool)
isint = lambda x: isinstance(x, int)
odd = lambda x: isint(x) and x % 2 != 0
even = lambda x: isint(x) and x % 2 == 0
is_meaning_of_life = lambda x: x == 42


class TestFirst(object):
    def test_empty_iterables(self):
        """
        Empty iterables return None.
        """
        s = set()
        l = []
        assert first(s) is None
        assert first(l) is None

    def test_default_value(self):
        """
        Empty iterables + a default value return the default value.
        """
        s = set()
        l = []
        assert first(s, default=42) == 42
        assert first(l, default=3.14) == 3.14

        l = [0, False, []]
        assert first(l, default=3.14) == 3.14

    def test_selection(self):
        """
        Success cases with and without a key function.
        """
        l = [(), 0, False, 3, []]

        assert first(l, default=42) == 3
        assert first(l, key=isint) == 0
        assert first(l, key=isbool) is False
        assert first(l, key=odd) == 3
        assert first(l, key=even) == 0
        assert first(l, key=is_meaning_of_life) is None
