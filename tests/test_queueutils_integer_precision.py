import pytest

from boltons.queueutils import HeapPriorityQueue, SortedPriorityQueue


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
@pytest.mark.parametrize('base', [2 ** 53, 10 ** 100, -(2 ** 53) - 2, 10 ** 1000],
                         ids=['float-boundary', 'large', 'negative', 'overflow'])
def test_adjacent_integer_priorities_remain_distinct(queue_type, base):
    queue = queue_type()
    queue.add('lower', base)
    queue.add('higher', base + 1)
    assert queue.peek() == 'higher'
    assert queue.pop() == 'higher'
    assert queue.pop() == 'lower'


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
def test_integer_priority_replacement_and_ties(queue_type):
    queue = queue_type()
    queue.add('first', 2 ** 53)
    queue.add('second', 2 ** 53)
    queue.add('promoted', 0)
    queue.add('promoted', 2 ** 53 + 1)
    assert [queue.pop(), queue.pop(), queue.pop()] == ['promoted', 'first', 'second']


@pytest.mark.parametrize('queue_type', [HeapPriorityQueue, SortedPriorityQueue])
def test_existing_priority_conversion_and_custom_key(queue_type):
    queue = queue_type()
    queue.add('default')
    queue.add('numeric string', '2.5')
    queue.add('float', 1.5)
    assert [queue.pop(), queue.pop(), queue.pop()] == ['numeric string', 'float', 'default']
    queue = queue_type(priority_key=lambda value: value)
    queue.add('small', 1)
    queue.add('large', 2)
    assert queue.pop() == 'small'
