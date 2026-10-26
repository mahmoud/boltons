import io

import pytest

from boltons.ioutils import SpooledStringIO


@pytest.mark.parametrize('text', [
    '', 'no newline', 'first\nlast', 'αβ\n雪山\n终',
    '\ntrailing', 'head\n' + '🙂' * 10000,
], ids=['empty', 'eof', 'ascii', 'unicode', 'empty-line', 'large-tail'])
@pytest.mark.parametrize('rolled', [False, True])
@pytest.mark.parametrize('tail_method', ['read', 'readlines'])
@pytest.mark.parametrize('length_query', [len, lambda stream: stream.len])
def test_length_queries_preserve_unread_text(
        text, rolled, tail_method, length_query):
    with SpooledStringIO() as stream:
        if rolled:
            stream.rollover()
        stream.write(text)
        stream.seek(0)
        reference = io.StringIO(text)
        assert stream.readline() == reference.readline()
        position = stream.tell()
        for _ in range(2):
            assert length_query(stream) == len(text)
            assert stream.tell() == position
        actual = getattr(stream, tail_method)()
        assert actual == getattr(reference, tail_method)()
        assert stream.tell() == reference.tell()


@pytest.mark.parametrize('rolled', [False, True])
def test_length_queries_preserve_positions_beyond_eof(rolled):
    with SpooledStringIO() as stream:
        stream.write('雪\nlast')
        if rolled:
            stream.rollover()
        stream.seek(20)
        assert len(stream) == 6
        assert stream.tell() == 20
        assert stream.read() == ''
