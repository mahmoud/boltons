import pytest

from boltons.queueutils import SortedPriorityQueue, HeapPriorityQueue


def _test_priority_queue(queue_type):
    pq = queue_type()
    item1 = 'a'
    item2 = 'b'
    item3 = 'c'
    pq.add(item1)
    pq.remove(item1)

    # integer priorities
    pq.add(item1, 2)
    pq.add(item2, 9)
    pq.add(item3, 7)
    assert len(pq) == 3
    assert item2 == pq.pop()
    assert len(pq) == 2
    assert item3 == pq.pop()
    assert len(pq) == 1
    assert item1 == pq.pop()
    assert len(pq) == 0

    # float priorities
    pq.add(item1, 0.2)
    pq.add(item2, 0.9)
    pq.add(item3, 0.7)
    assert len(pq) == 3
    assert item2 == pq.pop()
    assert len(pq) == 2
    assert item3 == pq.pop()
    assert len(pq) == 1
    assert item1 == pq.pop()
    assert len(pq) == 0

    try:
        pq.pop()
    except IndexError:
        pass
    else:
        assert False, 'priority queue should be empty'
    return


def test_heap_queue():
    _test_priority_queue(HeapPriorityQueue)


def test_sorted_queue():
    _test_priority_queue(SortedPriorityQueue)


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
@pytest.mark.parametrize('old_priority,new_priority', [(1, 3), (3, 1)])
def test_priority_update(queue_type, old_priority, new_priority):
    pq = queue_type()
    pq.add('updated', old_priority)
    pq.add('unchanged', 2)
    pq.add('updated', new_priority)

    assert len(pq) == 2
    expected = ['updated', 'unchanged'] if new_priority > 2 else ['unchanged', 'updated']
    assert pq.peek() == expected[0]
    assert len(pq) == 2
    assert [pq.pop(), pq.pop()] == expected
    assert len(pq) == 0
    assert pq.pop(None) is None


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
def test_equal_priorities_preserve_insertion_order(queue_type):
    pq = queue_type()
    tasks = [object(), object(), object()]
    for task in tasks:
        pq.add(task, 1)

    assert pq.peek() is tasks[0]
    assert [pq.pop(), pq.pop(), pq.pop()] == tasks


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
def test_remove_and_readd(queue_type):
    pq = queue_type()
    pq.add('removed', 3)
    pq.add('remaining', 2)
    pq.remove('removed')

    assert len(pq) == 1
    assert pq.peek() == 'remaining'
    pq.add('removed', 1)
    assert len(pq) == 2
    assert [pq.pop(), pq.pop()] == ['remaining', 'removed']
    assert len(pq) == 0


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
@pytest.mark.parametrize('method', ['peek', 'pop'])
def test_removed_only_queue(queue_type, method):
    pq = queue_type()
    pq.add('removed')
    pq.remove('removed')
    read = getattr(pq, method)
    default = object()

    assert len(pq) == 0
    assert read(default) is default
    assert len(pq) == 0
    with pytest.raises(IndexError):
        read()
