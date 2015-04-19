from __future__ import absolute_import
from __future__ import unicode_literals

from boltons.tbutils import ParsedException


def test_normal_tb():
    tb = '''\
Traceback (most recent call last):
  File "<string>", line 2, in _some_function
    return some_other_function(1)
  File "myfile.py", line 3, in some_other_function
    return foo(bar, baz)
MyException: ExceptionValue
'''
    parsed = ParsedException.from_string(tb)
    assert parsed.exc_type == 'MyException'
    assert parsed.exc_msg == ' ExceptionValue'
    assert parsed.frames == [
        {
            'source_line': 'return some_other_function(1)',
            'filepath': '<string>',
            'lineno': '2',
            'funcname': '_some_function'
        },
        {
            'source_line': 'return foo(bar, baz)',
            'filepath': 'myfile.py',
            'lineno': '3',
            'funcname': 'some_other_function',
        }
    ]


def test_eval_tb():
    tb = '''\
Traceback (most recent call last):
  File "<string>", line 2, in _some_function
  File "myfile.py", line 3, in some_other_function
    return foo(bar, baz)
MyException: ExceptionValue
'''
    parsed = ParsedException.from_string(tb)
    assert parsed.exc_type == 'MyException'
