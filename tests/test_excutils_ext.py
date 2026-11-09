import sys
import linecache

import pytest

from boltons.excutils import (ExceptionCauseMixin, _DeferredLine, _TBItem,
                              _extract_from_frame, _extract_from_tb,
                              _format_exc)


class MyErr(ExceptionCauseMixin, Exception):
    pass


class SubErr(MyErr):
    pass


def _make_tb(depth=2):
    """Build a real traceback object of the requested depth."""
    def inner():
        raise ValueError('boom')
    def outer():
        inner()
    try:
        if depth <= 2:
            outer()
        else:
            def lvl(n):
                if n == 0:
                    outer()
                else:
                    lvl(n - 1)
            lvl(depth - 2)
    except ValueError:
        return sys.exc_info()[2]
    raise AssertionError('expected ValueError')


def test_cause_outside_handler_has_no_trace():
    err = MyErr(ValueError('inner'), 'outer message')
    assert err.cause is not None
    assert err.root_cause is err.cause
    # constructed outside an except block: no traceback captured
    s = str(err)
    assert 'outer message' in s
    assert 'ValueError: inner' in s


def test_cause_inside_handler_captures_trace():
    try:
        _make_tb()
    except Exception:
        raise AssertionError('helper should not raise')
    try:
        inner_fn()
    except Exception:
        pass
    try:
        raise ValueError('inner')
    except ValueError as ve:
        err = MyErr(ve, 'wrapped')
    assert err.full_trace is not None
    assert len(err._tb) >= 1
    assert len(err._stack) >= 1
    s = str(err)
    assert 'Wrapped traceback (most recent call last):' in s
    assert 'wrapped' in s
    assert 'caused by' in s


def inner_fn():
    raise ValueError('x')


def test_root_cause_chains():
    try:
        raise ValueError('root')
    except ValueError as ve:
        root = ve
        mid = MyErr(ve, 'mid')
    top = SubErr(mid, 'top')
    assert top.root_cause is root
    # full_trace propagated from cause
    assert list(top.full_trace) == list(mid.full_trace)


def test_get_str_includes_traceback_and_message():
    try:
        raise KeyError('k')
    except KeyError as ke:
        err = MyErr(ke, 'msg')
    s = err.get_str()
    assert s.startswith('Traceback (most recent call last):')
    assert 'msg' in s
    assert 'caused by' in s


def test_no_cause_falls_back_to_builtin():
    err = MyErr('plain message')
    assert err.cause is None
    assert str(err) == 'plain message'
    assert err._get_trace_str() == repr(err)
    assert err._get_message() == 'plain message'


def test_get_message_empty_when_no_args():
    err = MyErr(ValueError('inner'))
    assert err._get_message() == ''


def test_format_exc_default_and_message():
    s = _format_exc(ValueError('oops'))
    assert 'ValueError' in s and 'oops' in s
    s2 = _format_exc(ValueError('ignored'), 'custom msg')
    assert 'custom msg' in s2
    # returns rstripped string
    assert s == s.rstrip()


def test_extract_from_tb_items():
    tb = _make_tb()
    items = _extract_from_tb(tb)
    assert len(items) >= 2
    for item in items:
        assert isinstance(item, _TBItem)
        assert item.filename
        assert isinstance(item.lineno, int)
        assert item.name
        assert isinstance(item.line, _DeferredLine)
        assert item.frame_id
    # limit respected
    assert len(_extract_from_tb(tb, limit=1)) == 1
    # deepest frame is last
    assert items[-1].name == 'inner'


def test_extract_from_frame_items():
    def probe():
        return _extract_from_frame(sys._getframe())
    items = probe()
    assert items
    assert any(i.name == 'probe' for i in items)
    # reverse order: caller of _extract_from_frame is last
    assert items[-1].name == 'probe'
    assert len(_extract_from_frame(sys._getframe(), limit=1)) == 1


def test_tbitem_repr_includes_frame_id():
    tb = _make_tb()
    item = _extract_from_tb(tb)[0]
    r = repr(item)
    assert '_TBItem(' in r
    assert str(item.frame_id) in r


def test_deferred_line_resolves_and_caches():
    dl = _DeferredLine(__file__, 1)
    assert str(dl).startswith('import sys')
    # cached after first resolution
    assert dl._line == 'import sys'
    assert repr(dl) == repr('import sys')
    assert len(dl) == len('import sys')
    assert dl.strip() == 'import sys'


def test_deferred_line_equality():
    a = _DeferredLine('f.py', 10)
    b = _DeferredLine('f.py', 10)
    c = _DeferredLine('f.py', 11)
    assert a == b
    assert not (a != b)
    assert a != c
    assert not (a == c)


def test_deferred_line_missing_file_returns_none_str():
    dl = _DeferredLine('/nonexistent/path/xyz.py', 5)
    assert str(dl) == ''
    assert len(dl) == 0


def test_deferred_line_module_globals_filtering():
    g = {'__name__': 'm', '__loader__': object(), 'secret': 1}
    dl = _DeferredLine(__file__, 1, g)
    assert 'secret' not in dl.module_globals
    assert dl.module_globals['__name__'] == 'm'


def test_math_lol_example():
    from boltons.excutils import math_lol, MathError
    with pytest.raises(MathError) as excinfo:
        math_lol()
    err = excinfo.value
    assert err.root_cause is not None
    assert isinstance(err.root_cause, ZeroDivisionError)
    assert 'ya done messed up' in str(err)
    assert 'Wrapped traceback' in str(err)
