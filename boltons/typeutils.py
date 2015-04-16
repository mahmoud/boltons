# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function support.
``typeutils`` attempts to do the same for metaprogramming with types
and instances.
"""

from collections import deque

_issubclass = issubclass


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

    >>> class MyObject(object): pass
    ...
    >>> issubclass(MyObject, object)  # always a fun fact
    True
    >>> issubclass('hi', 'friend')
    False
    """
    try:
        return _issubclass(subclass, baseclass)
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
    >>> [t.__name__ for t in get_all_subclasses(A)]
    ['B', 'D', 'C']
    >>> [t.__name__ for t in get_all_subclasses(B)]
    ['C']
    """
    try:
        to_check = deque(cls.__subclasses__())
    except (AttributeError, TypeError):
        raise TypeError('expected type object, not %r' % cls)
    seen, ret = set(), []
    while to_check:
        cur = to_check.popleft()
        if cur in seen:
            continue
        ret.append(cur)
        seen.add(cur)
        to_check.extend(cur.__subclasses__())
    return ret


class classproperty(object):
    """Much like a :func:`property`, but the wrapped get function is a
    class method.  For simplicity, only read-only properties are
    implemented.
    """

    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, cls):
        return self.fn(cls)
