from boltons.funcutils import wraps, FunctionBuilder

import pytest


def pita_wrap(flag=False):

    def cedar_dec(func):
        @wraps(func)
        def cedar_wrapper(*a, **kw):
            return (flag, func.__name__, func(*a, **kw))
        return cedar_wrapper

    return cedar_dec


def test_wraps_py3():

    @pita_wrap(flag=True)
    def annotations(a: int, b: float=1) -> "tuple":
        return a, b

    annotations(0) == (True, "annotations", (0, 1))
    annotations.__annotations__ == {'a': int, 'b': float,
                                    'return': 'tuple'}

    @pita_wrap(flag=False)
    def kwonly_arg(a, *, b, c=2):
        return a, b, c

    with pytest.raises(TypeError):
        kwonly_arg(0)

    kwonly_arg(0, b=1) == (False, "kwonly_arg", (0, 1, 2))
    kwonly_arg(0, b=1, c=3) == (False, "kwonly_arg", (0, 1, 3))

    @pita_wrap(flag=True)
    def kwonly_non_roundtrippable_repr(*, x=lambda y: y + 1):
        return x(1)

    assert kwonly_non_roundtrippable_repr() == (
        True, 'kwonly_non_roundtrippable_repr', 2)


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
