import pytest

from boltons.listutils import BarrelList


class FalseIterable:
    def __iter__(self):
        return iter([1, 2, 3])

    def __bool__(self):
        return False


class AmbiguousIterable(FalseIterable):
    def __bool__(self):
        raise ValueError("truth value is ambiguous")


@pytest.mark.parametrize("factory", [FalseIterable, AmbiguousIterable])
def test_constructor_does_not_truth_test_iterables(factory):
    assert list(BarrelList(factory())) == list(factory())


@pytest.mark.parametrize("value", [None, [], (), iter(())])
def test_empty_constructor_inputs(value):
    assert list(BarrelList(value)) == []


def test_false_noniterable_is_rejected():
    with pytest.raises(TypeError):
        BarrelList(0)
