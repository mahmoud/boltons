import operator
import os

import pytest

from boltons.ioutils import READ_CHUNK_SIZE, SpooledStringIO


pytestmark = pytest.mark.parametrize('get_length', [len, operator.attrgetter('len')],
                                    ids=['len', 'property'])


@pytest.fixture(params=[False, True], ids=['memory', 'disk'])
def stream(request):
    with SpooledStringIO() as stream:
        if request.param:
            stream.rollover()
        yield stream


@pytest.mark.parametrize('text', ['', 'a\u2603bc', '\u2603' * (READ_CHUNK_SIZE + 2)],
                         ids=['empty', 'unicode', 'multiple_chunks'])
def test_length_preserves_position(stream, get_length, text):
    stream.write(text)
    for position in [0, len(text) // 2, len(text)]:
        stream.seek(position)
        byte_position = stream.buffer.tell()
        for _ in range(2):
            assert get_length(stream) == len(text)
            assert stream.tell() == position
            assert stream.buffer.tell() == byte_position
        assert stream.read() == text[position:]


def test_relative_seek_after_length(stream, get_length):
    stream.write('a\u2603bc')
    stream.seek(1)
    assert get_length(stream) == 4
    assert stream.seek(-1, os.SEEK_CUR) == 0
    assert stream.read() == 'a\u2603bc'


def test_write_after_length(stream, get_length):
    stream.write('a\u2603bc')
    stream.seek(2)
    assert get_length(stream) == 4
    assert stream.write('X') == 1
    assert stream.tell() == 3
    assert stream.getvalue() == 'a\u2603Xc'
