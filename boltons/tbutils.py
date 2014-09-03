# -*- coding: utf-8 -*-

"""Extract, format and print information about Python stack traces."""
from __future__ import print_function

import re
import sys
import linecache


# TODO: cross compatibility (jython, etc.)
# TODO: parser
# TODO: chaining primitives?  what are real use cases where these help?
# TODO: intelligently truncating repr

# TODO: print_* for backwards compatability
# __all__ = ['extract_stack', 'extract_tb', 'format_exception',
#            'format_exception_only', 'format_list', 'format_stack',
#            'format_tb', 'print_exc', 'format_exc', 'print_exception',
#            'print_last', 'print_stack', 'print_tb']


class Callpoint(object):
    __slots__ = ('func_name', 'lineno', 'module_name', 'module_path', 'lasti',
                 'line')  # line is for the actual single-line code content

    def __init__(self, module_name, module_path, func_name,
                 lineno, lasti, line=None):
        self.func_name = func_name
        self.lineno = lineno
        self.module_name = module_name
        self.module_path = module_path
        self.lasti = lasti
        self.line = line

    def to_dict(self):
        ret = {}
        for slot in self.__slots__:
            try:
                ret[slot] = getattr(self, slot)
            except AttributeError:
                pass
        return ret

    @classmethod
    def from_current(cls, level=1):
        frame = sys._getframe(level)
        return cls.from_frame(frame)

    @classmethod
    def from_frame(cls, frame):
        func_name = frame.f_code.co_name
        lineno = frame.f_lineno
        module_name = frame.f_globals.get('__name__', '')
        module_path = frame.f_code.co_filename
        lasti = frame.f_lasti
        line = _DeferredLine(module_path, lineno, frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    @classmethod
    def from_tb(cls, tb):
        # main difference with from_frame is that lineno and lasti
        # come from the traceback, which is to say the line that
        # failed in the try block, not the line currently being
        # executed (in the except block)
        func_name = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno
        lasti = tb.tb_lasti
        module_name = tb.tb_frame.f_globals.get('__name__', '')
        module_path = tb.tb_frame.f_code.co_filename
        line = _DeferredLine(module_path, lineno, tb.tb_frame.f_globals)
        return cls(module_name, module_path, func_name,
                   lineno, lasti, line=line)

    def __repr__(self):
        cn = self.__class__.__name__
        args = [getattr(self, s, None) for s in self.__slots__]
        if not any(args):
            return super(Callpoint, self).__repr__()
        else:
            return '%s(%s)' % (cn, ', '.join([repr(a) for a in args]))

    def tb_frame_str(self):
        ret = '  File "{0}", line {1}, in {2}\n'.format(self.module_path,
                                                        self.lineno,
                                                        self.func_name)
        if self.line:
            ret += '    {0}\n'.format(str(self.line))
        return ret


class _DeferredLine(object):
    def __init__(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        # TODO: this is going away when we fix linecache
        # TODO: (mark) read about loader
        self.module_globals = {}
        if module_globals is not None:
            for k in ('__name__', '__loader__'):
                v = module_globals.get(k)
                if v is None:
                    self.module_globals[k] = v

    def __eq__(self, other):
        return (self.lineno, self.filename) == (other.lineno, other.filename)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        if hasattr(self, '_line'):
            return self._line
        linecache.checkcache(self.filename)
        line = linecache.getline(self.filename,
                                 self.lineno,
                                 self.module_globals)
        line = line.strip()
        self._line = line
        return line

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return len(str(self))


class ExceptionInfo(object):
    def __init__(self, exc_type, exc_msg, tb_info):
        # TODO: additional fields for SyntaxErrors
        self.exc_type = exc_type
        self.exc_msg = exc_msg
        self.tb_info = tb_info

    @classmethod
    def from_exc_info(cls, exc_type, exc_value, traceback):
        type_str = exc_type.__name__
        type_mod = exc_type.__module__
        if type_mod not in ("__main__", "__builtin__", "exceptions"):
            type_str = '%s.%s' % (type_mod, type_str)
        val_str = _some_str(exc_value)
        tb_info = TracebackInfo.from_traceback(traceback)
        return cls(type_str, val_str, tb_info)

    @classmethod
    def from_current(cls):
        return cls.from_exc_info(*sys.exc_info())

    def __repr__(self):
        cn = self.__class__.__name__
        try:
            len_frames = len(self.tb_info.frames)
            last_frame = ', last=%r' % (self.tb_info.frames[-1],)
        except:
            len_frames = 0
            last_frame = ''
        args = (cn, self.exc_type, self.exc_msg, len_frames, last_frame)
        return '<%s [%s: %s] (%s frames%s)>' % args


# TODO: dedup frames, look at __eq__ on _DeferredLine
# TODO: StackInfo/TracebackInfo split, latter stores exc
class TracebackInfo(object):
    def __init__(self, frames):
        self.frames = frames

    @classmethod
    def from_frame(cls, frame, limit=None):
        ret = []
        if frame is None:
            frame = sys._getframe(1)  # cross-impl yadayada
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while frame is not None and n < limit:
            item = Callpoint.from_frame(frame)
            ret.append(item)
            frame = frame.f_back
            n += 1
        ret.reverse()
        return cls(ret)

    @classmethod
    def from_traceback(cls, tb, limit=None):
        ret = []
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', 1000)
        n = 0
        while tb is not None and n < limit:
            item = Callpoint.from_tb(tb)
            ret.append(item)
            tb = tb.tb_next
            n += 1
        return cls(ret)

    @classmethod
    def from_dict(cls, d):
        return cls(d['frames'])

    def to_dict(self):
        return {'frames': [f.to_dict() for f in self.frames]}

    def __len__(self):
        return len(self.frames)

    def __iter__(self):
        return iter(self.frames)

    def __repr__(self):
        class_name = self.__class__.__name__

        if self.frames:
            frame_part = ' last={0}'.format(repr(self.frames[-1]))
        else:
            frame_part = ''

        return ('<{class_name} frames={nframes}{frame_part}>'
                .format(class_name=class_name,
                        nframes=len(self),
                        frame_part=frame_part))

    def __str__(self):
        ret = 'Traceback (most recent call last):\n'
        ret += ''.join([f.tb_frame_str() for f in self.frames])
        return ret


# TODO: clean up & reimplement -- specifically for syntax errors
def format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    # Gracefully handle (the way Python 2.4 and earlier did) the case of
    # being called with (None, None).
    if etype is None:
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__
    smod = etype.__module__
    if smod not in ("__main__", "builtins", "exceptions"):
        stype = smod + '.' + stype

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    filename = value.filename or "<string>"
    lineno = str(value.lineno) or '?'
    lines.append('  File "%s", line %s\n' % (filename, lineno))
    badline = value.text
    offset = value.offset
    if badline is not None:
        lines.append('    %s\n' % badline.strip())
        if offset is not None:
            caretspace = badline.rstrip('\n')[:offset].lstrip()
            # non-space whitespace (likes tabs) must be kept for alignment
            caretspace = ((c.isspace() and c or ' ') for c in caretspace)
            # only three spaces to account for offset1 == pos 0
            lines.append('   %s^\n' % ''.join(caretspace))
    msg = value.msg or "<no detail available>"
    lines.append("%s: %s\n" % (stype, msg))
    return lines


# TODO: use asciify, improved if necessary
def _some_str(value):
    try:
        return str(value)
    except Exception:
        pass
    try:
        value = unicode(value)
        return value.encode("ascii", "backslashreplace")
    except Exception:
        pass
    return '<unprintable %s object>' % type(value).__name__


def _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = "%s: %s\n" % (etype, valuestr)
    return line


def print_exception(etype, value, tb, limit=None, file=None):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """

    if file is None:
        file = sys.stderr
    if tb:
        tbi = TracebackInfo.from_traceback(tb, limit)
        print(str(tbi), end='', file=file)

    for line in format_exception_only(etype, value):
        print(line, end='', file=file)


def fix_print_exception():
    sys.excepthook = print_exception


_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)'
                       r', in (?P<funcname>.+)$')
_se_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)')


class ParsedTB(object):
    """
    Parses a traceback string as typically output by sys.excepthook.
    """
    def __init__(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(frames or [])

    @property
    def source_file(self):
        try:
            return self.frames[-1]['filepath']
        except IndexError:
            return None

    def to_dict(self):
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': self.frames}

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(%r, %r, frames=%r)'
                % (cn, self.exc_type, self.exc_msg, self.frames))

    @classmethod
    def from_string(cls, tb_str):
        if not isinstance(tb_str, unicode):
            tb_str = tb_str.decode('utf-8')
        tb_lines = tb_str.lstrip().splitlines()
        if tb_lines[0].strip() == 'Traceback (most recent call last):':
            frame_lines = tb_lines[1:-1]
            frame_re = _frame_re
        elif len(tb_lines) > 1 and tb_lines[-2].lstrip().startswith('^'):
            frame_lines = tb_lines[:-2]
            frame_re = _se_frame_re
        else:
            raise ValueError('unrecognized traceback string format')
        while tb_lines:
            cl = tb_lines[-1]
            if cl.startswith('Exception ') and cl.endswith('ignored'):
                # handle some ignored exceptions
                tb_lines.pop()
            else:
                break
        for line in reversed(tb_lines):
            # get the bottom-most line that looks like an actual Exception
            # repr(), (i.e., "Exception: message")
            exc_type, sep, exc_msg = line.partition(':')
            if sep and exc_type and len(exc_type.split()) == 1:
                break

        frames = []
        for pair_idx in range(0, len(frame_lines), 2):
            frame_line = frame_lines[pair_idx].strip()
            frame_match = frame_re.match(frame_line)
            if frame_match:
                frame_dict = frame_match.groupdict()
            else:
                continue
            frame_dict['source_line'] = frame_lines[pair_idx + 1].strip()
            frames.append(frame_dict)

        return cls(exc_type, exc_msg, frames)


if __name__ == '__main__':
    import cStringIO

    builtin_exc_hook = sys.excepthook
    fix_print_exception()
    tbi_str = ''

    def test():
        raise ValueError('yay fun')

    fake_stderr1 = cStringIO.StringIO()
    fake_stderr2 = cStringIO.StringIO()
    sys.stderr = fake_stderr1

    try:
        test()
    except:
        _, _, exc_traceback = sys.exc_info()
        tbi = TracebackInfo.from_traceback(exc_traceback)
        exc_info = ExceptionInfo.from_exc_info(*sys.exc_info())
        exc_info2 = ExceptionInfo.from_current()
        tbi_str = str(tbi)
        print_exception(*sys.exc_info(), file=fake_stderr2)
        new_exc_hook_res = fake_stderr2.getvalue()
        builtin_exc_hook(*sys.exc_info())
        builtin_exc_hook_res = fake_stderr1.getvalue()
    finally:
        sys.stderr = sys.__stderr__

    print()
    print('# Single frame:\n')
    print(tbi.frames[-1].tb_frame_str())

    print('# Traceback info:\n')
    print(tbi_str)

    print('# Full except hook output:\n')
    print(new_exc_hook_res)

    assert new_exc_hook_res == builtin_exc_hook_res

    FAKE_TB_STR = u"""
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    plarp
NameError: name 'plarp' is not defined
"""
    parsed_tb = ParsedTB.from_string(FAKE_TB_STR)
    print(parsed_tb)

    def func1():
        return func2()
    def func2():
        return func3()
    def func3():
        return Callpoint.from_current(level=2)

    callpoint = func1()
    print(repr(callpoint))
    assert 'func2' in repr(callpoint)
