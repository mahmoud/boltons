# -*- coding: utf-8 -*-
"""
A small set of utilities useful for debugging misbehaving
applications. Currently this focuses on ways to use :mod:`pdb`, the
built-in Python debugger.
"""

import time

try:
    basestring
except NameError:
    basestring = (str, bytes)  # py3

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
    return


def wt_print_hook(obj, name, args, kwargs):
    args = (hex(id(obj)), time.time(), obj.__class__.__name__, name,
            ', '.join([repr(a) for a in args]))
    tmpl = '@%s %r - %s.%s(%s)'
    if kwargs:
        args += (', '.join(['%s=%r' % (k, v) for k, v in kwargs.items()]),)
        tmpl = '%s - %s@%s.%s(%s, %s)'

    print(tmpl % args)


def wrap_trace(obj, hook=wt_print_hook, which=None):
    # other actions: pdb.set_trace, print, aggregate, aggregate_return
    # (like aggregate but with the return value) Q: should aggregate
    # includ self?

    # TODO: how to handle creating the instance
    # Specifically, getting around the namedtuple problem
    # TODO: test classmethod/staticmethod/property
    # TODO: label for object
    # TODO: wrap __dict__ for old-style classes?

    if isinstance(which, basestring):
        which_func = lambda attr_name, attr_val: attr_name == which
    else:   # if callable(which):
        which_func = which

    def wrap_method(attr_name, func, _hook=hook):
        def wrapped(*a, **kw):
            a = a[1:]
            hook(obj, attr_name, a, kw)
            return func(*a, **kw)
        wrapped.__name__ = func.__name__
        wrapped.__doc__ = func.__doc__
        try:
            wrapped.__module__ = func.__module__
        except Exception:
            pass
        try:
            if func.__dict__:
                wrapped.__dict__.update(func.__dict__)
        except Exception:
            pass
        return wrapped

    def wrap_getattribute():
        def __getattribute__(self, attr_name):
            hook(obj, '__getattribute__', (attr_name,), {})
            ret = type(obj).__getattribute__(obj, attr_name)
            if callable(ret):
                ret = type(obj).__getattribute__(self, attr_name)
            return ret
        return __getattribute__

    attrs = {}
    for attr_name in dir(obj):
        try:
            attr_val = getattr(obj, attr_name)
        except Exception:
            continue

        if not callable(attr_val) or attr_name in ('__new__',):
            continue
        elif which_func and not which_func(attr_name, attr_val):
            continue

        if attr_name == '__getattribute__':
            wrapped_method = wrap_getattribute()
        else:
            wrapped_method = wrap_method(attr_name, attr_val)

        attrs[attr_name] = wrapped_method

    cls_name = obj.__class__.__name__
    if cls_name == cls_name.lower():
        type_name = 'wrapped_' + cls_name
    else:
        type_name = 'Wrapped' + cls_name

    if hasattr(obj, '__mro__'):
        bases = (obj.__class__,)
    else:
        # need new-style class for even basic wrapping of callables to
        # work. getattribute won't work for old-style classes of course.
        bases = (obj.__class__, object)

    trace_type = type(type_name, bases, attrs)
    for cls in trace_type.__mro__:
        try:
            return cls.__new__(trace_type)
        except Exception:
            pass
    raise TypeError('unable to wrap_trace %r instance %r'
                    % (obj.__class__, obj))


if __name__ == '__main__':
    obj = wrap_trace({})
    obj['hi'] = 'hello'
    obj.fail
    import pdb;pdb.set_trace()
