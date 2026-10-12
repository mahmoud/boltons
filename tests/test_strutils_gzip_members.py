import gzip

import pytest

from boltons.strutils import gunzip_bytes


@pytest.mark.parametrize('parts', [
    [b'first', b'second'],
    [b'', b'payload'],
    [b'one', b'', b'three'],
])
def test_gunzip_bytes_reads_all_members(parts):
    compressed = b''.join(gzip.compress(part) for part in parts)
    assert gunzip_bytes(compressed) == b''.join(parts)


def test_gunzip_bytes_rejects_truncated_later_member():
    compressed = gzip.compress(b'first') + gzip.compress(b'second')[:-1]
    with pytest.raises(EOFError):
        gunzip_bytes(compressed)
