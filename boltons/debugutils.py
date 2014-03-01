# -*- coding: utf-8 -*-


def pdb_on_signal(signal=None):
    import pdb
    import signal
    if not signal:
        signal = signal.SIGINT

    def pdb_int_handler(sig, frame):
        pdb.set_trace()

    signal.signal(signal.SIGINT, pdb_int_handler)
    return
