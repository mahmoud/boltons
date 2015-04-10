# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function support.
``classutils`` attempts to do the same for metaprogramming with
classes, types and instances.
"""

import weakref


def gencls(*bases, **extras):
    """Define a new class inline (ie. class version of "lambda").
    Takes classes to use as base class from positional arguments,
    and any extra attributes of the class to set from keyword arguments.

    Useful for once-off classes that can be described as "other class, but with a mixin"

    >>> class A(object):
    ...     name = 'Alice'
    ...     def greet(self):
    ...         print 'Hello, ' + self.name
    ...
    >>> class BobNameMixin(object):
    ...     name = 'Bob'
    ...
    >>> gencls(BobNameMixin, A)().greet()
    Hello, Bob
    >>> gencls(A, name='Eve')().greet()
    Hello, Eve

    """
    return type('gencls:{}'.format(','.join(base.__name__ for base in bases)), bases, extras)


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
    >>> get_all_subclasses(A)
    set([<class 'boltons.classutils.D'>, <class 'boltons.classutils.B'>, <class 'boltons.classutils.C'>])
    >>> get_all_subclasses(B)
    set([<class 'boltons.classutils.C'>])

    """
	# XXX doctest result is fragile - relies on str(set), which relies on hash order
	#     how to make it better without losing readability?
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


class mixedmethod(object):
    """A decorator for methods such that they can act like a classmethod when called via the class,
    or an instance method when bound to an instance. For example:
        >>> class MyCls(object):
        ...   x = 1
        ...   @mixedmethod
        ...   def foo(self):
        ...     return self.x
        >>> print MyCls.foo()
        1
        >>> mycls = MyCls()
        >>> mycls.x = 2
        >>> print mycls.foo()
        2
    """

    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, cls):
        arg = cls if instance is None else instance
        return lambda *args, **kwargs: self.fn(arg, *args, **kwargs)


class TracksInstances(object):
    """A mixin that lets you easily track instances of subclasses of this object.
    A set of all active (not garbage collected) instances of a class can be retrieved
    with cls.get_instances(). This includes instances of subclasses by default - you can pass the paramter
    exclusive=True to override this."""

    _instances = weakref.WeakKeyDictionary() # maps cls to set of instances

    def __new__(cls, *args, **kwargs):
        instances = cls._instances.setdefault(cls, weakref.WeakSet())
        instance = super(TracksInstances, cls).__new__(cls, *args, **kwargs)
        instances.add(instance)
        return instance

    @classmethod
    def get_instances(cls, exclusive=False):
        """Get a set of instances that exist for this class or subclasses.
        If exculsive, restrict output to only instances strictly of this class."""
        result = cls._instances.setdefault(cls, weakref.WeakSet())
        if not exclusive:
            for subcls in cls.__subclasses__():
                result |= subcls.get_instances()
        return result

