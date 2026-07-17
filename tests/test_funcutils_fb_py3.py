import time
import sys
import inspect
import functools
from collections import defaultdict

import pytest

from boltons.funcutils import wraps, FunctionBuilder, update_wrapper, copy_function
import boltons.funcutils as funcutils


def wrappable_func(a, b):
    return a, b


def wrappable_varkw_func(a, b, **kw):
    return a, b


def pita_wrap(flag=False):

    def cedar_dec(func):
        @wraps(func)
        def cedar_wrapper(*a, **kw):
            return (flag, func.__name__, func(*a, **kw))
        return cedar_wrapper

    return cedar_dec


def test_wraps_py3():

    @pita_wrap(flag=True)
    def annotations(a: int, b: float=1, c: defaultdict=()) -> defaultdict:
        return a, b, c

    assert annotations(0) == (True, "annotations", (0, 1, ()))
    assert annotations.__annotations__ == {'a': int, 'b': float,
                                           'c': defaultdict,
                                           'return': defaultdict}

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

    assert kwonly_non_roundtrippable_repr() == (
        True, 'kwonly_non_roundtrippable_repr', 2)


def test_copy_function_kw_defaults_py3():
    # test that the copy works with keyword-only defaults
    f = lambda x, *, y=2: x * y
    f_copy = copy_function(f)
    assert f(21) == f_copy(21) == 42


@pytest.mark.parametrize('partial_kind', (functools, funcutils))
def test_update_wrapper_partial(partial_kind):
    wrapper = partial_kind.partial(wrappable_varkw_func, b=1)

    fully_wrapped = update_wrapper(wrapper, wrappable_varkw_func)
    assert fully_wrapped(1) == (1, 1)


def test_remove_kwonly_arg():
    # example adapted from https://github.com/mahmoud/boltons/issues/123

    def darkhelm_inject_loop(func):
        sig = inspect.signature(func)
        loop_param = sig.parameters['loop'].replace(default=None)
        sig = sig.replace(parameters=[loop_param])

        def add_loop(args, kwargs):
            bargs = sig.bind(*args, **kwargs)
            bargs.apply_defaults()
            if bargs.arguments['loop'] is None:
                bargs.arguments['loop'] = "don't look at me, I just use gevent"

            return bargs.arguments

        def wrapper(*args, **kwargs):
            return func(**add_loop(args, kwargs))

        return wraps(func, injected=['loop'])(wrapper)

    @darkhelm_inject_loop
    def example(test='default', *, loop='lol'):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert 'test' in fb_example.args
    assert fb_example.get_defaults_dict()['test'] == 'default'

    assert 'loop' not in fb_example.kwonlyargs
    assert 'loop' not in fb_example.kwonlydefaults


def test_defaults_dict():
    def example(req, test='default', *, loop='lol'):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert 'test' in fb_example.args
    dd = fb_example.get_defaults_dict()
    assert dd['test'] == 'default'
    assert dd['loop'] == 'lol'
    assert 'req' not in dd


def test_get_arg_names():
    def example(req, test='default', *, loop='lol'):
        return loop

    fb_example = FunctionBuilder.from_func(example)
    assert 'test' in fb_example.args
    assert fb_example.get_arg_names() == ('req', 'test', 'loop')
    assert fb_example.get_arg_names(only_required=True) == ('req',)


def test_FunctionBuilder_add_arg_kwonly():
    fb = FunctionBuilder('return_val', doc='returns the value',
                         body='return val')

    broken_func = fb.get_func()
    with pytest.raises(NameError):
        broken_func()

    fb.add_arg('val', default='default_val', kwonly=True)

    better_func = fb.get_func()
    assert better_func() == 'default_val'

    with pytest.raises(ValueError):
        fb.add_arg('val')

    assert better_func(val='keyword') == 'keyword'

    with pytest.raises(TypeError):
        assert better_func('positional')
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

    wraps(g)(f) used to raise a TypeError when f's b was keyword-only,
    because g's defaulted b was forwarded positionally. Defaulted args
    are now forwarded as keywords (with positional-only awareness), so
    the wrapper works in both directions.
    """
    from boltons.funcutils import wraps

    def g(a: float, b=10):
        return a * b

    def f(a: int,  *, b=1):
        return a * b

    # all is well here...
    assert f(3) == 3
    assert g(3) == 30
    assert wraps(f)(g)(3) == 3  # yay, g got the f default (not so with functools.wraps!)

    assert wraps(g)(f)(3) == 30  # g's b=10 is forwarded as a keyword

    return


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
                return (await wrapped(*args, **kw))
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
    new_func = wraps(wrappable_func, injected='b')(lambda a: wrappable_func(a, b=1))
    new_sig = inspect.signature(new_func, follow_wrapped=True)

    assert list(new_sig.parameters.keys()) == ['a', 'b']

    new_func = wraps(wrappable_func, injected='b', hide_wrapped=True)(lambda a: wrappable_func(a, b=1))
    new_sig = inspect.signature(new_func, follow_wrapped=True)

    assert list(new_sig.parameters.keys()) == ['a']

    new_func = wraps(wrappable_func, injected='b')(lambda a: wrappable_func(a, b=1))
    new_new_func = wraps(new_func, injected='a', hide_wrapped=True)(lambda: new_func(a=1))
    new_new_sig = inspect.signature(new_new_func, follow_wrapped=True)

    assert len(new_new_sig.parameters) == 0


def test_wraps_defaulted_arg_keyword_forwarding():
    # issue #343: a defaulted arg passed by keyword must reach the
    # wrapper's **kwargs, not be flattened into *args
    def flip(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*reversed(args), **kwargs)
        return wrapper

    def power(x, y, msg=''):
        return (x, y, msg)

    assert flip(power)(3, 2, msg='abc') == (2, 3, 'abc')
    assert flip(power)(3, 2) == (2, 3, '')


def test_wraps_defaulted_arg_before_varargs():
    # a defaulted arg preceding *varargs must stay positional; forwarding
    # it as a keyword would raise "got multiple values for argument"
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    def func(x, y=1, *rest):
        return (x, y, rest)

    assert deco(func)(1, 2, 3) == (1, 2, (3,))
    assert deco(func)(1) == (1, 1, ())


@pytest.mark.skipif(sys.version_info < (3, 8),
                    reason='positional-only params require 3.8+')
def test_wraps_posonly_defaulted_arg():
    # positional-only params, defaulted or not, are never keyword-forwarded
    ns = {}
    exec('def func(x, y=2, /, z=3):\n    return (x, y, z)', ns)
    func = ns['func']

    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    assert deco(func)(1, 5) == (1, 5, 3)
    assert deco(func)(1, 5, z=7) == (1, 5, 7)
