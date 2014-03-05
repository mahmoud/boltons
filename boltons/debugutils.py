# -*- coding: utf-8 -*-


def pdb_on_signal(signalnum=None):
    """
    Installs a signal handler for `signalnum` (default SIGINT/keyboard
    interrupt/ctrl-c) that launches a pdb breakpoint. This can be
    useful for debugging infinite loops and getting into deep call
    stacks.

    This may have unintended results when used in highly
    threaded/concurrent code.
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
    """
    Installs a handler which, instead of exiting, attaches a
    post-mortem pdb console whenever an unhandled exception is
    encountered.

    To restore default behavior, just do:

    `sys.excepthook = sys.__excepthook__`

    A similar effect can be achieved with the following command:

    `python -m pdb your_code.py`
    """
    import pdb
    import sys
    import traceback

    def pdb_excepthook(exc_type, exc_val, exc_tb):
        traceback.print_tb(exc_tb, limit=limit)
        pdb.post_mortem(exc_tb)

    sys.excepthook = pdb_excepthook
