import io

import pytest

from boltons.ioutils import SpooledStringIO


@pytest.mark.parametrize('text, method, args', [
    ('first\nlast', 'readline', ()),
    ('\u2603aa\nlast', 'readline', ()),
    ('first\nmiddle\nlast', 'readline', ()),
    ('first\n' + 'a' * 65 + '\u2603' * 100, 'readline', ()),
    ('\u2603abTAIL', 'read', (3,)),
    ('\u2603abTAIL', 'seek', (3,)),
    ('first\nlast', 'readlines', ()),
], ids=['ascii-line', 'unicode-prefix', 'buffered-lines', 'partial-codepoint',
        'bounded-read', 'seek', 'readlines'])
@pytest.mark.parametrize('rolled', [False, True])
def test_write_after_read_uses_character_position(text, method, args, rolled):
    with SpooledStringIO() as stream:
        stream.write(text)
        if rolled:
            stream.rollover()
        stream.seek(0)
        reference = io.StringIO(text)
        assert getattr(stream, method)(*args) == getattr(reference, method)(*args)
        assert stream.tell() == reference.tell()
        for value in ('X', 'Y'):
            assert stream.write(value) == reference.write(value)
            assert stream.tell() == reference.tell()
        assert stream.read() == reference.read()
        assert stream.getvalue() == reference.getvalue()


@pytest.mark.parametrize('text', ['first\nlast', '\u2603aa\nlast'])
def test_write_after_readline_can_trigger_rollover(text):
    with SpooledStringIO(max_size=len(text.encode('utf-8')) + 1) as stream:
        stream.write(text)
        assert not stream._rolled
        stream.seek(0)
        reference = io.StringIO(text)
        assert stream.readline() == reference.readline()
        assert stream.write('XXXX') == reference.write('XXXX')
        assert stream._rolled
        assert stream.tell() == reference.tell()
        assert stream.read() == reference.read()
        assert stream.getvalue() == reference.getvalue()


def test_write_after_readline_and_rollover():
    with SpooledStringIO() as stream:
        stream.write('\u2603aa\nlast')
        stream.seek(0)
        assert stream.readline() == '\u2603aa\n'
        stream.rollover()
        assert stream.write('X') == 1
        assert stream.tell() == 5
        assert stream.read() == 'ast'
        assert stream.getvalue() == '\u2603aa\nXast'


@pytest.mark.parametrize('rolled', [False, True])
def test_empty_write_preserves_unread_text(rolled):
    with SpooledStringIO() as stream:
        stream.write('\u2603aa\nlast')
        if rolled:
            stream.rollover()
        stream.seek(0)
        assert stream.readline() == '\u2603aa\n'
        assert stream.write('') == 0
        assert stream.tell() == 4
        assert stream.read() == 'last'


@pytest.mark.parametrize('rolled', [False, True])
def test_appends_do_not_seek_or_read_existing_text(monkeypatch, rolled):
    with SpooledStringIO() as stream:
        if rolled:
            stream.rollover()

        def unexpected_io(*args, **kwargs):
            raise AssertionError('appending must not scan or seek existing text')

        with monkeypatch.context() as patch:
            patch.setattr(stream.buffer, 'seek', unexpected_io)
            patch.setattr(stream.buffer.reader, 'read', unexpected_io)
            for _ in range(100):
                assert stream.write('\u2603abc') == 4
        assert stream.tell() == 400
        assert stream.getvalue() == '\u2603abc' * 100


@pytest.mark.parametrize('query', ['getvalue', '__len__'])
@pytest.mark.parametrize('rolled', [False, True])
def test_write_position_survives_content_queries(query, rolled):
    text = '\u2603aa\nlast'
    with SpooledStringIO() as stream:
        stream.write(text)
        if rolled:
            stream.rollover()
        stream.seek(0)
        reference = io.StringIO(text)
        assert stream.readline() == reference.readline()
        expected = text if query == 'getvalue' else len(text)
        assert getattr(stream, query)() == expected
        assert stream.write('X') == reference.write('X')
        assert stream.tell() == reference.tell()
        assert stream.getvalue() == reference.getvalue()


@pytest.mark.parametrize('rolled', [False, True])
def test_write_then_truncate_preserves_character_position(rolled):
    with SpooledStringIO() as stream:
        stream.write('first\nlast')
        if rolled:
            stream.rollover()
        stream.seek(0)
        assert stream.readline() == 'first\n'
        assert stream.write('X') == 1
        stream.truncate(8)
        assert stream.tell() == 7
        assert stream.read() == 'a'
        assert stream.getvalue() == 'first\nXa'
