import pytest

from boltons.mathutils import Bits


class Index:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


class IntSubclass(int):
    pass


@pytest.mark.parametrize('length', [
    0, 1, 2, 10, False, True, Index(0), Index(2), IntSubclass(2),
])
def test_explicit_length_accepts_integer_protocol(length):
    expected = length.__index__()
    bits = Bits(0, length)
    assert len(bits) == expected
    assert bits.as_bin() == '0' * expected


@pytest.mark.parametrize('length', [2.0, 2.5, '2', [], None])
def test_invalid_explicit_lengths(length):
    if length is None:
        assert Bits(0, length).as_bin() == '0'
    else:
        with pytest.raises(TypeError):
            Bits(0, length)


@pytest.mark.parametrize('length', [Index(-1), IntSubclass(-1), -1])
def test_negative_integer_lengths(length):
    with pytest.raises(ValueError):
        Bits(0, length)


@pytest.mark.parametrize('index', [
    0, 1, 2, -1, -3, False, True, Index(0), Index(-1), IntSubclass(1),
])
def test_item_indices_match_lists(index):
    bits = Bits('101')
    assert bits[index] is [True, False, True][index]


@pytest.mark.parametrize('index', [3, -4, Index(3), Index(-4)])
def test_out_of_range_item_indices(index):
    with pytest.raises(IndexError):
        Bits('101')[index]


@pytest.mark.parametrize('index', [1.0, '1', [], Index(1.5)])
def test_invalid_item_indices(index):
    with pytest.raises(TypeError):
        Bits('101')[index]


@pytest.mark.parametrize('index', [
    slice(None), slice(None, None, -1), slice(Index(1), None),
])
def test_slicing_keeps_binary_string_semantics(index):
    assert Bits('101')[index].as_bin() == '101'[index]
