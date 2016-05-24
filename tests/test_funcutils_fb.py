
import pytest

from boltons.funcutils import wraps


def test_wraps_basic():

    def pita_wrap(flag=False):

        def cedar_dec(func):
            @wraps(func)
            def cedar_wrapper(*a, **kw):
                return (flag, func.func_name, func(*a, **kw))
            return cedar_wrapper

        return cedar_dec

    @pita_wrap(flag=True)
    def simple_func():
        return 'hello'

    assert simple_func() == (True, 'simple_func', 'hello')

    @pita_wrap(flag=False)
    def less_simple_func(arg='hello'):
        return arg

    assert less_simple_func() == (False, 'less_simple_func', 'hello')
    assert less_simple_func(arg='bye') == (False, 'less_simple_func', 'bye')

    with pytest.raises(TypeError):
        simple_func(no_such_arg='nope')

    return
