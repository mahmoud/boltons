import io
import json
import os

import pytest

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


def _jsonl_stream(data, stream_kind, tmp_path):
    if stream_kind == 'stringio':
        return io.StringIO(data)
    if stream_kind == 'bytesio':
        return io.BytesIO(data.encode('utf-8'))
    path = tmp_path / 'unicode.jsonl'
    path.write_bytes(data.encode('utf-8'))
    if stream_kind == 'binary':
        return path.open('rb')
    return path.open(encoding='utf-8', newline='')


@pytest.mark.parametrize('stream_kind', ['stringio', 'bytesio', 'text', 'binary'])
@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('ignore_errors', [False, True])
@pytest.mark.parametrize('ensure_ascii', [False, True])
@pytest.mark.parametrize('newline', ['\n', '\r\n'])
@pytest.mark.parametrize('trailing_newline', [False, True])
def test_jsonl_unicode_records(tmp_path, stream_kind, reverse, ignore_errors,
                              ensure_ascii, newline, trailing_newline):
    # These are legal JSON string contents, not JSONL record boundaries.
    value = 'left\u0085middle\u2028more\u2029right'
    records = [{value: value}, {'n': 2}, value]
    data = newline.join(json.dumps(obj, ensure_ascii=ensure_ascii) for obj in records)
    if trailing_newline:
        data += newline
    expected = records[::-1] if reverse else records
    with _jsonl_stream(data, stream_kind, tmp_path) as stream:
        assert list(JSONLIterator(stream, reverse=reverse,
                                  ignore_errors=ignore_errors)) == expected


@pytest.mark.parametrize('newline', ['\n', '\r', '\r\n'])
@pytest.mark.parametrize('offset', [-1, 0, 1])
@pytest.mark.parametrize('trailing_newline', [False, True])
def test_jsonl_unicode_block_boundaries(newline, offset, trailing_newline):
    # Put U+2029 immediately before, at, and after the first backward read
    # boundary, with a record spanning multiple blocks.
    tail = newline if trailing_newline else ''
    suffix_size = DEFAULT_BLOCKSIZE - 2 - len(tail) + offset
    value = 'x' * DEFAULT_BLOCKSIZE + '\u0085\u2028\u2029' + 'y' * suffix_size
    records = [value, {'n': 2}, value]
    data = newline.join(json.dumps(obj, ensure_ascii=False) for obj in records)
    if trailing_newline:
        data += newline
    assert list(JSONLIterator(io.StringIO(data), reverse=True)) == records[::-1]


def test_jsonl_unicode_crlf_block_boundary():
    # The first backward block begins at LF, splitting the CRLF pair.
    records = [{'text': '\u0085\u2028\u2029'}, 'y' * (DEFAULT_BLOCKSIZE - 6) + '\u0085\u2028\u2029']
    data = '\r\n'.join(json.dumps(obj, ensure_ascii=False) for obj in records)
    assert data[-DEFAULT_BLOCKSIZE] == '\n'
    assert list(JSONLIterator(io.StringIO(data), reverse=True)) == records[::-1]


@pytest.mark.parametrize('stream_kind', ['stringio', 'bytesio', 'text', 'binary'])
@pytest.mark.parametrize('trailing_newline', [False, True])
@pytest.mark.parametrize('ensure_ascii', [False, True])
def test_jsonl_reverse_cr_records(tmp_path, stream_kind, trailing_newline, ensure_ascii):
    records = [{'text': '\u0085\u2028\u2029'}, {'n': 2}]
    data = '\r'.join(json.dumps(obj, ensure_ascii=ensure_ascii) for obj in records)
    if trailing_newline:
        data += '\r'
    with _jsonl_stream(data, stream_kind, tmp_path) as stream:
        assert list(JSONLIterator(stream, reverse=True)) == records[::-1]


@pytest.mark.parametrize('stream_kind', ['stringio', 'bytesio', 'text', 'binary'])
@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_jsonl_unicode_and_invalid_records(tmp_path, stream_kind, reverse, newline):
    records = [{'text': '\u0085\u2028\u2029'}, {'n': 2}]
    data = newline.join(['', json.dumps(records[0], ensure_ascii=False),
                         'not json', '', json.dumps(records[1]), ''])
    with _jsonl_stream(data, stream_kind, tmp_path) as stream:
        with pytest.raises(ValueError):
            list(JSONLIterator(stream, reverse=reverse))
    with _jsonl_stream(data, stream_kind, tmp_path) as stream:
        assert list(JSONLIterator(stream, reverse=reverse, ignore_errors=True)) == (
            records[::-1] if reverse else records)


@pytest.mark.parametrize('separator', ['\u0085', '\u2028', '\u2029'])
@pytest.mark.parametrize('reverse', [False, True])
def test_jsonl_unicode_outside_strings_is_invalid(separator, reverse):
    data = '1' + separator + '2\n3\n'
    with pytest.raises(ValueError):
        list(JSONLIterator(io.StringIO(data), reverse=reverse))
    assert list(JSONLIterator(io.StringIO(data), reverse=reverse,
                              ignore_errors=True)) == [3]


@pytest.mark.parametrize('separator', ['\v', '\f', '\x1c', '\x1d', '\x1e',
                                      '\u0085', '\u2028', '\u2029'])
@pytest.mark.parametrize('blocksize', [2, 7, DEFAULT_BLOCKSIZE])
def test_reverse_iter_lines_unicode_separators(separator, blocksize):
    # The generic helper retains its broader, public str.splitlines behavior.
    data = 'alpha' + separator + 'beta\n'
    assert list(reverse_iter_lines(io.StringIO(data), blocksize=blocksize)) == [
        '', 'beta', 'alpha']


@pytest.mark.parametrize('data', ['', '\n', '\r', '\r\n', '\n\n\r\n\r'])
def test_jsonl_reverse_empty_records(data):
    assert list(JSONLIterator(io.StringIO(data), reverse=True)) == []
