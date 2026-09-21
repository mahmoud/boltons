import io

import pytest

from boltons.ioutils import SpooledBytesIO, SpooledStringIO


@pytest.mark.parametrize('rolled', [False, True])
@pytest.mark.parametrize('factory,text', [(SpooledBytesIO, b'abc'), (SpooledStringIO, 'a\N{SNOWMAN}b')])
def test_spooled_write_returns_units_written(factory, text, rolled):
    stream = factory()
    try:
        if rolled:
            stream.rollover()
        assert stream.write(text) == len(text)
        assert stream.write(text[:0]) == 0
        assert stream.getvalue() == text
    finally:
        stream.close()


@pytest.mark.parametrize('rolled', [False, True])
def test_buffered_writer_can_flush_spooled_bytes(rolled):
    stream = SpooledBytesIO()
    if rolled:
        stream.rollover()
    writer = io.BufferedWriter(stream)
    try:
        writer.write(b'payload')
        writer.flush()
        assert stream.getvalue() == b'payload'
    finally:
        # Avoid a second failing flush masking the original regression.
        try:
            writer.close()
        except BlockingIOError:
            stream.close()


def test_buffer_write_uses_byte_count_for_rollover():
    stream = SpooledBytesIO(max_size=4)
    with memoryview(bytearray(b'abcd')).cast('I') as view:
        try:
            assert stream.write(view) == 4
            assert stream._rolled
            assert stream.getvalue() == b'abcd'
        finally:
            stream.close()
