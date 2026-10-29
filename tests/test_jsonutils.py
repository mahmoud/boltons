import os

from pytest import mark

from boltons.jsonutils import (JSONLIterator,
                               DEFAULT_BLOCKSIZE,
                               reverse_iter_lines)

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
NEWLINES_DATA_PATH = CUR_PATH + '/newlines_test_data.txt'
JSONL_DATA_PATH = CUR_PATH + '/jsonl_test_data.txt'


def _test_reverse_iter_lines(filename, blocksize=DEFAULT_BLOCKSIZE):
    fo = open(filename)
    reference = fo.read()
    fo.seek(0, os.SEEK_SET)
    rev_lines = list(reverse_iter_lines(fo, blocksize))
    assert '\n'.join(rev_lines[::-1]) == reference


def _test_reverse_iter_lines_bytes(filename, blocksize=DEFAULT_BLOCKSIZE):
    fo = open(filename, 'rb')
    reference = fo.read()
    fo.seek(0, os.SEEK_SET)
    rev_lines = list(reverse_iter_lines(fo, blocksize))
    assert os.linesep.encode('ascii').join(rev_lines[::-1]) == reference



def test_reverse_iter_lines():
    for blocksize in (2, 4, 16, 4096):
        _test_reverse_iter_lines(NEWLINES_DATA_PATH, blocksize)
        _test_reverse_iter_lines_bytes(NEWLINES_DATA_PATH, blocksize)


def test_jsonl_iterator():
    ref = [{'4': 4}, {'3': 3}, {'2': 2}, {'1': 1}, {}]
    jsonl_iter = JSONLIterator(open(JSONL_DATA_PATH), reverse=True)
    jsonl_list = list(jsonl_iter)
    assert jsonl_list == ref


class _CappedReadFile:
    """Wraps a file object, raising if read() is called more than
    max_reads times, so a non-terminating read loop fails fast
    instead of hanging the test suite."""
    def __init__(self, fo, max_reads=100):
        self._fo = fo
        self._reads = 0
        self._max_reads = max_reads

    def read(self, size=-1):
        self._reads += 1
        if self._reads > self._max_reads:
            raise RuntimeError('read() called more than %s times,'
                               ' likely an infinite loop' % self._max_reads)
        return self._fo.read(size)

    def __iter__(self):
        return iter(self._fo)

    def __getattr__(self, name):
        return getattr(self._fo, name)


def test_jsonl_iterator_mid_last_line_seek_terminates(tmp_path):
    # a rel_seek landing mid-final-line of a file with no trailing
    # newline used to loop forever in _align_to_newline
    path = tmp_path / 'no_trailing_newline.jsonl'
    path.write_text('{"1": 1}\n{"2": 2}')
    fo = _CappedReadFile(open(str(path)))
    jsonl_iter = JSONLIterator(fo, rel_seek=0.9)
    assert list(jsonl_iter) == []


def test_jsonl_iterator_rel_seek_negative():
    # negative rel_seek used to normalize to >1.0, seeking past EOF
    # and looping forever in _align_to_newline
    ref = list(JSONLIterator(open(JSONL_DATA_PATH)))
    fo = _CappedReadFile(open(JSONL_DATA_PATH))
    tail = list(JSONLIterator(fo, rel_seek=-0.5))
    assert tail
    assert tail == list(JSONLIterator(open(JSONL_DATA_PATH), rel_seek=0.5))
    assert tail == ref[len(ref) - len(tail):]


def test_jsonl_explicit_end_seek(tmp_path):
    path = tmp_path / 'records.jsonl'
    path.write_text('{"n": 1}\n{"n": 2}\n')
    with path.open('rb', buffering=0) as stream:
        assert list(JSONLIterator(stream, reverse=True, rel_seek=1.0)) == [{'n': 2}, {'n': 1}]
    with path.open() as stream:
        assert list(JSONLIterator(stream, rel_seek=1.0)) == []


def test_jsonl_relative_seek_binary_matches_text(tmp_path):
    path = tmp_path / 'records.jsonl'
    path.write_bytes(b'{"n": 1}\n{"n": 2}\n{"n": 3}\n')
    with path.open('rb') as binary, path.open() as text:
        assert list(JSONLIterator(binary, rel_seek=0.4)) == list(JSONLIterator(text, rel_seek=0.4))


def test_reverse_iter_lines_uses_file_encoding(tmp_path):
    path = tmp_path / 'latin1.txt'
    path.write_bytes('café\nfin'.encode('latin-1'))
    with path.open(encoding='latin-1') as stream:
        assert list(reverse_iter_lines(stream)) == ['fin', 'café']


def test_reverse_iter_lines_uses_explicit_binary_encoding():
    from io import BytesIO

    stream = BytesIO('café\nfin'.encode('latin-1'))
    assert list(reverse_iter_lines(stream, encoding='latin-1')) == ['fin', 'café']


def test_reverse_iter_lines_keeps_text_stream_attached(tmp_path):
    path = tmp_path / 'lines.txt'
    path.write_text('first\nsecond')
    with path.open() as stream:
        assert list(reverse_iter_lines(stream)) == ['second', 'first']
        stream.seek(0)
        assert stream.read() == 'first\nsecond'


def test_reverse_iter_lines_leading_empty_lines():
    from io import BytesIO
    data = b'\n\nfirst\nsecond\n'
    for blocksize in (2, 4, 4096):
        rev = list(reverse_iter_lines(BytesIO(data), blocksize=blocksize))
        assert rev == [b'', b'second', b'first', b'', b'']
        assert b'\n'.join(reversed(rev)) == data
    assert list(reverse_iter_lines(BytesIO(b'\n'))) == [b'', b'']


def test_reverse_iter_lines_stringio():
    from io import StringIO
    assert list(reverse_iter_lines(StringIO('a\nb\n'))) == ['', 'b', 'a']
    assert list(reverse_iter_lines(StringIO('x\ny'), blocksize=2)) == ['y', 'x']


def test_jsonl_iterator_text_cur_byte_pos(tmp_path):
    path = tmp_path / 'records.jsonl'
    path.write_bytes(b'{"1": 1}\n{"2": 2}\n')  # no CRLF translation on Windows
    with path.open() as stream:
        jsonl_iter = JSONLIterator(stream)
        assert next(jsonl_iter) == {'1': 1}
        assert jsonl_iter.cur_byte_pos == len('{"1": 1}\n')
        assert list(jsonl_iter) == [{'2': 2}]


@mark.parametrize('binary', [False, True])
@mark.parametrize('rel_seek', [0.1, 0.45, -0.4])
@mark.parametrize('max_chunk', [1, 3, 5])
def test_jsonl_relative_seek_short_reads(binary, rel_seek, max_chunk):
    import io
    import json

    class ShortReadFile(_CappedReadFile):
        def __init__(self, stream, max_chunk):
            super().__init__(stream, max_reads=1000)
            self.max_chunk = max_chunk

        def read(self, size=-1):
            if size >= 0:
                size = min(size, self.max_chunk)
            return super().read(size)

    text = ''.join(json.dumps({'n': i, 'padding': 'x' * 20}) + '\n'
                   for i in range(5))
    stream_type = io.BytesIO if binary else io.StringIO
    data = text.encode('utf-8') if binary else text
    expected = list(JSONLIterator(stream_type(data), rel_seek=rel_seek))
    assert expected
    stream = ShortReadFile(stream_type(data), max_chunk)
    actual = list(JSONLIterator(stream, rel_seek=rel_seek))
    assert actual == expected
    assert stream.tell() <= len(data)
