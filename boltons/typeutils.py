# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function support.
``typeutils`` attempts to do the same for metaprogramming with types
and instances.
"""


def issubclass(subclass, baseclass):
    """Just like the built-in :func:`issubclass`, this function checks
    whether *subclass* is inherited from *baseclass*. Unlike the
    built-in function, this ``issubclass`` will simply return
    ``False`` if either argument is not suitable (e.g., if *subclass*
    is not an instance of :class:`type`), instead of raising
    :exc:`TypeError`.

    Args:
        subclass (type): The target class to check.
        baseclass (type): The base class *subclass* will be checked against.

    >>> issubclass(bool, int)  # always a fun fact
    True
    >>> issubclass('hi', 'friend')
    False
    """
    try:
        return __builtins__['issubclass'](subclass, baseclass)
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
