# -*- coding: utf-8 -*-

import functools
from types import MethodType
from itertools import chain


__all__ = ['partial', 'CachedInstancePartial', 'InstancePartial',
           'dir_dict', 'mro_items']

_func_type = type(lambda: None)


def mro_items(type_obj):
    """\
    Takes a type and returns an iterator over all class variables
    throughout the type hierarchy (respecting the MRO).

    >>> sorted([k for k, v in mro_items(int) if not (callable(v) or isinstance(v, type(int.__int__)))])
    ['__class__', '__doc__', '__doc__', 'denominator', 'imag', 'numerator', 'real']
    """
    # TODO: handle slots?
    return chain.from_iterable([ct.__dict__.iteritems()
                                for ct in type_obj.__mro__])


def dir_dict(obj, raise_exc=False):
    """\
    Return a dictionary of attribute names to values for a given
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
    """\
    Returns a shallow copy of the function, including code object,
    globals, closure, etc. If ``copy_dict`` is set to ``True``, then
    the function's nonstandard attributes are also copied.
    """
    # TODO: Python 3 compat
    ret = _func_type(orig.func_code,
                     orig.func_globals,
                     name=orig.func_name,
                     argdefs=orig.func_defaults,
                     closure=orig.func_closure)
    if copy_dict:
        ret.__dict__.update(orig.__dict__)
    return ret


class InstancePartial(functools.partial):
    """\
    :class:`functools.partial` is a huge convenience for anyone working
    with Python's great first-class functions. It allows developers to
    curry arguments and incrementally create simpler callables for a
    variety of use cases.

    Unfortunately there's one big gap in its usefulness:
    methods. Partials just don't get bound as methods and
    automatically handed a reference to ``self``. The
    ``InstancePartial`` class remedies this by inheriting from
    :class:`functools.partial` and implementing the necessary
    descriptor protocol. There are no other differences in
    implementation or usage. :class:`CachedInstancePartial`, below,
    has the same ability, but is slightly more efficient.
    """
    def __get__(self, obj, obj_type):
        return MethodType(self, obj, obj_type)


class CachedInstancePartial(functools.partial):
    """\
    The CachedInstancePartial is virtually the same as
    :class:`InstancePartial`, adding support for method-usage to
    :class:`functools.partial`, except that upon first access, it
    caches the bound method on the associated object, speeding it up
    for future accesses, and bringing the method call overhead to
    about the same as non-``partial`` methods.

    See the :class:`InstancePartial` docstring for more info.
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
        print g.greet()
        print g.native_greet()
        print g.partial_greet()
        print g.cached_partial_greet()
        print CachedInstancePartial(g.greet, excitement='s')()

        def callee():
            return 1
        callee_copy = copy_function(callee)
        assert callee is not callee_copy
        assert callee() == callee_copy()
        import pdb;pdb.set_trace()

    _partial_main()
