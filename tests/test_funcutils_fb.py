import functools
import inspect
import time
from collections import defaultdict

import pytest

import boltons.funcutils as funcutils
from boltons.funcutils import FunctionBuilder, copy_function, update_wrapper, wraps


def wrappable_func(a, b):
    return a, b


def test_wraps_async():
    # from https://github.com/mahmoud/boltons/issues/194
    import asyncio

    def delayed(func):
        @wraps(func)
        async def wrapped(*args, **kw):
            await asyncio.sleep(1.0)
            return await func(*args, **kw)

        return wrapped

    async def f():
        await asyncio.sleep(0.1)

    assert asyncio.iscoroutinefunction(f)

    f2 = delayed(f)

    assert asyncio.iscoroutinefunction(f2)

    # from https://github.com/mahmoud/boltons/pull/195
    def yolo():
        def make_time_decorator(wrapped):
            @wraps(wrapped)
            async def decorator(*args, **kw):
                return await wrapped(*args, **kw)

            return decorator

        return make_time_decorator

    @yolo()
    async def foo(x):
        await asyncio.sleep(x)

    start_time = time.monotonic()
    asyncio.run(foo(0.3))
    duration = time.monotonic() - start_time

    # lol windows py37 somehow completes this in under 0.3
    # "assert 0.29700000000002547 > 0.3" https://ci.appveyor.com/project/mahmoud/boltons/builds/22261051/job/3jfq1tq2233csqp6
    assert duration > 0.25


def test_wraps_hide_wrapped():
    new_func = wraps(wrappable_func, injected="b")(lambda a: wrappable_func(a, b=1))
    new_sig = inspect.signature(new_func, follow_wrapped=True)

    assert list(new_sig.parameters.keys()) == ["a", "b"]

    new_func = wraps(wrappable_func, injected="b", hide_wrapped=True)(
        lambda a: wrappable_func(a, b=1)
    )
    new_sig = inspect.signature(new_func, follow_wrapped=True)

    assert list(new_sig.parameters.keys()) == ["a"]

    new_func = wraps(wrappable_func, injected="b")(lambda a: wrappable_func(a, b=1))
    new_new_func = wraps(new_func, injected="a", hide_wrapped=True)(
        lambda: new_func(a=1)
    )
    new_new_sig = inspect.signature(new_new_func, follow_wrapped=True)

    assert len(new_new_sig.parameters) == 0


def wrappable_varkw_func(a, b, **kw):
    return a, b


def pita_wrap(flag=False):
    def cedar_dec(func):
        @wraps(func)
        def cedar_wrapper(*a, **kw):
            return (flag, func.__name__, func(*a, **kw))

        return cedar_wrapper

    return cedar_dec


def test_wraps():
    @pita_wrap(flag=True)
    def annotations(a: int, b: float = 1, c: defaultdict = ()) -> defaultdict:
        return a, b, c

    assert annotations(0) == (True, "annotations", (0, 1, ()))
    assert annotations.__annotations__ == {
        "a": int,
        "b": float,
        "c": defaultdict,
        "return": defaultdict,
    }

    @pita_wrap(flag=False)
    def kwonly_arg(a, *, b, c=2):
        return a, b, c

    with pytest.raises(TypeError):
        kwonly_arg(0)

    assert kwonly_arg(0, b=1) == (False, "kwonly_arg", (0, 1, 2))
    assert kwonly_arg(0, b=1, c=3) == (False, "kwonly_arg", (0, 1, 3))

    @pita_wrap(flag=True)
    def kwonly_non_roundtrippable_repr(*, x=lambda y: y + 1):
        return x(1)

    expected = (True, "kwonly_non_roundtrippable_repr", 2)
    assert kwonly_non_roundtrippable_repr() == expected


def test_copy_function_kw_defaults():
    # test that the copy works with keyword-only defaults
    f = lambda x, *, y=2: x * y
    f_copy = copy_function(f)
    assert f(21) == f_copy(21) == 42


@pytest.mark.parametrize("partial_kind", (functools, funcutils))
def test_update_wrapper_partial(partial_kind):
    wrapper = partial_kind.partial(wrappable_varkw_func, b=1)

    fully_wrapped = update_wrapper(wrapper, wrappable_varkw_func)
    assert fully_wrapped(1) == (1, 1)


def test_remove_kwonly_arg():
    # example adapted from https://github.com/mahmoud/boltons/issues/123

    def darkhelm_inject_loop(func):
        sig = inspect.signature(func)
        loop_param = sig.parameters["loop"].replace(default=None)
        sig = sig.replace(parameters=[loop_param])

        def add_loop(args, kwargs):
            bargs = sig.bind(*args, **kwargs)
            bargs.apply_defaults()
            if bargs.arguments["loop"] is None:
                bargs.arguments["loop"] = "don't look at me, I just use gevent"

            return bargs.arguments

        def wrapper(*args, **kwargs):
            return func(**add_loop(args, kwargs))

        return wraps(func, injected=["loop"])(wrapper)

    @darkhelm_inject_loop
    def example(test="default", *, loop="lol"):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert "test" in fb_example.args
    assert fb_example.get_defaults_dict()["test"] == "default"

    assert "loop" not in fb_example.kwonlyargs
    assert "loop" not in fb_example.kwonlydefaults


def test_defaults_dict():
    def example(req, test="default", *, loop="lol"):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert "test" in fb_example.args
    dd = fb_example.get_defaults_dict()
    assert dd["test"] == "default"
    assert dd["loop"] == "lol"
    assert "req" not in dd


def test_get_arg_names():
    def example(req, test="default", *, loop="lol"):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert "test" in fb_example.args
    assert fb_example.get_arg_names() == ("req", "test", "loop")
    assert fb_example.get_arg_names(only_required=True) == ("req",)


@pytest.mark.parametrize(
    "signature,should_match",
    [
        ("a, *, b", True),
        ("a,*,b", True),
        ("a, * , b", True),
        ("a, *,\nb", True),
        ("a, *\n,b", True),
        ("a, b", False),
        ("a, *args", False),
        ("a, *args, **kwargs", False),
        ("*args", False),
        ("*args, **kwargs", False),
    ],
)
def test_FunctionBuilder_KWONLY_MARKER(signature, should_match):
    """
    _KWONLY_MARKER matches the keyword-only argument separator,
    regardless of whitespace.

    Note: it assumes the signature is valid Python.
    """
    matched = bool(FunctionBuilder._KWONLY_MARKER.search(signature))
    message = "{!r}: should_match was {}, but result was {}".format(
        signature, should_match, matched
    )
    assert bool(matched) == should_match, message


def test_FunctionBuilder_add_arg_kwonly():
    fb = FunctionBuilder("return_val", doc="returns the value", body="return val")

    broken_func = fb.get_func()
    with pytest.raises(NameError):
        broken_func()

    fb.add_arg("val", default="default_val", kwonly=True)

    better_func = fb.get_func()
    assert better_func() == "default_val"

    with pytest.raises(ValueError):
        fb.add_arg("val")

    assert better_func(val="keyword") == "keyword"

    with pytest.raises(TypeError):
        assert better_func("positional")
    return


@pytest.mark.parametrize(
    "args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, invocation_str, sig_str",
    [
        (
            None,
            "args",
            "kwargs",
            None,
            "a",
            dict(a="a"),
            "*args, a=a, **kwargs",
            "(*args, a, **kwargs)",
        )
    ],
)
def test_get_invocation_sig_str(
    args,
    varargs,
    varkw,
    defaults,
    kwonlyargs,
    kwonlydefaults,
    invocation_str,
    sig_str,
):
    fb = FunctionBuilder(
        name="return_five",
        body="return 5",
        args=args,
        varargs=varargs,
        varkw=varkw,
        defaults=defaults,
        kwonlyargs=kwonlyargs,
        kwonlydefaults=kwonlydefaults,
    )

    assert fb.get_invocation_str() == invocation_str
    assert fb.get_sig_str() == sig_str


def test_wraps_inner_kwarg_only():
    """from https://github.com/mahmoud/boltons/issues/261

    mh responds to the issue:

    You'll notice that when kw-only args are involved the first time
    (wraps(f)(g)) it works fine. The other way around, however,
    wraps(g)(f) fails, because by the very nature of funcutils.wraps,
    you're trying to give f the same signature as g. And f's signature
    is not like g's. g supports positional b and f() does not.

    If you want to make a wrapper which converts a keyword-only
    argument to one that can be positional or keyword only, that'll
    require a different approach for now.

    A potential fix would be to pass all function arguments as
    keywords. But doubt that's the right direction, because, while I
    have yet to add positional argument only support, that'll
    definitely throw a wrench into things.
    """

    def g(a: float, b=10):
        return a * b

    def f(a: int, *, b=1):
        return a * b

    # all is well here...
    assert f(3) == 3
    assert g(3) == 30
    assert (
        wraps(f)(g)(3) == 3
    )  # yay, g got the f default (not so with functools.wraps!)

    # but this doesn't work
    with pytest.raises(TypeError):
        wraps(g)(f)(3)


def test_wraps_basic():
    @pita_wrap(flag=True)
    def simple_func():
        '''"""a tricky docstring"""'''
        return "hello"

    assert simple_func() == (True, "simple_func", "hello")
    assert simple_func.__doc__ == '''"""a tricky docstring"""'''

    assert callable(simple_func.__wrapped__)
    assert simple_func.__wrapped__() == "hello"
    assert simple_func.__wrapped__.__doc__ == '''"""a tricky docstring"""'''

    @pita_wrap(flag=False)
    def less_simple_func(arg="hello"):
        return arg

    assert less_simple_func() == (False, "less_simple_func", "hello")
    assert less_simple_func(arg="bye") == (False, "less_simple_func", "bye")

    with pytest.raises(TypeError):
        simple_func(no_such_arg="nope")

    @pita_wrap(flag=False)
    def default_non_roundtrippable_repr(x=lambda y: y + 1):
        return x(1)

    expected = (False, "default_non_roundtrippable_repr", 2)
    assert default_non_roundtrippable_repr() == expected


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

    assert getattr(updated_dict(f), "something")


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


# noinspection PyPep8Naming
def test_FunctionBuilder_invalid_body():
    with pytest.raises(SyntaxError):
        FunctionBuilder(name="fails", body="*").get_func()


def test_FunctionBuilder_modify():
    fb = FunctionBuilder("return_five", doc="returns the integer 5", body="return 5")
    f = fb.get_func()
    assert f() == 5

    fb.varkw = "kw"
    f_kw = fb.get_func()
    assert f_kw(ignored_arg="ignored_val") == 5


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
    fb = FunctionBuilder("return_five", doc="returns the integer 5", body="return 5")
    f = fb.get_func()
    assert f() == 5

    fb.add_arg("val")
    f = fb.get_func()
    assert f(val="ignored") == 5

    with pytest.raises(ValueError) as excinfo:
        fb.add_arg("val")
    assert excinfo.typename == "ExistingArgument"

    fb = FunctionBuilder("return_val", doc="returns the value", body="return val")

    broken_func = fb.get_func()
    with pytest.raises(NameError):
        broken_func()

    fb.add_arg("val", default="default_val")

    better_func = fb.get_func()
    assert better_func() == "default_val"

    assert better_func("positional") == "positional"
    assert better_func(val="keyword") == "keyword"


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
    assert "argument" in repr(excinfo.value)

    def expect_list(func):
        @wraps(func, expected=["c"])
        def wrapped(*args, **kwargs):
            args, c = args[:2], args[-1]
            return func(*args, **kwargs) + (c,)

        return wrapped

    assert expect_list(wrappable_func)(1, 2, c=4) == (1, 2, 4)

    def expect_pair(func):
        @wraps(func, expected=[("c", 5)])
        def wrapped(*args, **kwargs):
            args, c = args[:2], args[-1]
            return func(*args, **kwargs) + (c,)

        return wrapped

    assert expect_pair(wrappable_func)(1, 2) == (1, 2, 5)

    def expect_dict(func):
        @wraps(func, expected={"c": 6})
        def wrapped(*args, **kwargs):
            args, c = args[:2], args[-1]
            return func(*args, **kwargs) + (c,)

        return wrapped

    assert expect_dict(wrappable_func)(1, 2) == (1, 2, 6)


@pytest.mark.parametrize(
    "args, varargs, varkw, defaults, invocation_str, sig_str",
    [
        (["a", "b"], None, None, None, "a, b", "(a, b)"),
        (None, "args", "kwargs", None, "*args, **kwargs", "(*args, **kwargs)"),
        ("a", None, None, dict(a="a"), "a", "(a)"),
    ],
)
def test_get_invocation_sig_str(
    args, varargs, varkw, defaults, invocation_str, sig_str
):
    fb = FunctionBuilder(
        name="return_five",
        body="return 5",
        args=args,
        varargs=varargs,
        varkw=varkw,
        defaults=defaults,
    )

    assert fb.get_invocation_str() == invocation_str
    assert fb.get_sig_str() == sig_str
