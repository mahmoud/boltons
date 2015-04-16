# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function support.
``classutils`` attempts to do the same for metaprogramming with
classes, types and instances.
"""

def issubclass(subcls, supercls):
    """As per the builtin issubclass(), but will simply return False if
    either arg is not suitable (eg. if subcls is not a class),
    instead of raising TypeError.
    """
    try:
        return __builtins__['issubclass'](subcls, supercls)
    except TypeError:
        return False


def get_all_subclasses(cls):
    """Recursive method to find all decendents of cls, ie.
    its subclasses, subclasses of those classes, etc.
    Returns a set.

    >>> class A(object):
    ...     pass
    ...
    >>> class B(A):
    ...     pass
    ...
    >>> class C(B):
    ...     pass
    ...
    >>> class D(A):
    ...     pass
    ...
    >>> get_all_subclasses(A) == set([B, C, D])
    True
    >>> get_all_subclasses(B) == set([C])
    True

    """
    subs = set(cls.__subclasses__())
    subs_of_subs = [get_all_subclasses(subcls) for subcls in subs]
    return subs.union(*subs_of_subs)


class classproperty(object):
    """Acts like a stdlib @property, but the wrapped get function is a class method.
    For simplicity, only read-only properties are implemented."""

    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, cls):
        return self.fn(cls)
