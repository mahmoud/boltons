
from boltons.excutils import ExceptionCauseMixin


class MyError(ExceptionCauseMixin, ValueError):
    pass


def test_no_cause_behaves_like_plain_exception():
    # When the first argument is not an exception, there is no cause and
    # the instance should behave like an ordinary exception.
    err = MyError('something broke')
    assert err.cause is None
    assert str(err) == 'something broke'
    assert err.args == ('something broke',)


def test_no_args_at_all():
    err = MyError()
    assert err.cause is None
    assert str(err) == ''


def test_wrapping_a_cause_sets_cause_and_root_cause():
    cause = KeyError('missing')
    err = MyError(cause, 'lookup failed')
    assert err.cause is cause
    # With a single, direct cause the root cause is that same exception.
    assert err.root_cause is cause


def test_cause_is_stripped_from_message():
    cause = KeyError('missing')
    err = MyError(cause, 'lookup failed')
    # The cause occupies the first positional slot, so the human-readable
    # message is the remaining argument, not the exception object.
    assert err._get_message() == 'lookup failed'


def test_message_empty_when_only_a_cause_is_given():
    err = MyError(KeyError('missing'))
    assert err._get_message() == ''


def test_exc_str_names_class_message_and_root_cause():
    cause = KeyError('missing')
    err = MyError(cause, 'lookup failed')
    exc_str = err._get_exc_str()
    assert exc_str.startswith('MyError: ')
    assert 'lookup failed' in exc_str
    assert 'caused by' in exc_str
    assert 'KeyError' in exc_str


def test_exc_str_without_message_still_reports_cause():
    err = MyError(KeyError('missing'))
    exc_str = err._get_exc_str()
    assert 'caused by' in exc_str
    assert 'KeyError' in exc_str


def test_chained_wrapping_propagates_original_root_cause():
    root = KeyError('missing')
    inner = MyError(root, 'inner')
    outer = MyError(inner, 'outer')
    # The cause is the immediate exception that was wrapped, but the root
    # cause should still point back at the original error.
    assert outer.cause is inner
    assert outer.root_cause is root


if __name__ == '__main__':
    import pytest
    raise SystemExit(pytest.main([__file__, '-v']))
