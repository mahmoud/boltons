import re
from collections import namedtuple

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


def _deferred_copy_value():
    return [123]


def test_deferredvalue_copy_and_pickle():
    import copy
    import pickle

    transforms = (copy.copy, copy.deepcopy,
                  lambda value: pickle.loads(pickle.dumps(value)))
    for cache_value in (False, True):
        for evaluated in (False, True):
            for transform in transforms:
                original = DV(_deferred_copy_value, cache_value=cache_value)
                original.extra = {'kept': True}
                if evaluated:
                    original.get_value()
                restored = transform(original)
                assert restored is not original
                assert restored.extra == {'kept': True}
                assert restored.get_value() == [123]
                assert str(restored) == '[123]'
                if cache_value:
                    assert restored.get_value() is restored.get_value()


def test_deferredvalue_deepcopied_log_record():
    import copy
    import logging

    record = logging.LogRecord('test', logging.INFO, '', 0, 'value=%s',
                               (DV(_deferred_copy_value),), None)
    assert copy.deepcopy(record).getMessage() == 'value=[123]'
    assert record.getMessage() == 'value=[123]'
