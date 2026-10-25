from boltons.excutils import ExceptionCauseMixin


class MyErr(ExceptionCauseMixin, Exception):
    pass


def test_cause_str_outside_handler():
    err = MyErr(ValueError('inner'))
    assert 'ValueError: inner' in str(err)
