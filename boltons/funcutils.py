# -*- coding: utf-8 -*-

import functools
from types import MethodType
from itertools import chain


__all__ = ['partial', 'CachedInstancePartial', 'InstancePartial']


def mro_items(obj_type):
    # handle slots?
    return chain.from_iterable([ct.__dict__.iteritems()
                                for ct in obj_type.__mro__])


def dir_dict(obj):
    # separate function for handling descriptors on types?
    ret = {}
    for k in dir(obj):
        ret[k] = getattr(obj, k)
    return ret


class InstancePartial(functools.partial):
    def __get__(self, obj, obj_type):
        return MethodType(self, obj, obj_type)


class CachedInstancePartial(functools.partial):
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

# tests

def _main():
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
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    _main()
