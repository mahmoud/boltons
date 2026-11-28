import re
from collections import namedtuple

import pytest

from boltons.formatutils import (get_format_args,
                                 BaseFormatField,
                                 split_format_str,
                                 tokenize_format_str,
                                 infer_positional_format_args,
                                 DeferredValue as DV)


@pytest.mark.parametrize('name', ['+1', '-1', '1_0', ' 1', '1 ', '²', '①', '₁', 'name'])
def test_numeric_looking_keyword_format_args(name):
    template = '{' + name + '}'
    assert template.format(**{name: 'value'}) == 'value'
    assert get_format_args(template) == ([], [(name, str)])


@pytest.mark.parametrize('name', ['+1', '-1', '1_0', ' 1', '1 '])
def test_numeric_looking_keyword_format_types(name):
    template = '{' + name + ':d}'
    assert template.format(**{name: 7}) == '7'
    assert get_format_args(template) == ([], [(name, int)])


@pytest.mark.parametrize('name', ['0', '01', '٢', '１２', '𝟙'])
def test_decimal_positional_format_controls(name):
    index = int(name)
    values = ['value'] * (index + 1)
    assert ('{' + name + '}').format(*values) == 'value'
    assert get_format_args('{' + name + '}') == ([(index, str)], [])
    assert BaseFormatField(name).is_positional


@pytest.mark.parametrize('name', ['+1', '-1', '1_0', ' 1', '1 ', '²', '①', '₁', 'name'])
def test_keyword_format_field_classification(name):
    field = BaseFormatField(name)
    assert field.fstr.format(**{name: 'value'}) == 'value'
    assert not field.is_positional


def test_nested_numeric_looking_keyword_format_args():
    template = '{value:{1_0}}'
    assert template.format(**{'value': 'x', '1_0': 3}) == 'x  '
    assert get_format_args(template) == ([], [('value', str), ('1_0', str)])


def test_format_field_classification_updates_and_subpaths():
    field = BaseFormatField('0')
    assert field.is_positional
    field.set_fname('²[0]')
    assert not field.is_positional
    assert field.fstr.format(**{'²': ['value']}) == 'value'
    field.set_fname('١[0]')
    assert field.is_positional
    assert field.fstr.format('unused', ['value']) == 'value'
    field.set_fname('')
    assert field.is_positional


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
               "example 5: {0}, {1:d}, {2:f}, {1}",
               "example 6: {}, {}, {}, {1}"]


def test_get_fstr_args():
    results = []
    for t in _TEST_TMPLS:
        inferred_t = infer_positional_format_args(t)
        res = get_format_args(inferred_t)
        assert res


def test_split_fstr():
    results = []
    for t in _TEST_TMPLS:
        res = split_format_str(t)
        results.append(res)
        assert res


def test_tokenize_format_str():
    results = []
    for t in _TEST_TMPLS:
        res = tokenize_format_str(t)
        results.append(res)
        assert res


def test_deferredvalue():
    def myfunc():
        myfunc.called += 1
        return 123

    myfunc.called = 0

    dv = DV(myfunc)
    assert str(dv) == '123'
    assert myfunc.called == 1
    assert str(dv) == '123'
    assert myfunc.called == 1
    dv.cache_value = False
    assert str(dv) == '123'
    assert myfunc.called == 2
    assert str(dv) == '123'
    assert myfunc.called == 3
