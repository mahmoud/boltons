
import inspect
from collections import defaultdict

import pytest

from boltons.funcutils import wraps, FunctionBuilder


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


@pytest.mark.parametrize('signature,should_match',
                         [('a, *, b', True),
                          ('a,*,b', True),
                          ('a, * , b', True),
                          ('a, *,\nb', True),
                          ('a, *\n,b', True),
                          ('a, b', False),
                          ('a, *args', False),
                          ('a, *args, **kwargs', False),
                          ('*args', False),
                          ('*args, **kwargs', False)])
def test_FunctionBuilder_KWONLY_MARKER(signature, should_match):
    """
    _KWONLY_MARKER matches the keyword-only argument separator,
    regardless of whitespace.

    Note: it assumes the signature is valid Python.
    """
    matched = bool(FunctionBuilder._KWONLY_MARKER.search(signature))
    message = "{!r}: should_match was {}, but result was {}".format(
        signature, should_match, matched)
    assert bool(matched) == should_match, message


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
