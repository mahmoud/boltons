# -*- coding: utf-8 -*-

from heapq import heappush, heappop
from bisect import insort
import itertools

try:
    from compat import make_sentinel
    _REMOVED = make_sentinel(var_name='_REMOVED')
except ImportError:
    _REMOVED = object()

try:
    from listutils import BList
    # see BarrelList docstring for notes
except ImportError:
    BList = list


__all__ = ['PriorityQueue', 'HeapPriorityQueue', 'SortedPriorityQueue']


# TODO: make Base a real abstract class
# TODO: add uniqueification


class BasePriorityQueue(object):
    # negating priority means larger numbers = higher priority
    _default_priority_key = staticmethod(lambda p: -int(p or 0))
    _backend_type = list

    def __init__(self, **kw):
        self._pq = self._backend_type()
        self._entry_map = {}
        self._counter = itertools.count()
        self._get_priority = kw.pop('priority_key', self._default_priority_key)

    @staticmethod
    def _push_entry(backend, entry):
        pass  # abstract

    @staticmethod
    def _pop_entry(backend):
        pass  # abstract

    def add(self, task, priority=None):
        priority = self._get_priority(priority)
        if task in self._entry_map:
            self.remove(task)
        count = next(self._counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        self._push_entry(self._pq, entry)

    def remove(self, task):
        entry = self._entry_map.pop(task)
        entry[-1] = _REMOVED

    def _cull(self, raise_exc=True):
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                self._pop_entry(self._pq)
                continue
            return
        if raise_exc:
            raise IndexError('empty priority queue')

    def peek(self, default=_REMOVED):
        try:
            self._cull()
            _, _, task = self._pq[0]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('peek on empty queue')
        return task

    def pop(self, default=_REMOVED):
        try:
            self._cull()
            _, _, task = self._pop_entry(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def __len__(self):
        return len(self._entry_map)


class HeapPriorityQueue(BasePriorityQueue):
    @staticmethod
    def _pop_entry(backend):
        return heappop(backend)

    @staticmethod
    def _push_entry(backend, entry):
        heappush(backend, entry)


class SortedPriorityQueue(BasePriorityQueue):
    _backend_type = BList

    @staticmethod
    def _pop_entry(backend):
        return backend.pop(0)

    @staticmethod
    def _push_entry(backend, entry):
        insort(backend, entry)


PriorityQueue = SortedPriorityQueue

# tests


def main():
    pq = PriorityQueue()
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
    import pdb;pdb.set_trace()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
