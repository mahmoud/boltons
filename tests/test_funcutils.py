# -*- coding: utf-8 -*-

from boltons.funcutils import (copy_function,
                               total_ordering,
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


class test_total_ordering():
    @total_ordering
    class Number(object):
        def __init__(self, val):
            self.val = int(val)

        def __gt__(self, other):
            return self.val > other

        def __eq__(self, other):
            return self.val == other

    num = Number(3)
    assert num > 0
    assert num == 3

    assert num < 5
    assert num >= 2
    assert num != 1
