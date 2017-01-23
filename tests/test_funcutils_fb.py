import pytest

from boltons.funcutils import wraps, FunctionBuilder


def pita_wrap(flag=False):

    def cedar_dec(func):
        @wraps(func)
        def cedar_wrapper(*a, **kw):
            return (flag, func.__name__, func(*a, **kw))
        return cedar_wrapper

    return cedar_dec


def wrappable_func(a, b):
    return a, b


def wrappable_varkw_func(a, b, **kw):
    return a, b


def test_wraps_basic():

    @pita_wrap(flag=True)
    def simple_func():
        "my doc string"
        return 'hello'

    assert simple_func() == (True, 'simple_func', 'hello')
    assert simple_func.__doc__ == "my doc string"

    assert callable(simple_func.__wrapped__)
    assert simple_func.__wrapped__() == 'hello'
    assert simple_func.__wrapped__.__doc__ == "my doc string"

    @pita_wrap(flag=False)
    def less_simple_func(arg='hello'):
        return arg

    assert less_simple_func() == (False, 'less_simple_func', 'hello')
    assert less_simple_func(arg='bye') == (False, 'less_simple_func', 'bye')

    with pytest.raises(TypeError):
        simple_func(no_such_arg='nope')

    @pita_wrap(flag=False)
    def default_non_roundtrippable_repr(x=lambda y: y + 1):
        return x(1)

    assert default_non_roundtrippable_repr() == (
        False, 'default_non_roundtrippable_repr', 2)


def test_wraps_injected():
    def inject_string(func):
        @wraps(func, injected="a")
        def wrapped(*args, **kwargs):
            return func(1, *args, **kwargs)
        return wrapped

    assert inject_string(wrappable_func)(2) == (1, 2)

    def inject_list(func):
        @wraps(func, injected=["b"])
        def wrapped(a, *args, **kwargs):
            return func(a, 2, *args, **kwargs)
        return wrapped

    assert inject_list(wrappable_func)(1) == (1, 2)

    def inject_nonexistent_arg(func):
        @wraps(func, injected=["X"])
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped

    with pytest.raises(ValueError):
        inject_nonexistent_arg(wrappable_func)

    def inject_missing_argument(func):
        @wraps(func, injected="c")
        def wrapped(*args, **kwargs):
            return func(1, *args, **kwargs)
        return wrapped

    def inject_misc_argument(func):
        # inject_to_varkw is default True, just being explicit
        @wraps(func, injected="c", inject_to_varkw=True)
        def wrapped(*args, **kwargs):
            return func(c=1, *args, **kwargs)
        return wrapped

    assert inject_misc_argument(wrappable_varkw_func)(1, 2) == (1, 2)

    def inject_misc_argument_no_varkw(func):
        @wraps(func, injected="c", inject_to_varkw=False)
        def wrapped(*args, **kwargs):
            return func(c=1, *args, **kwargs)
        return wrapped

    with pytest.raises(ValueError):
        inject_misc_argument_no_varkw(wrappable_varkw_func)


def test_wraps_update_dict():

    def updated_dict(func):
        @wraps(func, update_dict=True)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped

    def f(a, b):
        return a, b

    f.something = True

    assert getattr(updated_dict(f), 'something')


def test_wraps_unknown_args():

    def fails(func):
        @wraps(func, foo="bar")
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped

    with pytest.raises(TypeError):
        fails(wrappable_func)


def test_FunctionBuilder_invalid_args():
    with pytest.raises(TypeError):
        FunctionBuilder(name="fails", foo="bar")


def test_FunctionBuilder_invalid_body():
    with pytest.raises(SyntaxError):
        FunctionBuilder(name="fails", body="*").get_func()


def test_FunctionBuilder_modify():
    fb = FunctionBuilder('return_five', doc='returns the integer 5',
                         body='return 5')
    f = fb.get_func()
    assert f() == 5

    fb.varkw = 'kw'
    f_kw = fb.get_func()
    assert f_kw(ignored_arg='ignored_val') == 5


def test_wraps_wrappers():
    call_list = []

    def call_list_appender(func):
        @wraps(func)
        def appender(*a, **kw):
            call_list.append((a, kw))
            return func(*a, **kw)
        return appender

    with pytest.raises(TypeError):
        class Num(object):
            def __init__(self, num):
                self.num = num

            @call_list_appender
            @classmethod
            def added(cls, x, y=1):
                return cls(x + y)

    return
