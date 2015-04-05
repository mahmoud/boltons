# -*- coding: utf-8 -*-
"""
A small set of utilities useful for debugging misbehaving
applications. Currently this focuses on ways to use :mod:`pdb`, the
built-in Python debugger.
"""

__all__ = ['pdb_on_signal', 'pdb_on_exception']


def pdb_on_signal(signalnum=None):
    """Installs a signal handler for *signalnum*, which defaults to
    ``SIGINT``, or keyboard interrupt/ctrl-c. This signal handler
    launches a :mod:`pdb` breakpoint. Results vary in concurrent
    systems, but this technique can be useful for debugging infinite
    loops, or easily getting into deep call stacks.

    Args:
        signalnum (int): The signal number of the signal to handle
            with pdb. Defaults to :mod:`signal.SIGINT`, see
            :mod:`signal` for more information.
    """
    import pdb
    import signal
    if not signalnum:
        signalnum = signal.SIGINT

    old_handler = signal.getsignal(signalnum)

    def pdb_int_handler(sig, frame):
        signal.signal(signalnum, old_handler)
        pdb.set_trace()
        pdb_on_signal(signalnum)  # use 'u' to find your code and 'h' for help

    signal.signal(signalnum, pdb_int_handler)
    return


def pdb_on_exception(limit=100):
    """Installs a handler which, instead of exiting, attaches a
    post-mortem pdb console whenever an unhandled exception is
    encountered.

    Args:
        limit (int): the max number of stack frames to display when
            printing the traceback

    A similar effect can be achieved from the command-line using the
    following command::

      python -m pdb your_code.py

    But ``pdb_on_exception`` allows you to do this conditionally and within
    your application. To restore default behavior, just do::

      sys.excepthook = sys.__excepthook__
    """
    import pdb
    import sys
    import traceback

    def pdb_excepthook(exc_type, exc_val, exc_tb):
        traceback.print_tb(exc_tb, limit=limit)
        pdb.post_mortem(exc_tb)

    sys.excepthook = pdb_excepthook
