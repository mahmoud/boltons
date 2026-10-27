import io
import os

import pytest

from boltons.ioutils import SpooledStringIO


@pytest.mark.parametrize('rolled', [False, True])
@pytest.mark.parametrize('whence,offset', [(os.SEEK_SET, 9),
                                           (os.SEEK_CUR, 7),
                                           (os.SEEK_END, 5)])
def test_text_sparse_seek_matches_stringio(rolled, whence, offset):
    value = 'a\N{LATIN SMALL LETTER E WITH ACUTE}bc'
    with SpooledStringIO() as stream, io.StringIO() as reference:
        for target in (stream, reference):
            target.write(value)
            target.seek(2)
        if rolled:
            stream.rollover()
        destination = offset
        if whence == os.SEEK_CUR:
            destination += reference.tell()
        elif whence == os.SEEK_END:
            destination += len(value)
        assert stream.seek(offset, whence) == reference.seek(destination)
        assert stream.read() == reference.read() == ''
        assert stream.write('\N{GREEK SMALL LETTER PI}') == reference.write('\N{GREEK SMALL LETTER PI}')
        assert stream.tell() == reference.tell()
        assert stream.getvalue() == reference.getvalue()


def test_sparse_write_can_trigger_rollover():
    with SpooledStringIO(max_size=6) as stream:
        stream.write('a\N{LATIN SMALL LETTER E WITH ACUTE}bc')
        assert not stream._rolled
        stream.seek(9)
        stream.write('\N{GREEK SMALL LETTER PI}')
        assert stream._rolled
        assert stream.getvalue() == 'a\N{LATIN SMALL LETTER E WITH ACUTE}bc' + '\0' * 5 + '\N{GREEK SMALL LETTER PI}'
