"""This module provides useful functions on top of Python's
built-in :mod:`threading` module.
"""
import threading


class TwoWayEvent(threading.Event):
    """A :py:class:`~threading.Event` which can be used to synchronize in both
    the set and clear directions. Use the :py:meth:`.wait_clear` method to wait
    for the event's internal flag to be set to false.
    """
    __slots__ = ('__inverse_event',)
    def __init__(self):
        super(TwoWayEvent, self).__init__()
        self.__inverse_event = threading.Event()
        self.__inverse_event.set()

    def __repr__(self):
        return "<{0} is_set={1!r} >".format(self.__class__.__name__, self.is_set())

    def clear(self):
        super(TwoWayEvent, self).clear()
        self.__inverse_event.set()

    def is_clear(self):
        return self.__inverse_event.is_set()

    def set(self):
        self.__inverse_event.clear()
        super(TwoWayEvent, self).set()

    def wait(self, timeout=None):
        super(TwoWayEvent, self).wait(timeout=timeout)

    def wait_clear(self, timeout=None):
        """Block until the internal flag is false. If the internal flag is false
        on entry, return immediately. Otherwise, block until another thread
        calls :py:meth:`.clear` to set the flag to false, or until the optional
        timeout occurs.

        The timeout and return values are the same as those of :py:meth:`wait`.
        """
        self.__inverse_event.wait(timeout=timeout)
