import pytest

from boltons.ioutils import SpooledBytesIO, SpooledStringIO


@pytest.mark.parametrize('cls,value', [(SpooledBytesIO, b'first\nlast'),
                                       (SpooledStringIO, 'first\nlast')])
@pytest.mark.parametrize('rolled', [False, True])
def test_spooled_self_equality_preserves_cursor(cls, value, rolled):
    with cls() as stream:
        stream.write(value)
        if rolled:
            stream.rollover()
        stream.seek(2)
        assert stream == stream
        assert not (stream != stream)
        assert stream.tell() == 2
        assert stream.read() == value[2:]


@pytest.mark.parametrize('cls,value', [(SpooledBytesIO, b'hello'),
                                       (SpooledStringIO, 'hello')])
def test_spooled_distinct_comparisons_and_closed_files(cls, value):
    with cls() as left, cls() as right:
        left.write(value)
        right.write(value)
        assert left == right
        right.seek(0)
        right.write(value[:1] * 2)
        assert left != right
    with pytest.raises(ValueError):
        left == left
