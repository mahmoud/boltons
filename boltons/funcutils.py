# -*- coding: utf-8 -*-
"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function
support. ``funcutils`` generally stays in the same vein, adding to and
correcting Python's standard metaprogramming facilities.
"""
from __future__ import print_function

import sys
import functools
from types import MethodType, FunctionType
from itertools import chain


def get_module_callables(mod, ignore=None):
    """Returns two maps of (*types*, *funcs*) from *mod*, optionally
    ignoring based on the :class:`bool` return value of the *ignore*
    callable. *mod* can be a string name of a module in
    :data:`sys.modules` or the module instance itself.
    """
    if isinstance(mod, basestring):
        mod = sys.modules[mod]
    types, funcs = {}, {}
    for attr_name in dir(mod):
        if ignore and ignore(attr_name):
            continue
        try:
            attr = getattr(mod, attr_name)
        except:
            continue
        try:
            attr_mod_name = attr.__module__
        except AttributeError:
            continue
        if attr_mod_name != mod.__name__:
            continue
        if isinstance(attr, type):
            types[attr_name] = attr
        elif callable(attr):
            funcs[attr_name] = attr
    return types, funcs


def mro_items(type_obj):
    """Takes a type and returns an iterator over all class variables
    throughout the type hierarchy (respecting the MRO).

    >>> sorted(set([k for k, v in mro_items(int) if not k.startswith('__') and not callable(v)]))
    ['denominator', 'imag', 'numerator', 'real']
    """
    # TODO: handle slots?
    return chain.from_iterable(ct.__dict__.items()
    for ct in type_obj.__mro__)


def dir_dict(obj, raise_exc=False):
    """Return a dictionary of attribute names to values for a given
    object. Unlike ``obj.__dict__``, this function returns all
    attributes on the object, including ones on parent classes.
    """
    # TODO: separate function for handling descriptors on types?
    ret = {}
    for k in dir(obj):
        try:
            ret[k] = getattr(obj, k)
        except:
            if raise_exc:
                raise
    return ret


def copy_function(orig, copy_dict=True):
    """Returns a shallow copy of the function, including code object,
    globals, closure, etc.

    >>> func = lambda: func
    >>> func() is func
    True
    >>> func_copy = copy_function(func)
    >>> func_copy() is func
    True
    >>> func_copy is not func
    True

    Args:
        orig (function): The function to be copied. Must be a
            function, not just any method or callable.
        copy_dict (bool): Also copy any attributes set on the function
            instance. Defaults to ``True``.
    """
    ret = FunctionType(orig.__code__,
                       orig.__globals__,
                       name=orig.__name__,
                       argdefs=getattr(orig, "__defaults__", None),
                       closure=getattr(orig, "__closure__", None))
    if copy_dict:
        ret.__dict__.update(orig.__dict__)
    return ret


def partial_ordering(cls):
    """Class decorator, similar to :func:`functools.total_ordering`,
    except it is used to define `partial orderings`_ (i.e., it is
    possible that *x* is neither greater than, equal to, or less than
    *y*). It assumes the presence of the ``__le__()`` and ``__ge__()``
    method, but nothing else. It will not override any existing
    additional comparison methods.

    .. _partial orderings: https://en.wikipedia.org/wiki/Partially_ordered_set

    >>> @partial_ordering
    ... class MySet(set):
    ...     def __le__(self, other):
    ...         return self.issubset(other)
    ...     def __ge__(self, other):
    ...         return self.issuperset(other)
    ...
    >>> a = MySet([1,2,3])
    >>> b = MySet([1,2])
    >>> c = MySet([1,2,4])
    >>> b < a
    True
    >>> b > a
    False
    >>> b < c
    True
    >>> a < c
    False
    >>> c > a
    False
    """
    def __lt__(self, other): return self <= other and not self >= other
    def __gt__(self, other): return self >= other and not self <= other
    def __eq__(self, other): return self >= other and self <= other

    if not hasattr(cls, '__lt__'): cls.__lt__ = __lt__
    if not hasattr(cls, '__gt__'): cls.__gt__ = __gt__
    if not hasattr(cls, '__eq__'): cls.__eq__ = __eq__

    return cls


class InstancePartial(functools.partial):
    """:class:`functools.partial` is a huge convenience for anyone
    working with Python's great first-class functions. It allows
    developers to curry arguments and incrementally create simpler
    callables for a variety of use cases.

    Unfortunately there's one big gap in its usefulness:
    methods. Partials just don't get bound as methods and
    automatically handed a reference to ``self``. The
    ``InstancePartial`` type remedies this by inheriting from
    :class:`functools.partial` and implementing the necessary
    descriptor protocol. There are no other differences in
    implementation or usage. :class:`CachedInstancePartial`, below,
    has the same ability, but is slightly more efficient.

    """
    def __get__(self, obj, obj_type):
        return MethodType(self, obj, obj_type)


class CachedInstancePartial(functools.partial):
    """The ``CachedInstancePartial`` is virtually the same as
    :class:`InstancePartial`, adding support for method-usage to
    :class:`functools.partial`, except that upon first access, it
    caches the bound method on the associated object, speeding it up
    for future accesses, and bringing the method call overhead to
    about the same as non-``partial`` methods.

    See the :class:`InstancePartial` docstring for more details.
    """
    def __init__(self, func, *a, **kw):
        self.__name__ = None
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    def __get__(self, obj, obj_type):
        name = self.__name__
        if name is None:
            for k, v in mro_items(obj_type):
                if v is self:
                    self.__name__ = name = k
        if obj is None:
            return MethodType(self, obj, obj_type)
        try:
            # since this is a data descriptor, this block
            # is probably only hit once (per object)
            return obj.__dict__[name]
        except KeyError:
            obj.__dict__[name] = ret = MethodType(self, obj, obj_type)
            return ret

partial = CachedInstancePartial


#class FunctionDef(object):
#    """
#    general blocker: accept a bunch of fine-grained arguments, or just
#    accept a whole ArgSpec? or a whole signature?
#    """
#    def __init__(self, name, code, doc=None):
#        pass

# tests

if __name__ == '__main__':

    def _partial_main():
        class Greeter(object):
            def __init__(self, greeting):
                self.greeting = greeting

            def greet(self, excitement='.'):
                return self.greeting.capitalize() + excitement

            partial_greet = InstancePartial(greet, excitement='!')
            cached_partial_greet = CachedInstancePartial(greet, excitement='...')

            def native_greet(self):
                return self.greet(';')

        class SubGreeter(Greeter):
            pass

        g = SubGreeter('hello')
        print(g.greet())
        print(g.native_greet())
        print(g.partial_greet())
        print(g.cached_partial_greet())
        print(CachedInstancePartial(g.greet, excitement='s')())

        def callee():
            return 1
        callee_copy = copy_function(callee)
        assert callee is not callee_copy
        assert callee() == callee_copy()
        import pdb;pdb.set_trace()

    _partial_main()
