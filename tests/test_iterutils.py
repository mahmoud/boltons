
import pytest

from boltons.iterutils import first, remap


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


class TestRemap(object):
    def test_basic_clone(self):
        orig = {"a": "b", "c": [1, 2]}
        assert orig == remap(orig)

        orig2 = [{1: 2}, {"a": "b", "c": [1, 2, {"cat": "dog"}]}]
        assert orig2 == remap(orig2)

    def test_empty(self):
        assert [] == remap([])
        assert {} == remap({})
        obj = object()
        assert obj is remap(obj)

    def test_basic_upper(self):
        orig = {'a': 1, 'b': object(), 'c': {'d': set()}}
        remapped = remap(orig, lambda k, v: (k.upper(), v))
        assert orig['a'] == remapped['A']
        assert orig['b'] == remapped['B']
        assert orig['c']['d'] == remapped['C']['D']

    def test_item_drop(self):
        orig = range(10)
        even_items = remap(orig, lambda k, v: not (v % 2))
        assert even_items == [0, 2, 4, 6, 8]

    def test_noncallables(self):
        with pytest.raises(TypeError):
            remap([], handle_item='test')
        with pytest.raises(TypeError):
            remap([], handle_push='test')
        with pytest.raises(TypeError):
            remap([], handle_pop='test')

    def test_selfref(self):
        selfref = range(4)
        selfref.append(selfref)
        assert selfref == remap(selfref)

        selfref2 = {}
        selfref2['self'] = selfref2
        assert selfref2 == remap(selfref2)
