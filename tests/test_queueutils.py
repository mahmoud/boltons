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


def test_integer_priority_precision():
    # Nanosecond timestamps and large counters must not collapse to float ties.
    for queue_type in (HeapPriorityQueue, SortedPriorityQueue):
        for base in (2 ** 53, 10 ** 18, -(10 ** 18)):
            pq = queue_type()
            pq.add('lower', base)
            pq.add('higher', base + 1)
            assert pq.peek() == 'higher'
            assert [pq.pop(), pq.pop()] == ['higher', 'lower']


def test_integer_priority_outside_float_range():
    for queue_type in (HeapPriorityQueue, SortedPriorityQueue):
        pq = queue_type()
        pq.add('low', -(10 ** 400))
        pq.add('high', 10 ** 400)
        assert [pq.pop(), pq.pop()] == ['high', 'low']


def test_mixed_priority_types_and_ties():
    for queue_type in (HeapPriorityQueue, SortedPriorityQueue):
        pq = queue_type()
        for task, priority in [('default', None), ('int', 1),
                               ('float', 1.0), ('text', '1.5'), ('negative', -2)]:
            pq.add(task, priority)
        assert [pq.pop() for _ in range(5)] == [
            'text', 'int', 'float', 'default', 'negative']


def test_update_large_integer_priority():
    for queue_type in (HeapPriorityQueue, SortedPriorityQueue):
        pq = queue_type()
        pq.add('first', 10 ** 18)
        pq.add('second', 10 ** 18 - 1)
        pq.add('second', 10 ** 18 + 1)
        assert len(pq) == 2
        assert [pq.pop(), pq.pop()] == ['second', 'first']
