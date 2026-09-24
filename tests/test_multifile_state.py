import io

import pytest

from boltons.ioutils import MultiFileReader


@pytest.fixture(params=[str, bytes])
def reader(request):
    if request.param is str:
        return MultiFileReader(io.StringIO('ab'), io.StringIO('cd')), 'abcd'
    return MultiFileReader(io.BytesIO(b'ab'), io.BytesIO(b'cd')), b'abcd'


def test_zero_read_does_not_consume(reader):
    stream, contents = reader
    assert stream.read(0) == contents[:0]
    assert stream.read() == contents


def test_negative_read_returns_remaining(reader):
    stream, contents = reader
    assert stream.read(1) == contents[:1]
    assert stream.read(-1) == contents[1:]
    assert stream.read(1) == contents[:0]


@pytest.mark.parametrize('initial_read', [3, 5, -1])
def test_rewind_resets_file_selection(reader, initial_read):
    stream, contents = reader
    stream.read(initial_read)
    stream.seek(0)
    assert stream.read(4) == contents
