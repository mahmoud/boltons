import pytest

from boltons.listutils import BarrelList


@pytest.mark.parametrize('size', [0, 1, 6])
@pytest.mark.parametrize('step', [10**100, -10**100])
@pytest.mark.parametrize('start, stop', [(None, None), (1, 5), (-2, None)])
def test_large_slice_stride_matches_list(size, step, start, stop):
    values = list(range(size))
    actual = BarrelList(values)
    bounds = slice(start, stop, step)
    assert list(actual[bounds]) == values[bounds]
    assert list(actual.iter_slice(start, stop, step)) == values[bounds]


def test_large_stride_across_barrels():
    actual = BarrelList(range(6))
    actual.lists = [[0, 1], [2, 3], [4, 5]]
    assert list(actual[::10**100]) == [0]
    assert list(actual[::-10**100]) == [5]


def test_zero_stride_still_raises():
    with pytest.raises(ValueError, match='slice step cannot be zero'):
        BarrelList(range(6))[::0]
