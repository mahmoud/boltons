# -*- coding: utf-8 -*-

import re
from collections import namedtuple

import pytest
from boltons.formatutils import (get_format_args,
                                 split_format_str,
                                 tokenize_format_str,
                                 infer_positional_format_args,
                                 FormatArgs,
                                 NamedFormatArg,
                                 PositionalFormatArg)


PFAT = namedtuple("PositionalFormatArgTest", "fstr arg_vals res")

_PFATS = [PFAT('{} {} {}', ('hi', 'hello', 'bye'), "hi hello bye"),
          PFAT('{:d} {}', (1, 2), "1 2"),
          PFAT('{!s} {!r}', ('str', 'repr'), "str 'repr'"),
          PFAT('{[hi]}, {.__name__!r}', ({'hi': 'hi'}, re), "hi, 're'"),
          PFAT('{{joek}} ({} {})', ('so', 'funny'), "{joek} (so funny)")]


def test_pos_infer():
    for i, (tmpl, args, res) in enumerate(_PFATS):
        converted = infer_positional_format_args(tmpl)
        assert converted.format(*args) == res


_TEST_TMPLS = ["example 1: {hello}",
               "example 2: {hello:*10}",
               "example 3: {hello:*{width}}",
               "example 4: {hello!r:{fchar}{width}}, {width}, yes",
               "example 5: {0}, {1:d}, {2:f}, {1}"]

try:
    from collections import OrderedDict
except ImportError:
    pass  # skip the non-2.6 compatible tests on 2.6
else:
    _TEST_TMPLS.append("example 6: {}, {}, {}, {1}")
    del OrderedDict


def test_get_fstr_args():
    results = []
    for t in _TEST_TMPLS:
        inferred_t = infer_positional_format_args(t)
        res = get_format_args(inferred_t)
        results.append(res)
    return results


@pytest.mark.parametrize(('sample', 'expected'), zip(_TEST_TMPLS, [
        ([], [('hello', str)]),
        ([], [('hello', str)]),
        ([], [('hello', str), ('width', str)]),
        ([], [('hello', str), ('fchar', str), ('width', str)]),
        ([(0, str), (1, int), (2, float)], []),
        # example 6 is skipped
]))
def test_get_format_args(sample, expected):
    """Test `get_format_args` result as tuples."""
    assert get_format_args(sample) == expected


@pytest.mark.parametrize(('sample', 'expected'), zip(_TEST_TMPLS, [
        FormatArgs([], [NamedFormatArg('hello', str)]),
        FormatArgs([], [NamedFormatArg('hello', str)]),
        FormatArgs([], [NamedFormatArg('hello', str),
                        NamedFormatArg('width', str)]),
        FormatArgs([], [NamedFormatArg('hello', str),
                        NamedFormatArg('fchar', str),
                        NamedFormatArg('width', str)]),
        FormatArgs([PositionalFormatArg(0, str),
                    PositionalFormatArg(1, int),
                    PositionalFormatArg(2, float)], []),
        # example 6 is skipped
]))
def test_get_format_args_namedtuples(sample, expected):
    """Test `get_format_args` result as `namedtuples`."""
    result = get_format_args(sample)
    assert result == expected
    assert result.positional == expected.positional
    assert result.named == expected.named


def test_split_fstr():
    results = []
    for t in _TEST_TMPLS:
        res = split_format_str(t)
        results.append(res)
    return results


def test_tokenize_format_str():
    results = []
    for t in _TEST_TMPLS:
        res = tokenize_format_str(t)
        results.append(res)
    return results
