"""Extract, format and print information about Python stack traces."""
from __future__ import print_function

from collections import namedtuple
import linecache
import sys

# TODO: cross compatibility (jython, etc.)
# TODO: parser
# TODO: chaining primitives?  what are real use cases where these help?

# TODO: print_* for backwards compatability
# __all__ = ['extract_stack', 'extract_tb', 'format_exception',
#            'format_exception_only', 'format_list', 'format_stack',
#            'format_tb', 'print_exc', 'format_exc', 'print_exception',
#            'print_last', 'print_stack', 'print_tb']


class FrameInfo(namedtuple('FrameInfo', 'filename, lineno, name, line')):
    # TODO: intelligently truncating repr

    def __str__(self):
        header = '  File "{0}", line {1}, in {2}\n'.format(self.filename,
                                                           self.lineno,
                                                           self.name)
        ret = header
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
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            name = frame.f_code.co_name
            line = _DeferredLine(filename, lineno, frame.f_globals)
            item = FrameInfo(filename, lineno, name, line)
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
            filename = tb.tb_frame.f_code.co_filename
            lineno = tb.tb_lineno
            name = tb.tb_frame.f_code.co_name
            line = _DeferredLine(filename, lineno, tb.tb_frame.f_globals)
            item = FrameInfo(filename, lineno, name, line)
            ret.append(item)
            tb = tb.tb_next
        n += 1
        return cls(ret)

    @classmethod
    def from_dict(cls, d):
        # TODO: respect message, exception; part of
        # StackInfo/TracebackInfo split
        return cls(d['frames'])

    def to_dict(self):
        # TODO: fill in message, exception; part of
        # StackInfo/TracebackInfo split
        return {'frames': [f._asdict() for f in self],
                'message': None,
                'exception': None}

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
        header = 'Traceback (most recent call last):\n'
        return header + ''.join(str(f) for f in self)


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


if __name__ == '__main__':
    fix_print_exception()

    def test():
        raise ValueError

    try:
        test()
    except:
        _, _, exc_traceback = sys.exc_info()
        tbi = TracebackInfo.from_traceback(exc_traceback)
        print(repr(tbi))
        print(tbi.frames[-1]._asdict())

    test()
