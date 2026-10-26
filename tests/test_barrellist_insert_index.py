import pytest

from boltons.listutils import BarrelList


class Index:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


@pytest.mark.parametrize("partitioned", [False, True])
@pytest.mark.parametrize("index", [-100, -1, 0, 2, 4, 100])
def test_insert_accepts_index_protocol(partitioned, index):
    expected = [1, 2, 3, 4]
    actual = BarrelList(expected)
    if partitioned:
        actual.lists = [[1, 2], [3, 4]]
    expected.insert(Index(index), "new")
    actual.insert(Index(index), "new")
    assert list(actual) == expected


@pytest.mark.parametrize("partitioned", [False, True])
def test_insert_rejects_noninteger_without_mutation(partitioned):
    actual = BarrelList([1, 2, 3, 4])
    if partitioned:
        actual.lists = [[1, 2], [3, 4]]
    with pytest.raises(TypeError):
        actual.insert(1.5, "new")
    assert list(actual) == [1, 2, 3, 4]
