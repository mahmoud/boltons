# -*- coding: utf-8 -*-

import gc


def get_all(type_obj, include_subtypes=True):
    """\
    Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there, with some
    exceptions. For example, `get_all(bool)` returns an empty list
    because True and False are themselves built-in and not tracked.

    There are some optimizations present, such that getting instances
    of user-created types is quite fast. Also, setting
    `include_subtypes` to False is another way to increase performance
    where instances of subtypes aren't required.

    Finally, in concurrent environments, note that objects coming back
    may be partially constructed or in all sorts of states, so caveat
    emptor.
    """

    if not isinstance(type_obj, type):
        raise TypeError('expected a type, not %r' % type_obj)
    if gc.is_tracked(type_obj):
        to_check = gc.get_referrers(type_obj)
    else:
        to_check = gc.get_objects()

    if include_subtypes:
        ret = [x for x in to_check if isinstance(x, type_obj)]
    else:
        ret = [x for x in to_check if type(x) is type_obj]
    return ret


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
    class TestType(object):
        pass

    tt = TestType()

    def _test_main():
        print 'TestTypes:', len(get_all(TestType))
        print 'bools:', len(get_all(bool))
        import pdb;pdb.set_trace()


    def _test_main2():
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
