import io
import os

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



def test_jsonl_rel_seek_eof_without_newline():
    class CountingStringIO(io.StringIO):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.read_calls = 0

        def read(self, size=-1):
            self.read_calls += 1
            if self.read_calls > 64:
                raise AssertionError('too many reads; _align_to_newline hung')
            return super().read(size)

    bio = CountingStringIO('{"a": 1}')
    assert list(JSONLIterator(bio, rel_seek=0.5)) == []

    bio = CountingStringIO('')
    assert list(JSONLIterator(bio, rel_seek=0.5)) == []
