import asyncio
import functools

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
        '''"""a tricky docstring"""'''
        return 'hello'

    assert simple_func() == (True, 'simple_func', 'hello')
    assert simple_func.__doc__ == '''"""a tricky docstring"""'''

    assert callable(simple_func.__wrapped__)
    assert simple_func.__wrapped__() == 'hello'
    assert simple_func.__wrapped__.__doc__ == '''"""a tricky docstring"""'''

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
        class Num:
            def __init__(self, num):
                self.num = num

            @call_list_appender
            @classmethod
            def added(cls, x, y=1):
                return cls(x + y)

    return


def test_FunctionBuilder_add_arg():
    fb = FunctionBuilder('return_five', doc='returns the integer 5',
                         body='return 5')
    f = fb.get_func()
    assert f() == 5

    fb.add_arg('val')
    f = fb.get_func()
    assert f(val='ignored') == 5

    with pytest.raises(ValueError) as excinfo:
        fb.add_arg('val')
    excinfo.typename == 'ExistingArgument'

    fb = FunctionBuilder('return_val', doc='returns the value',
                         body='return val')

    broken_func = fb.get_func()
    with pytest.raises(NameError):
        broken_func()

    fb.add_arg('val', default='default_val')

    better_func = fb.get_func()
    assert better_func() == 'default_val'

    assert better_func('positional') == 'positional'
    assert better_func(val='keyword') == 'keyword'


def test_wraps_expected():
    def expect_string(func):
        @wraps(func, expected="c")
        def wrapped(*args, **kwargs):
            args, c = args[:2], args[-1]
            return func(*args, **kwargs) + (c,)
        return wrapped

    expected_string = expect_string(wrappable_func)
    assert expected_string(1, 2, 3) == (1, 2, 3)

    with pytest.raises(TypeError) as excinfo:
        expected_string(1, 2)

    # a rough way of making sure we got the kind of error we expected
    assert 'argument' in repr(excinfo.value)

    def expect_list(func):
        @wraps(func, expected=["c"])
        def wrapped(*args, **kwargs):
            args, c = args[:2], args[-1]
            return func(*args, **kwargs) + (c,)
        return wrapped

    assert expect_list(wrappable_func)(1, 2, c=4) == (1, 2, 4)

    def expect_pair(func):
        @wraps(func, expected=[('c', 5)])
        def wrapped(*args, **kwargs):
            c = kwargs.pop('c')
            return func(*args, **kwargs) + (c,)
        return wrapped

    assert expect_pair(wrappable_func)(1, 2) == (1, 2, 5)

    def expect_dict(func):
        @wraps(func, expected={'c': 6})
        def wrapped(*args, **kwargs):
            c = kwargs.pop('c')
            return func(*args, **kwargs) + (c,)
        return wrapped

    assert expect_dict(wrappable_func)(1, 2) == (1, 2, 6)


def test_defaults_dict():
    def example(req, test='default'):
        return req

    fb_example = FunctionBuilder.from_func(example)
    assert 'test' in fb_example.args
    dd = fb_example.get_defaults_dict()
    assert dd['test'] == 'default'
    assert 'req' not in dd


def test_get_arg_names():
    def example(req, test='default'):
        return req

    fb_example = FunctionBuilder.from_func(example)
    assert 'test' in fb_example.args
    assert fb_example.get_arg_names() == ('req', 'test')
    assert fb_example.get_arg_names(only_required=True) == ('req',)


def test_from_func_copies_body():
    # the example from #301
    def foo(a, b=2):
        return a / b

    fb = FunctionBuilder.from_func(foo)
    assert fb.body == 'return a / b'

    f = fb.get_func()
    assert f(20) == foo(20) == 10.0
    assert f(20, b=4) == foo(20, b=4) == 5.0


def test_from_func_body_multiline_signature():
    def multi(a,
              b=5):
        total = a + b
        return total * 2

    f = FunctionBuilder.from_func(multi).get_func()
    assert f(1) == multi(1) == 12
    assert f(1, b=1) == multi(1, b=1) == 4


def test_from_func_body_oneline():
    def one(x): return x + 1

    f = FunctionBuilder.from_func(one).get_func()
    assert f(1) == one(1) == 2


def test_from_func_body_oneline_non_ascii():
    # ast col_offsets count UTF-8 bytes, not characters, so a
    # non-ASCII parameter name must not throw off the extraction
    def uni(é): return é

    fb = FunctionBuilder.from_func(uni)
    assert fb.body == 'return é'
    assert fb.get_func()(3) == 3


def test_from_func_body_docstring_and_branches():
    def branchy(x):
        """Docstring."""
        if x > 0:
            return 'pos'
        return 'neg'

    f = FunctionBuilder.from_func(branchy).get_func()
    assert f(1) == 'pos'
    assert f(-1) == 'neg'
    assert f.__doc__ == 'Docstring.'


def test_from_func_body_async():
    async def afunc(x):
        return x + 10

    fb = FunctionBuilder.from_func(afunc)
    assert fb.is_async
    assert fb.body == 'return x + 10'
    assert asyncio.run(fb.get_func()(5)) == 15


def test_from_func_body_partial():
    # the signature generated for a partial does not line up with
    # the wrapped function's parameters, so the body is not copied
    # and the builder keeps the previous default body
    def base(a, b=2):
        return a / b

    fb = FunctionBuilder.from_func(functools.partial(base, 10))
    assert fb.body == 'pass'
    assert fb.get_func()(4) is None


def test_from_func_body_multiline_string():
    # the continuation line of the string literal is unindented, and
    # must not throw off the dedentation of the rest of the body
    def with_str(x):
        s = """line1
line2"""
        return s + str(x)

    fb = FunctionBuilder.from_func(with_str)
    assert fb.body == 's = """line1\nline2"""\nreturn s + str(x)'

    f = fb.get_func()
    assert f(9) == with_str(9)


def test_from_func_no_source_falls_back():
    # functions defined via exec have no retrievable source, so the
    # builder keeps the previous default body
    namespace = {}
    exec("def dyn(x):\n    return x - 1\n", namespace)
    fb = FunctionBuilder.from_func(namespace['dyn'])
    assert fb.body == 'pass'


def test_from_func_lambda_falls_back():
    # lambdas have no def statement to extract a body from, so the
    # builder keeps the previous default body
    fb = FunctionBuilder.from_func(lambda x: x + 1)
    assert fb.body == 'pass'
    assert callable(fb.get_func())


def test_from_func_closure_falls_back():
    # free variables cannot be captured from source alone, so the
    # builder keeps the previous default body
    def outer():
        factor = 3

        def inner(x):
            return x * factor
        return inner

    fb = FunctionBuilder.from_func(outer())
    assert fb.body == 'pass'


def test_from_func_nonlocal_falls_back():
    def outer():
        count = 0

        def inc():
            nonlocal count
            count += 1
            return count
        return inc

    fb = FunctionBuilder.from_func(outer())
    assert fb.body == 'pass'


def test_from_func_zero_arg_super_falls_back():
    # zero-argument super() relies on the implicit __class__ cell,
    # which is a free variable, so such methods fall back as well
    class A:
        def who(self):
            return 'A'

    class B(A):
        def who(self):
            return 'B>' + super().who()

    fb = FunctionBuilder.from_func(B().who)
    assert fb.body == 'pass'


@pytest.mark.parametrize(
    "args, varargs, varkw, defaults, invocation_str, sig_str",
    [
        (["a", "b"], None, None, None, "a, b", "(a, b)"),
        (None, "args", "kwargs", None, "*args, **kwargs", "(*args, **kwargs)"),
        ("a", None, None, dict(a="a"), "a=a", "(a)"),
    ],
)
def test_get_invocation_sig_str(
    args, varargs, varkw, defaults, invocation_str, sig_str
):
    fb = FunctionBuilder(
        name='return_five',
        body='return 5',
        args=args,
        varargs=varargs,
        varkw=varkw,
        defaults=defaults
    )

    assert fb.get_invocation_str() == invocation_str
    assert fb.get_sig_str() == sig_str
