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

def test_parsed_exc_with_anchor():
    """parse a traceback with anchor lines beneath source lines"""
    _tb_str = """\
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(add(1, "two"))
          ^^^^^^^^^^^^^
  File "add.py", line 2, in add
    return a + b
           ~~^~~
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""

    parsed_tb = ParsedException.from_string(_tb_str)

    assert parsed_tb.exc_type == 'TypeError'
    assert parsed_tb.exc_msg == "unsupported operand type(s) for +: 'int' and 'str'"
    assert parsed_tb.frames == [{'source_line': 'print(add(1, "two"))',
                                  'filepath': 'main.py',
                                  'lineno': '3',
                                  'funcname': '<module>'},
                                  {'source_line': 'return a + b',
                                  'filepath': 'add.py',
                                  'lineno': '2',
                                  'funcname': 'add'}]
    
    # Note: not checking the anchor lines (indices 3, 6) because column details not currently stored in ParsedException
    _tb_str_lines = _tb_str.splitlines()
    _tb_str_without_anchor = "\n".join(_tb_str_lines[:3] + _tb_str_lines[4:6] + _tb_str_lines[7:])
    assert parsed_tb.to_string() == _tb_str_without_anchor