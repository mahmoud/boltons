# -*- coding: utf-8 -*-

from boltons.funcutils import (copy_function,
                               InstancePartial,
                               CachedInstancePartial)


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


def test_partials():
    g = SubGreeter('hello')

    assert g.greet() == 'Hello.'
    assert g.native_greet() == 'Hello;'
    assert g.partial_greet() == 'Hello!'
    assert g.cached_partial_greet() == 'Hello...'
    assert CachedInstancePartial(g.greet, excitement='s')() == 'Hellos'


def test_copy_function():
    def callee():
        return 1
    callee_copy = copy_function(callee)
    assert callee is not callee_copy
    assert callee() == callee_copy()
