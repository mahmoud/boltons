import sys
import traceback

import pytest

from boltons.tbutils import ParsedException


def test_parsed_exc_basic():
    _tb_str = """\
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    plarp
NameError: name 'plarp' is not defined"""

    parsed_tb = ParsedException.from_string(_tb_str)
    print(parsed_tb)
    assert parsed_tb.exc_type == 'NameError'
    assert parsed_tb.exc_msg == "name 'plarp' is not defined"
    assert parsed_tb.frames == [{'source_line': 'plarp',
                                 'filepath': 'example.py',
                                 'lineno': '2',
                                 'funcname': '<module>'}]

    assert parsed_tb.to_string() == _tb_str


def test_parsed_exc_nosrcline():
    """just making sure that everything can be parsed even if there is
    a line without source and also if the exception has no message"""

    _tb_str = """\
Traceback (most recent call last):
  File "/home/mahmoud/virtualenvs/chert/bin/chert", line 9, in <module>
    load_entry_point('chert==0.2.1.dev0', 'console_scripts', 'chert')()
  File "/home/mahmoud/projects/chert/chert/core.py", line 1281, in main
    ch.process()
  File "/home/mahmoud/projects/chert/chert/core.py", line 741, in process
    self.load()
  File "<boltons.FunctionBuilder-0>", line 2, in load
  File "/home/mahmoud/projects/lithoxyl/lithoxyl/logger.py", line 291, in logged_func
    return func_to_log(*a, **kw)
  File "/home/mahmoud/projects/chert/chert/core.py", line 775, in load
    raise RuntimeError
RuntimeError"""

    parsed_tb = ParsedException.from_string(_tb_str)

    assert parsed_tb.exc_type == 'RuntimeError'
    assert parsed_tb.exc_msg == ''

    assert len(parsed_tb.frames) == 6
    assert parsed_tb.frames[3] == {'source_line': '',
                                   'filepath': '<boltons.FunctionBuilder-0>',
                                   'lineno': '2',
                                   'funcname': 'load'}
    assert parsed_tb.to_string() == _tb_str

_ANCHOR_TB_STR = """\
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(add(1, "two"))
          ^^^^^^^^^^^^^
  File "add.py", line 2, in add
    return a + b
           ~~^~~
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""


def test_parsed_exc_with_anchor():
    """parse a traceback with anchor lines beneath source lines"""
    parsed_tb = ParsedException.from_string(_ANCHOR_TB_STR)

    assert parsed_tb.exc_type == 'TypeError'
    assert parsed_tb.exc_msg == "unsupported operand type(s) for +: 'int' and 'str'"
    assert parsed_tb.frames == [{'source_line': 'print(add(1, "two"))',
                                 'source_line_anchor': '      ^^^^^^^^^^^^^',
                                 'filepath': 'main.py',
                                 'lineno': '3',
                                 'funcname': '<module>'},
                                {'source_line': 'return a + b',
                                 'source_line_anchor': '       ~~^~~',
                                 'filepath': 'add.py',
                                 'lineno': '2',
                                 'funcname': 'add'}]
    assert parsed_tb.to_string() == _ANCHOR_TB_STR


def test_parsed_exc_with_anchor_indented():
    """anchors stay aligned when the whole traceback arrives indented,
    e.g. pasted from a log: source_line is stripped, and the anchor is
    dedented by the same amount"""
    plain = ParsedException.from_string(_ANCHOR_TB_STR)
    indented = ParsedException.from_string(
        '\n'.join('    ' + line for line in _ANCHOR_TB_STR.splitlines()))
    assert indented.frames == plain.frames


def test_parsed_exc_truncated():
    """a traceback whose last frame has a source line but no following
    exception line should parse without raising IndexError"""
    _tb_str = """\
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(add(1, 2))"""

    parsed_tb = ParsedException.from_string(_tb_str)

    assert parsed_tb.exc_type == ''
    assert parsed_tb.exc_msg == ''
    assert parsed_tb.frames == [{'source_line': 'print(add(1, 2))',
                                 'filepath': 'main.py',
                                 'lineno': '3',
                                 'funcname': '<module>'}]

_MULTILINE_TB_STR = """\
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    multiline()
    ~~~~~~~~~^^
  File "example.py", line 2, in multiline
    1
    ~
    + "two"
    ^~~~~~~
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""


def test_parsed_exc_multiline_source():
    # Python 3.13+ prints every source/anchor row in a multiline expression.
    parsed = ParsedException.from_string(_MULTILINE_TB_STR)
    assert parsed.exc_type == 'TypeError'
    assert parsed.exc_msg == "unsupported operand type(s) for +: 'int' and 'str'"
    assert len(parsed.frames) == 2
    assert parsed.frames[-1] == {
        'filepath': 'example.py', 'lineno': '2', 'funcname': 'multiline',
        'source_line': '1', 'source_line_anchor': '~',
        'source_line_continuations': ['+ "two"', '^~~~~~~'],
    }
    assert parsed.source_file == 'example.py'
    assert parsed.to_string() == _MULTILINE_TB_STR
    parsed.frames[-1]['source_line'] = '2'
    assert '\n    2\n    ~\n' in parsed.to_string()


@pytest.mark.parametrize('source_rows', [
    ['call(', '    argument,', ')'],
    ['call(', '    argument,', '    ^^^^^^^^', ')'],
    ['    argument', '    ~~~~~~~~', '+ value', '  ^^^^^'],
])
def test_parsed_exc_multiline_source_rows(source_rows):
    text = ('Traceback (most recent call last):\n'
            '  File "outer.py", line 3, in outer\n'
            + ''.join('    ' + line + '\n' for line in source_rows)
            + '  File "inner.py", line 8, in inner\n'
            '    raise ValueError("first\\n    detail\\nlast")\n'
            'ValueError: first\n    detail\nlast')
    parsed = ParsedException.from_string(text)
    assert parsed.exc_type == 'ValueError'
    assert parsed.exc_msg == 'first\n    detail\nlast'
    assert len(parsed.frames) == 2
    assert parsed.frames[0]['filepath'] == 'outer.py'
    assert parsed.frames[1]['filepath'] == 'inner.py'
    assert parsed.frames[1]['source_line'] == (
        'raise ValueError("first\\n    detail\\nlast")')
    assert parsed.to_string() == text


def test_parsed_exc_multiline_source_indented():
    plain = ParsedException.from_string(_MULTILINE_TB_STR)
    indented = ParsedException.from_string(
        '\n'.join('    ' + line for line in _MULTILINE_TB_STR.splitlines()))
    assert indented.frames == plain.frames


def test_parsed_exc_multiline_source_truncated():
    text = _MULTILINE_TB_STR.rsplit('\n', 1)[0]
    parsed = ParsedException.from_string(text)
    assert parsed.exc_type == ''
    assert parsed.exc_msg == ''
    assert len(parsed.frames) == 2
    assert parsed.frames[-1]['source_line_continuations'] == [
        '+ "two"', '^~~~~~~']
    assert parsed.to_string().rstrip('\n') == text


@pytest.mark.skipif(sys.version_info < (3, 13),
                    reason='multiline traceback formatting requires Python 3.13')
def test_parsed_exc_multiline_source_from_traceback():
    def fail():
        return (
            1
            + "two"
        )

    try:
        fail()
    except TypeError as error:
        text = ''.join(traceback.format_exception(error))
        message = str(error)
    parsed = ParsedException.from_string(text)
    assert parsed.exc_type == 'TypeError'
    assert parsed.exc_msg == message
    assert len(parsed.frames) == 2
    assert parsed.frames[-1]['funcname'] == 'fail'
    assert parsed.frames[-1]['source_line'] == '1'
    assert '+ "two"' in parsed.frames[-1]['source_line_continuations']
    assert parsed.to_string() == text.rstrip('\n')


@pytest.mark.skipif(sys.version_info < (3, 13),
                    reason='multiline traceback formatting requires Python 3.13')
def test_parsed_exc_multiline_source_resembling_frame():
    def fail():
        return (
            """first
File "fake.py", line 123, in bogus
last"""
            + 1
        )

    try:
        fail()
    except TypeError as error:
        text = ''.join(traceback.format_exception(error))
        message = str(error)
    assert '    File "fake.py", line 123, in bogus' in text
    parsed = ParsedException.from_string(text)
    assert parsed.exc_type == 'TypeError'
    assert parsed.exc_msg == message
    assert len(parsed.frames) == 2
    assert parsed.frames[-1]['funcname'] == 'fail'
    assert all(frame['filepath'] != 'fake.py' for frame in parsed.frames)
    assert any('File "fake.py", line 123, in bogus' in line
               for line in parsed.frames[-1]['source_line_continuations'])
    assert parsed.to_string() == text.rstrip('\n')
