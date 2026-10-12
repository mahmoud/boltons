import pytest

from boltons.listutils import BarrelList


@pytest.mark.parametrize('partitioned', [False, True])
@pytest.mark.parametrize('args', [(None,), ((),), (-1.0,), (0, 1)])
def test_pop_invalid_arguments_leave_contents_unchanged(partitioned, args):
    value = BarrelList([1, 2, 3])
    if partitioned:
        value.lists = [[1], [2, 3]]
    with pytest.raises(TypeError):
        value.pop(*args)
    assert list(value) == [1, 2, 3]


@pytest.mark.parametrize('partitioned', [False, True])
def test_pop_accepts_index_protocol(partitioned):
    class Index:
        def __index__(self):
            return 1

    value = BarrelList([1, 2, 3])
    if partitioned:
        value.lists = [[1], [2, 3]]
    assert value.pop(Index()) == 2
    assert list(value) == [1, 3]
    assert value.pop() == 3
    assert value.pop(-1) == 1
    with pytest.raises(IndexError):
        value.pop()
