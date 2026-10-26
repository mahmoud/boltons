import pytest

from boltons.excutils import ExceptionCauseMixin


class MyErr(ExceptionCauseMixin, Exception):
    pass


def test_cause_str_outside_handler():
    err = MyErr(ValueError('inner'))
    assert 'ValueError: inner' in str(err)


@pytest.mark.parametrize('generated', [False, True])
def test_cause_traceback_without_source(tmp_path, generated):
    filename = '<generated-source>' if generated else str(tmp_path / 'missing.py')
    try:
        exec(compile('raise ValueError("inner")', filename, 'exec'), {})
    except ValueError as cause:
        err = MyErr(cause, 'outer')
    # Restrict the source-availability check to the captured exception frames.
    err.full_trace = err._tb

    # Render repeatedly to exercise both deferred loading and the cached line.
    for _ in range(2):
        for rendered in (str(err), err.get_str()):
            assert filename in rendered
            assert 'ValueError: inner' in rendered
            assert 'outer' in rendered


def test_cause_traceback_with_source(tmp_path):
    filename = tmp_path / 'source.py'
    source = 'raise ValueError("inner from source")\n'
    filename.write_text(source)
    try:
        exec(compile(source, str(filename), 'exec'), {})
    except ValueError as cause:
        err = MyErr(cause, 'outer')
    err.full_trace = err._tb
    for rendered in (str(err), err.get_str()):
        assert str(filename) in rendered
        assert source.strip() in rendered
