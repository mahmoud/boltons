import io

import pytest

from boltons.ioutils import READ_CHUNK_SIZE, SpooledStringIO


@pytest.fixture(params=['memory', 'rolled', 'automatic'])
def stream(request):
    with SpooledStringIO(max_size=1 if request.param == 'automatic' else 10**7) as result:
        if request.param == 'rolled':
            result.rollover()
        yield result


@pytest.mark.parametrize('initial, position, replacement', [
    ('éé', 0, 'a'),
    ('ab', 0, 'é'),
    ('A🙂中Z', 1, 'é'),
    ('Aé中Z', 1, '🙂'),
    ('中tail', 0, '🙂🙂'),
    ('a🙂', 1, '界more'),
    ('abcd', 1, 'XY'),
    ('é中🙂', 1, '界'),
])
def test_overwrite_unicode_characters(stream, initial, position, replacement):
    reference = io.StringIO(initial)
    stream.write(initial)
    reference.seek(position)
    stream.seek(position)
    assert stream.write(replacement) == reference.write(replacement)
    assert stream.tell() == reference.tell()
    assert stream.getvalue() == reference.getvalue()
    assert stream.read() == reference.read()


@pytest.mark.parametrize('initial_head, replacement', [('a', '🙂'), ('🙂', 'a')])
def test_overwrite_preserves_a_large_tail(stream, monkeypatch, initial_head, replacement):
    initial = initial_head + 'é中' * (READ_CHUNK_SIZE + 1) + 'tail'
    reference = io.StringIO(initial)
    stream.write(initial)
    stream.seek(0)
    raw_read = stream.buffer.stream.read

    def bounded_read(size=-1):
        assert 0 <= size <= READ_CHUNK_SIZE
        return raw_read(size)

    with monkeypatch.context() as patch:
        patch.setattr(stream.buffer.stream, 'read', bounded_read)
        stream.write(replacement)
    reference.write(replacement)
    assert stream.tell() == reference.tell()
    assert stream.getvalue() == reference.getvalue()


def test_overwrite_rolls_when_the_tail_pushes_size_over_the_limit():
    with SpooledStringIO(max_size=5) as stream:
        stream.write('abcd')
        assert not stream._rolled
        stream.seek(0)
        stream.write('🙂')
        assert stream._rolled
        assert stream.tell() == 1
        assert stream.getvalue() == '🙂bcd'


@pytest.mark.parametrize('read_method', ['read', 'readline'])
def test_overwrite_after_read(stream, read_method):
    initial = 'é\nfirst\nsecond\nthird'
    reference = io.StringIO(initial)
    stream.write(initial)
    stream.seek(0)
    args = (1,) if read_method == 'read' else ()
    assert getattr(stream, read_method)(*args) == getattr(reference, read_method)(*args)
    assert stream.write('🙂') == reference.write('🙂')
    assert stream.tell() == reference.tell()
    assert stream.getvalue() == reference.getvalue()
