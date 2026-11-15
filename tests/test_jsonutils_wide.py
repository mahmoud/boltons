import codecs
import io

import pytest

from boltons.jsonutils import reverse_iter_lines


ENCODINGS = ('utf-16', 'utf-16-le', 'utf-16-be',
             'utf-32', 'utf-32-le', 'utf-32-be')


def _reference(text):
    # Encoded binary streams have the CR/LF delimiter set of bytes.splitlines,
    # including reverse_iter_lines' extra empty line after a trailing LF.
    lines = text.encode('utf8').splitlines()
    if text.endswith('\n'):
        lines.append(b'')
    return [line.decode('utf8') for line in reversed(lines)]


@pytest.mark.parametrize('encoding', ENCODINGS)
@pytest.mark.parametrize('blocksize', (1, 2, 3, 4, 7, 16, 4096))
@pytest.mark.parametrize('wrapped', (False, True))
@pytest.mark.parametrize('text', (
    'first\nlast',
    '\n\n\u010a\u0a00\u010d\u0d00\n\U0001f642\u00e9\n\n',
    'one\r\ntwo\rthree\nlast',
    'a\x85b\u2028c\u2029d\ve\ff\x1cg\x1dh\x1ei',
))
def test_wide_encoded_lines(encoding, blocksize, wrapped, text):
    raw = io.BytesIO(text.encode(encoding))
    stream = io.TextIOWrapper(raw, encoding=encoding) if wrapped else raw
    kwargs = {} if wrapped else {'encoding': encoding}
    with stream:
        assert list(reverse_iter_lines(stream, blocksize, **kwargs)) == _reference(text)
        assert not stream.closed


@pytest.mark.parametrize('encoding,codec,bom', (
    ('utf-16', 'utf-16-le', codecs.BOM_UTF16_LE),
    ('utf-16', 'utf-16-be', codecs.BOM_UTF16_BE),
    ('utf-32', 'utf-32-le', codecs.BOM_UTF32_LE),
    ('utf-32', 'utf-32-be', codecs.BOM_UTF32_BE),
))
@pytest.mark.parametrize('blocksize', (1, 3, 8, 4096))
def test_wide_bom_endianness(encoding, codec, bom, blocksize):
    text = '\U0001f642\n\u00e9\n'
    raw = io.BytesIO(bom + text.encode(codec))
    assert list(reverse_iter_lines(raw, blocksize, encoding=encoding)) == _reference(text)
    assert list(reverse_iter_lines(io.BytesIO(bom), blocksize, encoding=encoding)) == []


@pytest.mark.parametrize('encoding', ENCODINGS)
def test_wide_empty_and_explicit_bom(encoding):
    assert list(reverse_iter_lines(io.BytesIO(), encoding=encoding)) == []
    if encoding.endswith(('-le', '-be')):
        text = '\ufefffirst\nlast'
        assert list(reverse_iter_lines(io.BytesIO(text.encode(encoding)),
                                      encoding=encoding)) == ['last', '\ufefffirst']


@pytest.mark.parametrize('encoding', ('utf-16', 'utf-32'))
def test_wide_native_endian_without_bom(encoding):
    text = 'first\nlast'
    # bytes.decode accepts native-endian data without a BOM; the helper's
    # encoding argument has historically been passed to that decoder.
    data = text.encode(encoding)[len(''.encode(encoding)):]
    assert data.decode(encoding) == text
    assert list(reverse_iter_lines(io.BytesIO(data), encoding=encoding)) == ['last', 'first']


@pytest.mark.parametrize('encoding', ('UTF_16_LE', 'utf_16be', 'UTF_32_LE', 'utf_32be'))
def test_wide_codec_aliases(encoding):
    assert list(reverse_iter_lines(io.BytesIO('a\nb'.encode(encoding)),
                                   blocksize=3, encoding=encoding)) == ['b', 'a']


@pytest.mark.parametrize('encoding', ENCODINGS)
@pytest.mark.parametrize('blocksize', (1, 7, 4096))
def test_wide_preseek_prefix(encoding, blocksize):
    prefix = 'first\n\U0001f642'
    data = (prefix + '\nlast').encode(encoding)
    stream = io.BytesIO(data)
    stream.seek(len(prefix.encode(encoding)))
    assert list(reverse_iter_lines(stream, blocksize, preseek=False,
                                   encoding=encoding)) == ['\U0001f642', 'first']
    stream.seek(0)
    assert list(reverse_iter_lines(stream, blocksize, preseek=False,
                                   encoding=encoding)) == []


@pytest.mark.parametrize('encoding', ENCODINGS)
def test_wide_disk_and_reuse(tmp_path, encoding):
    path = tmp_path / 'wide.txt'
    text = 'first\n\U0001f642\nlast'
    path.write_bytes(text.encode(encoding))
    with path.open(encoding=encoding) as stream:
        assert list(reverse_iter_lines(stream, blocksize=3)) == _reference(text)
        stream.seek(0)
        assert stream.read() == text


@pytest.mark.parametrize('encoding,data', (
    ('utf-16-le', b'a'),
    ('utf-16-be', b'\xd8\x00'),
    ('utf-16-le', b'\x00\xdc'),
    ('utf-32-le', b'a\x00\x00'),
    ('utf-32-be', b'\x00\x11\x00\x00'),
    ('utf-32-le', b'\x00\xd8\x00\x00'),
))
def test_wide_malformed_input(encoding, data):
    with pytest.raises(UnicodeError):
        list(reverse_iter_lines(io.BytesIO(data), blocksize=1, encoding=encoding))


def test_wide_partial_codepoint_prefix():
    stream = io.BytesIO('\U0001f642\nlast'.encode('utf-16-le'))
    stream.seek(2)  # prefix ends with an unmatched high surrogate
    with pytest.raises(UnicodeError):
        list(reverse_iter_lines(stream, preseek=False, encoding='utf-16-le'))


@pytest.mark.parametrize('encoding', ENCODINGS)
def test_wide_partial_code_unit_prefix(encoding):
    stream = io.BytesIO('first\nlast'.encode(encoding))
    stream.seek(1)
    with pytest.raises(UnicodeError):
        list(reverse_iter_lines(stream, preseek=False, encoding=encoding))


class _BoundedReads(io.BytesIO):
    def __init__(self, data, max_size):
        super().__init__(data)
        self.max_size = max_size
        self.total_read = 0
        self.read_calls = 0
        self.max_request = 0

    def read(self, size=-1):
        assert 0 <= size <= self.max_size
        self.max_request = max(self.max_request, size)
        data = super().read(size)
        self.total_read += len(data)
        self.read_calls += 1
        return data


@pytest.mark.parametrize('encoding', ENCODINGS)
def test_wide_bounded_reads_and_long_line(encoding):
    text = ('\U0001f642\u010a\u0d00\n' * 2000) + ('x' * 10000) + '\nlast'
    data = text.encode(encoding)
    max_size = 18 if encoding.startswith('utf-16') else 20
    stream = _BoundedReads(data, max_size=max_size)
    assert list(reverse_iter_lines(stream, blocksize=17, encoding=encoding)) == _reference(text)
    assert stream.total_read <= len(data) + 4
    assert stream.read_calls > 100


def test_empty_input_does_not_resolve_unused_codec():
    assert list(reverse_iter_lines(io.BytesIO(), encoding='not-a-codec')) == []


def test_nonwide_and_nonseekable_controls():
    data = b'\nfirst\r\nsecond\rthird\n'
    expected = [b'', b'third', b'second', b'first', b'']
    for blocksize in (1, 3, 4096):
        assert list(reverse_iter_lines(io.BytesIO(data), blocksize)) == expected
        assert list(reverse_iter_lines(io.BytesIO(data), blocksize, encoding='utf8')) == [
            line.decode('utf8') for line in expected]
    assert list(reverse_iter_lines(io.StringIO('a\u2028b'))) == ['b', 'a']
    assert list(reverse_iter_lines(io.BytesIO('caf\u00e9\nfin'.encode('latin1')),
                                   encoding='latin1')) == ['fin', 'caf\u00e9']
    with pytest.raises(io.UnsupportedOperation):
        list(reverse_iter_lines(io.BufferedIOBase(), encoding='utf-16'))
