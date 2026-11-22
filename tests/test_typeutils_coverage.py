import pytest

from boltons.typeutils import (
    classproperty,
    get_all_subclasses,
    issubclass,
    make_sentinel,
)

NOT_SET = make_sentinel('not_set', var_name='NOT_SET')


def test_sentinel_repr_without_var_name():
    sentinel = make_sentinel('TEST')
    assert repr(sentinel) == "Sentinel('TEST')"


def test_sentinel_repr_with_var_name():
    assert repr(NOT_SET) == 'NOT_SET'


def test_pickleable_sentinel_requires_top_level_module():
    fake_globals = {'__name__': 'boltons._missing_typeutils_sentinel_mod'}
    with pytest.raises(ValueError, match='top-level module scopes'):
        exec(
            "make_sentinel('X', var_name='X')",
            fake_globals,
            {'make_sentinel': make_sentinel},
        )


def test_issubclass_non_type_arguments():
    assert issubclass(str, object) is True
    assert issubclass('hi', 'friend') is False
    assert issubclass(object, 'not_a_class') is False
    assert issubclass(42, object) is False


def test_get_all_subclasses_invalid_input():
    with pytest.raises(TypeError, match='expected type object'):
        get_all_subclasses(object())
    with pytest.raises(TypeError, match='expected type object'):
        get_all_subclasses('not_a_type')


def test_get_all_subclasses_diamond_inheritance():
    class A:
        pass

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    names = [t.__name__ for t in get_all_subclasses(A)]
    assert names.count('D') == 1
    assert set(names) == {'B', 'C', 'D'}


def test_classproperty():
    class Widget:
        @classproperty
        def kind(cls):
            return cls.__name__

    assert Widget.kind == 'Widget'
    assert Widget().kind == 'Widget'
