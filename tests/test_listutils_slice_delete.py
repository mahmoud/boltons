import pytest

from boltons.listutils import BarrelList


def _make_barrel_list(reference, partitioned):
    value = BarrelList(reference)
    if partitioned:
        # Use the same small sublists as the existing cross-barrel tests.
        value.lists = [reference[i : i + 3] for i in range(0, len(reference), 3)] or [
            []
        ]
    return value


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('size', [0, 1, 12])
@pytest.mark.parametrize(
    'key',
    [
        slice(None),
        slice(None, None, 2),
        slice(1, 9, 2),
        slice(2, 10, 3),
        slice(None, None, -1),
        slice(None, None, -2),
        slice(10, 1, -3),
        slice(8, 2, -1),
        slice(-2, -10, -2),
        slice(1, 9),
        slice(-100, 5),
        slice(3, 100),
        slice(-100, 100),
        slice(100, 200),
        slice(-100, -50),
        slice(9, 2),
        slice(3, 3),
        slice(2, 9, -1),
        slice(-100, None, -2),
        slice(None, 100, -1),
    ],
)
def test_slice_delete_matches_list(key, size, partitioned):
    reference = list(range(size))
    value = _make_barrel_list(reference, partitioned)

    del reference[key]
    del value[key]

    assert list(value) == reference
    assert len(value) == len(reference)
    assert list(reversed(value)) == list(reversed(reference))
    # Deleting every item must leave a usable empty BarrelList.
    value.append('new')
    assert value.pop() == 'new'
    assert list(value) == reference


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize(
    'key, error',
    [
        (slice(None, None, 0), ValueError),
        (slice(None, None, 1.0), TypeError),
        (slice(None, None, 2.0), TypeError),
        (slice(None, None, '2'), TypeError),
        (slice(1.5, None), TypeError),
        (slice(None, 2.5), TypeError),
        (slice(1.5, None, -2), TypeError),
    ],
)
def test_invalid_slice_delete_preserves_contents(key, error, partitioned):
    reference = list(range(12))
    value = _make_barrel_list(reference, partitioned)

    with pytest.raises(error):
        del reference[key]
    with pytest.raises(error):
        del value[key]

    assert list(value) == reference == list(range(12))


class _Index:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('step', [1, 2, -1, -2])
def test_slice_delete_accepts_index_protocol(step, partitioned):
    reference = list(range(12))
    value = _make_barrel_list(reference, partitioned)
    key = slice(_Index(1), _Index(10), _Index(step))

    del reference[key]
    del value[key]

    assert list(value) == reference


@pytest.mark.parametrize('method', ['del_slice', '__delslice__'])
def test_direct_slice_delete(method):
    value = _make_barrel_list(list(range(12)), True)

    assert getattr(value, method)(None, None, -2) is None

    assert list(value) == [0, 2, 4, 6, 8, 10]
