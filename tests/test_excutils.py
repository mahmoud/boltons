from boltons.excutils import ExceptionCauseMixin


class WrappedError(ExceptionCauseMixin, ValueError):
    pass


def test_cause_can_be_formatted_outside_exception_handler():
    error = WrappedError(ValueError('original'), 'context')
    assert str(error) == 'context (caused by ValueError: original)'
    assert error.get_str() == 'WrappedError: context (caused by ValueError: original)'


def test_chained_uncaptured_causes_preserve_the_original_error():
    cause = ValueError('original')
    inner = WrappedError(cause, 'inner')
    error = WrappedError(inner, 'outer')
    assert error.root_cause is cause
    assert str(error) == 'outer (caused by ValueError: original)'


def test_unrelated_active_exception_does_not_supply_a_traceback():
    cause = ValueError('original')
    try:
        raise RuntimeError('unrelated')
    except RuntimeError:
        error = WrappedError(cause, 'context')
    assert str(error) == 'context (caused by ValueError: original)'
    assert 'unrelated' not in error.get_str()
