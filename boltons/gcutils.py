# -*- coding: utf-8 -*-

import gc


class GCToggler(object):
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
