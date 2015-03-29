# -*- coding: utf-8 -*-
"""\
The Python Garbage Collector (GC) doesn't usually get too much attention,
probably because:

- Python's reference counting effectively handles the vast majority of
  unused objects
- People are slowly learning to avoid implementing ``__del__()``
- The collection itself strikes a good balance between simplicity and
  power (tuneable generation sizes)
- The collector itself is fast and rarely the cause of long pauses
  associated with GC in other runtimes

Even so, for many applications, the time will come when the developer
will need to track down:

 - Circular references
 - Misbehaving objects (locks, ``__del__()``)
 - Memory leaks
 - Or just ways to shave off a couple percent of execution time

The GC is a well-instrumented entry point for exactly these
tasks, and ``gcutils`` aims to facilitate it further.
"""
# TODO: type survey

import gc

__all__ = ['get_all', 'GCToggler', 'toggle_gc', 'toggle_gc_postcollect']


def get_all(type_obj, include_subtypes=True):
    """\
    Get a list containing all instances of a given type.  This will
    work for the vast majority of types out there.

    >>> class Ratking(object): pass
    >>> wiki, hak, sport = Ratking(), Ratking(), Ratking()
    >>> len(get_all(Ratking))
    3

    However, there are some exceptions. For example, ``get_all(bool)``
    returns an empty list because ``True`` and ``False`` are
    themselves built-in and not tracked.

    >>> get_all(bool)
    []

    Still, it's not hard to see how this functionality can be used to
    find all instances of a leaking type and track them down further
    using :func:`gc.get_referrers` and :func:`gc.get_referrents`.
    Furthermore, there are some optimizations present, such that
    getting instances of user-created types is quite fast. Also,
    setting ``include_subtypes`` to ``False`` is another way to
    increase performance where instances of subtypes aren't required.

    Finally, in concurrent environments, note that objects coming back
    may be partially constructed (their ``__init__()`` may not have
    completed) or in all sorts of states, so caveat emptor.

    """
    # TODO: old-style classes
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

    The ``GCToggler`` is a context-manager that allows one to safely
    take more control of your garbage collection schedule. Anecdotal
    experience says certain object-creation-heavy tasks see speedups
    of around 10% by simply doing one explicit collection at the very
    end, especially if most of the objects will stay resident.

    Two GCTogglers are already present in the ``gcutils`` module:

    - ``toggle_gc`` simply turns off GC at context entrance, and
      re-enables at exit
    - ``toggle_gc_postcollect`` does the same, but triggers an
      explicit collection after re-enabling.

    >>> with toggle_gc:
    ...     x = [object() for i in xrange(1000)]

    Between those two instances, the ``GCToggler`` type probably won't
    be used much directly, but is exported for inheritance purposes.
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
