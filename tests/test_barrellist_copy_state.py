import copy
import pickle

import pytest

from boltons.listutils import BarrelList


class CustomBarrelList(BarrelList):
    pass


COPIERS = [copy.copy, copy.deepcopy] + [
    pytest.param(
        lambda value, protocol=protocol:
        pickle.loads(pickle.dumps(value, protocol)), id='pickle-%s' % protocol)
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1)
]


@pytest.mark.parametrize('clone', COPIERS)
@pytest.mark.parametrize('cls', [BarrelList, CustomBarrelList])
def test_copy_preserves_values_and_instance_attributes(clone, cls):
    item = ['shared']
    values = cls([item, item, 3])
    values.label = 'example'
    values.metadata = {'item': item}
    result = clone(values)

    assert type(result) is cls
    assert result is not values
    assert list(result) == [item, item, 3]
    assert result.label == 'example'
    assert result[0] is result[1]
    assert result.metadata['item'] is result[0]
    if clone is copy.copy:
        assert result[0] is item
        assert result.metadata is values.metadata
    else:
        assert result[0] is not item
        assert result.metadata is not values.metadata
    result.append('new')
    assert len(values) == 3


@pytest.mark.parametrize('clone', COPIERS)
def test_copy_recursive_contents(clone):
    values = BarrelList()
    values.append(values)
    result = clone(values)

    assert result is not values
    assert len(result) == 1
    assert result[0] is (values if clone is copy.copy else result)


@pytest.mark.parametrize('clone', COPIERS)
def test_copy_recursive_attributes(clone):
    values = BarrelList([1])
    values.owner = values
    result = clone(values)

    assert list(result) == [1]
    assert result.owner is (values if clone is copy.copy else result)


@pytest.mark.parametrize('clone', COPIERS)
def test_copy_partitioned_contents(clone):
    values = BarrelList()
    values.lists = [[1, 2], [], [3]]
    result = clone(values)

    assert list(result) == [1, 2, 3]
    result[1] = 9
    result.pop()
    assert list(values) == [1, 2, 3]
    assert list(result) == [1, 9]
