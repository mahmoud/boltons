import io

import pytest

from boltons.jsonutils import reverse_iter_lines


class ShortReader:
    def __init__(self, stream):
        self.stream = stream

    def read(self, size=-1):
        return self.stream.read(min(size, 2) if size >= 0 else 2)

    def seek(self, *args):
        return self.stream.seek(*args)

    def tell(self):
        return self.stream.tell()


@pytest.mark.parametrize('binary', [False, True])
@pytest.mark.parametrize('blocksize', [4, 9])
@pytest.mark.parametrize('trailing', [False, True])
def test_reverse_lines_collects_short_reads(binary, blocksize, trailing):
    data = 'first\nsecond\nthird' + ('\n' if trailing else '')
    expected = ([''] if trailing else []) + ['third', 'second', 'first']
    if binary:
        stream = io.BytesIO(data.encode('ascii'))
        expected = [line.encode('ascii') for line in expected]
    else:
        stream = io.StringIO(data)
    assert list(reverse_iter_lines(ShortReader(stream), blocksize=blocksize)) == expected
