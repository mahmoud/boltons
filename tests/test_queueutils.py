# -*- coding: utf-8 -*-

from boltons.queueutils import SortedPriorityQueue, HeapPriorityQueue


def _test_priority_queue(queue_type):
    pq = queue_type()
    func = lambda x: x
    pq.add(func)
    pq.remove(func)
    pq.add(func)
    pq.add(func)
    assert len(pq) == 1
    assert func == pq.pop()
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
