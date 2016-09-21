#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for :mod:`boltons.jsonutils.coerce_to_json`."""

from __future__ import print_function, absolute_import

import json

import pytest  # noqa
from boltons.iterutils import remap, default_enter

try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict

try:
    from collections import UserList
except ImportError:
    from UserList import UserList

try:
    from types import SimpleNamespace
except ImportError:
    class SimpleNamespace:
        pass

from collections import namedtuple as stdlib_namedtuple
from boltons.namedutils import namedtuple as boltons_namedtuple

from boltons.jsonutils import coerce_to_json

class SampleScalarDict(object):
    def _to_dict(self): return {'fee': 'fie'}


def sample_generator():
    yield True

class SillyList(list):
    def to_json(self):
        return 42

@pytest.mark.parametrize(('type_constructor', 'outtype'), [
    # 'type_constructor', 'outtype'
    # Auto-convert scalars
    (SampleScalarDict, dict),
    (SampleScalarDict, dict),  # Repeat to ensure conversion list is non-lazy
    # Scalar types to themselves
    (lambda: None, type(None)),
    (lambda: True, bool),
    (lambda: 1, int),
    (lambda: 1.0, float),
    (SimpleNamespace, SimpleNamespace),
    (SillyList, int),
    # Lists
    (list, list),
    (tuple, list),
    (set, list),
    (UserList, list),
    (stdlib_namedtuple('Empty', ''), list),
    (boltons_namedtuple('Empty', ''), list),
    (sample_generator, list),
    # Dicts
    (dict, dict),
    (UserDict, dict),
     # Anything else to string
])
def test_coerce_to_json(type_constructor, outtype):
    """Test :func:`coerce_to_json`."""
    assert isinstance(coerce_to_json(type_constructor()), outtype)


def test_coerce_to_json_remap():
    """Test recursively mapping a structure with non-JSON data."""

    # I had an error caused by some inappropriately stored state that only
    # surfaced on the 2nd run, so I run it multiple times
    for i in range(10):
        sample_map = UserDict({
            'map': UserDict({
                'set': set([1, 2, 3]),
                'to_dict_object': SampleScalarDict(),
            })
        })

        assert json.dumps(
            remap(sample_map,
                  enter=lambda p, k, v: default_enter(p, k, coerce_to_json(v))))


def test_coerce_to_json_default():
    """Test as the *default* for :func:`json.dumps`"""
    sample_map = UserDict({
        'map': UserDict({
            'set': set([1, 2, 3]),
            'to_dict_object': SampleScalarDict(),
        })
    })

    r = json.loads(json.dumps(sample_map, default=coerce_to_json))
    assert r == {"map": {"to_dict_object": {"fee": "fie"}, "set": [1, 2, 3]}}
