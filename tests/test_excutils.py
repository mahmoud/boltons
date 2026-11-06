from boltons.excutils import ExceptionCauseMixin


class MyErr(ExceptionCauseMixin, Exception):
    pass


def test_get_str_without_a_cause():
    assert MyErr('invalid operand').get_str() == 'MyErr: invalid operand'
    assert MyErr(404).get_str() == 'MyErr: 404'
    assert MyErr().get_str() == 'MyErr'


def test_cause_str_outside_handler():
    err = MyErr(ValueError('inner'))
    assert 'ValueError: inner' in str(err)
