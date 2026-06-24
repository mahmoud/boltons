import threading
import time
from boltons.funcutils import (copy_function,
                               total_ordering,
                               format_invocation,
                               InstancePartial,
                               CachedInstancePartial,
                               noop,
                               once,
                               wraps)


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

def test_wraps_preserves_kwargs_for_defaulted_args():
    """wraps must not collapse keyword args into positional args (issue #343).

    When a caller passes a defaulted parameter by keyword, the generated
    invocation must forward it as a keyword argument so that wrappers
    that inspect *args and **kwargs see the value in the right place.
    """
    def flip(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*reversed(args), **kwargs)
        return wrapper

    def power(x, y, msg=''):
        return (x, y, msg)

    flipped = flip(power)

    # keyword arg must stay in kwargs, not bleed into args
    assert flipped(3, 2, msg='abc') == (2, 3, 'abc')
    # positional-only call still works
    assert flipped(3, 2) == (2, 3, '')
    # passing the defaulted arg positionally: the generated wrapper binds it
    # as msg='pos' then forwards msg=msg (keyword), so the inner wrapper sees
    # args=(3, 2) and kwargs={'msg': 'pos'}; reversed args only affects x and y
    assert flipped(3, 2, 'pos') == (2, 3, 'pos')


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
