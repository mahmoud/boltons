
"""Utilities for working with terminals.
This supplements the stdlib module `termios`, and is only available for posix platforms.
"""

import fcntl
import signal
import struct
import sys
import termios

__ALL__ = ['TermAttrs', 'termsize']


class TermAttrs(object):
    def __init__(self, attrs, fd=None, when=termios.TCSANOW):
        """A context manager for changing terminal attrs.
        fd defaults to stdin.
        attrs must be a 7-element iterable as taken by tcsetattr.

        Note: context manager is not reenterant wrt the same instance.
        """
        self.attrs = attrs
        self.fd = fd if fd is not None else sys.stdin.fileno()
        self.when = when

    @classmethod
    def modify(cls, include=(0,0,0,0), exclude=(0,0,0,0), fd=None, *args, **kwargs):
        """Alternate creation function, allowing you to base changes off current term attrs.
        include and exclude should be 4-tuples of (iflag, oflag, cflag, lflag).
        All values in include will be set.
        All values in exclude will be unset.
        All other values will be unchanged from current values.
        Other args are passed though to TermAttrs.__init__
        """
        if fd is None: fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        for index, (i, e) in enumerate(zip(include, exclude)):
            attrs[index] |= i
            attrs[index] &= ~e
        return TermAttrs(attrs, fd, *args, **kwargs)

    @classmethod
    def raw(cls, *args, **kwargs):
        """Shortcut method for specifying attrs for "raw mode" (see termios(3))"""
        t = termios
        return cls.modify(
            (0, 0, t.CS8, 0),
            (t.IGNBRK|t.BRKINT|t.PARMRK|t.ISTRIP|t.INLCR|t.IGNCR|t.IGNNL|t.IXON,
             t.OPOST,
             t.CSIZE|t.PARENB,
             t.ECHO|t.ECHONL|t.ICANON|t.ISIG|t.IEXTEN),
        *args, **kwargs)

    def __enter__(self):
        self.oldattrs = termios.tcgetattr(self.fd)
        termios.tcsetattr(self.fd, self.when, self.attrs)

    def __exit__(self, *exc_info):
        termios.tcsetattr(self.fd, self.when, self.oldattrs)


_size_cache = None
def termsize(cache=True):
    """Returns the size (columns, rows) of the terminal associated with sys.stdout.
    Note that this function will set up a SIGWINCH handler on first run.
    This should be harmless, since it will call any handler that was already registered.
    Under normal circumstances, the function will only actually fetch the size on first run
    or SIGWINCH. To override this behaviour and force it to refresh the data, pass cache=False.
    """
    old_handler = None

    def get_termsize():
        winsize_t = 'HHHH'
        winsize = struct.pack(winsize_t, 0, 0, 0, 0)
        winsize = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, winsize)
        rows, columns, _, _ = struct.unpack(winsize_t, winsize)
        global _size_cache
        _size_cache = columns, rows

    def termsize_handler(frame, signal):
        get_termsize()
        if old_handler is not None and callable(old_handler):
            old_handler()

    if _size_cache is None:
        old_handler = signal.signal(signal.SIGWINCH, termsize_handler)

    if not cache or _size_cache is None:
        get_termsize()

    return _size_cache

