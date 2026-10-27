import io

import pytest

from boltons.jsonutils import reverse_iter_lines


@pytest.mark.parametrize('newline', ['\n', '\r\n'])
@pytest.mark.parametrize('count,expected', [(0, []), (3, ['one']),
                                            (4, ['', 'one']), (6, ['t\N{LATIN SMALL LETTER E WITH ACUTE}', 'one'])])
def test_reverse_lines_respects_text_read_position(newline, count, expected):
    data = newline.join(['one', 't\N{LATIN SMALL LETTER E WITH ACUTE}wo', 'three'])
    with io.TextIOWrapper(io.BytesIO(data.encode('utf-8')), encoding='utf-8') as stream:
        stream.read(count)
        assert list(reverse_iter_lines(stream, preseek=False, blocksize=2)) == expected


def test_reverse_lines_preseek_still_reads_the_whole_file():
    with io.TextIOWrapper(io.BytesIO(b'one\ntwo'), encoding='utf-8') as stream:
        stream.read(1)
        assert list(reverse_iter_lines(stream, blocksize=2)) == ['two', 'one']
