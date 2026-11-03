import re
from collections import namedtuple

import pytest

from boltons.formatutils import (get_format_args,
                                 split_format_str,
                                 tokenize_format_str,
                                 infer_positional_format_args,
                                 DeferredValue as DV)


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


@pytest.mark.parametrize('key', ['{}', '{:}', '{!r}', '{.}', '{['])
@pytest.mark.parametrize('field', ['[{key}]', 'lookup[{key}]', '0[{key}]'])
def test_pos_infer_preserves_braces_in_lookup_keys(key, field):
    mapping = {key: 'found'}
    field = field.format(key=key)
    template = '{' + field + '}'
    if field.startswith('['):
        template += ' {}'
    inferred = infer_positional_format_args(template)
    expected = template.format(mapping, 'tail', lookup=mapping)
    assert inferred.format(mapping, 'tail', lookup=mapping) == expected


def test_pos_infer_nested_specs_and_escaped_literals():
    template = '{{literal}} {:{}} {!r} {{}}'
    inferred = infer_positional_format_args(template)
    assert inferred == '{{literal}} {0:{1}} {2!r} {{}}'
    assert inferred.format(12, 5, 'tail') == template.format(12, 5, 'tail')


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
