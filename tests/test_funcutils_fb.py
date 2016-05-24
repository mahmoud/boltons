import sys
import textwrap

import pytest

from boltons.funcutils import wraps, FunctionBuilder

IS_PY2 = sys.version_info[0] == 2


def pita_wrap(flag=False):

    def cedar_dec(func):
        @wraps(func)
        def cedar_wrapper(*a, **kw):
            return (flag, func.__name__, func(*a, **kw))
        return cedar_wrapper

    return cedar_dec


def wrappable_func(a, b):
    return a, b


def test_wraps_basic():

    @pita_wrap(flag=True)
    def simple_func():
        "my doc string"
        return 'hello'

    assert simple_func() == (True, 'simple_func', 'hello')
    assert simple_func.__doc__ == "my doc string"

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


def conditional_source(src, names):
    """
    Conditional compilation for Python 3
    """
    code = compile(textwrap.dedent(src), __file__, 'single')
    if IS_PY2:
        exec("exec code in globals(), T")
    else:
        exec_ = __builtins__["exec"]
        exec_(code, globals(), names)


@pytest.mark.skipif(IS_PY2, reason="Contains Python 3-only syntax")
def test_wraps_py3():
    F = {}

    def C(src):
        return conditional_source(src, F)

    C("""
    @pita_wrap(flag=True)
    def annotations(a: int, b: float=1) -> "tuple":
        return a, b
    """)

    assert F['annotations'](0) == (True, "annotations", (0, 1))
    assert F['annotations'].__annotations__ == {'a': int, 'b': float,
                                                'return': 'tuple'}

    C("""
    @pita_wrap(flag=False)
    def kwonly_arg(a, *, b, c=2):
        return a, b, c
    """)

    with pytest.raises(TypeError):
        F['kwonly_arg'](0)

    assert F["kwonly_arg"](0, b=1) == (False, "kwonly_arg", (0, 1, 2))
    assert F["kwonly_arg"](0, b=1, c=3) == (False, "kwonly_arg", (0, 1, 3))

    C("""
    @pita_wrap(flag=True)
    def kwonly_non_roundtrippable_repr(*, x=lambda y: y + 1):
        return x(1)
    """)

    assert F["kwonly_non_roundtrippable_repr"]() == (
        True, 'kwonly_non_roundtrippable_repr', 2)


def test_FunctionBuilder_invalid_args():
    with pytest.raises(TypeError):
        FunctionBuilder(name="fails", foo="bar")


def test_FunctionBuilder_invalid_body():
    with pytest.raises(SyntaxError):
        FunctionBuilder(name="fails", body="*").get_func()
