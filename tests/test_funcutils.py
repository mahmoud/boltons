import threading
import time

import pytest

from boltons.funcutils import (copy_function,
                               total_ordering,
                               partial_ordering,
                               format_invocation,
                               InstancePartial,
                               CachedInstancePartial,
                               noop,
                               once)


class Greeter:
    def __init__(self, greeting):
        self.greeting = greeting

    def greet(self, excitement='.'):
        return self.greeting.capitalize() + excitement

    partial_greet = InstancePartial(greet, excitement='!')
    cached_partial_greet = CachedInstancePartial(greet, excitement='...')

    def native_greet(self):
        return self.greet(';')


class SubGreeter(Greeter):
    pass


def test_partials():
    g = SubGreeter('hello')

    assert g.greet() == 'Hello.'
    assert g.native_greet() == 'Hello;'
    assert g.partial_greet() == 'Hello!'
    assert g.cached_partial_greet() == 'Hello...'
    assert CachedInstancePartial(g.greet, excitement='s')() == 'Hellos'

    g.native_greet = 'native reassigned'
    assert g.native_greet == 'native reassigned'

    g.partial_greet = 'partial reassigned'
    assert g.partial_greet == 'partial reassigned'

    g.cached_partial_greet = 'cached_partial reassigned'
    assert g.cached_partial_greet == 'cached_partial reassigned'


def test_copy_function():
    def callee():
        return 1
    callee_copy = copy_function(callee)
    assert callee is not callee_copy
    assert callee() == callee_copy()


def test_partial_ordering_from_object():
    @partial_ordering
    class PartiallyOrdered:
        def __init__(self, values):
            self.values = set(values)

        def __le__(self, other):
            return self.values <= other.values

        def __ge__(self, other):
            return self.values >= other.values

    values = [{1}, {1, 2}, {2}]
    for left in values:
        for right in values:
            a, b = PartiallyOrdered(left), PartiallyOrdered(right)
            assert (a < b) == (left < right)
            assert (a > b) == (left > right)
            assert (a == b) == (left == right)
            assert (a != b) == (left != right)
            assert (a <= b) == (left <= right)
            assert (a >= b) == (left >= right)
    with pytest.raises(TypeError):
        hash(PartiallyOrdered({1}))


@pytest.mark.parametrize('inherited', [False, True])
def test_partial_ordering_preserves_defined_comparisons(inherited):
    class Defined:
        def __lt__(self, other):
            return 'custom lt'

        def __gt__(self, other):
            return 'custom gt'

        def __eq__(self, other):
            return 'custom eq'

        def __hash__(self):
            return 42

    cls = type('Child', (Defined,), {}) if inherited else Defined
    decorated = partial_ordering(cls)
    assert decorated is cls
    a, b = cls(), cls()
    assert (a < b) == 'custom lt'
    assert (a > b) == 'custom gt'
    assert (a == b) == 'custom eq'
    assert hash(a) == 42


def test_partial_ordering_preserves_custom_hash():
    @partial_ordering
    class Hashable:
        def __le__(self, other):
            return True

        def __ge__(self, other):
            return True

        def __hash__(self):
            return 42

    assert hash(Hashable()) == 42


def test_total_ordering():
    @total_ordering
    class Number:
        def __init__(self, val):
            self.val = int(val)

        def __gt__(self, other):
            return self.val > other

        def __eq__(self, other):
            return self.val == other

    num = Number(3)
    assert num > 0
    assert num == 3

    assert num < 5
    assert num >= 2
    assert num != 1


def test_format_invocation():
    assert format_invocation('d') == "d()"
    assert format_invocation('f', ('a', 'b')) == "f('a', 'b')"
    assert format_invocation('g', (), {'x': 'y'})  == "g(x='y')"
    assert format_invocation('h', ('a', 'b'), {'x': 'y', 'z': 'zz'}) == "h('a', 'b', x='y', z='zz')"

def test_noop():
    assert noop() is None
    assert noop(1, 2) is None
    assert noop(a=1, b=2) is None


def test_once_executes_only_once():
    call_count = 0

    @once
    def get_value():
        nonlocal call_count
        call_count += 1
        return 42

    assert get_value() == 42
    assert get_value() == 42
    assert get_value() == 42
    assert call_count == 1


def test_once_caches_result():
    @once
    def get_list():
        return [1, 2, 3]

    result1 = get_list()
    result2 = get_list()
    assert result1 is result2


def test_once_thread_safety():
    call_count = 0
    barrier = threading.Barrier(10)

    @once
    def slow_computation():
        nonlocal call_count
        call_count += 1
        time.sleep(0.5)
        return 99

    results = []
    errors = []

    def worker():
        try:
            barrier.wait()
            results.append(slow_computation())
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert call_count == 1
    assert all(r == 99 for r in results)
    assert len(results) == 10
