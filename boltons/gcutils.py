# -*- coding: utf-8 -*-

import gc


class GCToggler(object):
    """\
    Safely take a bit more control of your garbage collection
    schedule. Anecdotal experience says certain object-creation-heavy
    tasks see speedups of around 10% by simply doing one GC at the end,
    especially if few of the objects will be collected.
    """
    def __init__(self, postcollect=False):
        self.postcollect = postcollect

    def __enter__(self):
        gc.disable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.enable()
        if self.postcollect:
            gc.collect()


toggle_gc = GCToggler()
toggle_gc_postcollect = GCToggler(postcollect=True)


if __name__ == '__main__':
    def _test_main():
        import time
        COUNT = int(1e6)

        start = time.time()
        with toggle_gc_postcollect:
            x = [{} for x in xrange(COUNT)]
        print time.time() - start, 'secs without gc'

        start = time.time()
        x = [{} for x in xrange(COUNT)]
        print time.time() - start, 'secs with gc'
    _test_main()
