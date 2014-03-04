# -*- coding: utf-8 -*-


def pdb_on_signal(signalnum=None):
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
