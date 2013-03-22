# -*- coding: utf-8 -*-

from heapq import heappush, heappop
import itertools

try:
    from compat import make_sentinel
    _REMOVED = make_sentinel(var_name='_REMOVED')
except ImportError:
    _REMOVED = object()


__all__ = ['PriorityQueue', 'HeapPriorityQueue']


class HeapPriorityQueue(object):
    """
    Real quick type based on the heapq docs.
    """
    def __init__(self):
        self._pq = []
        self._entry_map = {}
        self.counter = itertools.count()

    def add(self, task, priority=None):
        # larger numbers = higher priority
        priority = -int(priority or 0)
        if task in self._entry_map:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self._entry_map[task] = entry
        heappush(self._pq, entry)

    def remove(self, task):
        entry = self._entry_map.pop(task)
        entry[-1] = _REMOVED

    def _cull(self):
        while self._pq:
            priority, count, task = self._pq[0]
            if task is _REMOVED:
                heappop(self._pq)
                continue
            return

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
            _, _, task = heappop(self._pq)
            del self._entry_map[task]
        except IndexError:
            if default is not _REMOVED:
                return default
            raise IndexError('pop on empty queue')
        return task

    def __len__(self):
        return len(self._entry_map)


PriorityQueue = HeapPriorityQueue
