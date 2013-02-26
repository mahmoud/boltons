import sys
import traceback
import linecache
from collections import namedtuple

from pprint import pprint


class ExceptionCauseMixin(Exception):
    def __init__(self, *args, **kwargs):
        cause = kwargs.pop('cause', None)
        super(ExceptionCauseMixin, self).__init__(*args, **kwargs)
        if not cause:
            return
        if not isinstance(cause, Exception):
            return  # TODO: use current exception instead?

        if isinstance(cause, ExceptionCauseMixin):
            self.cause = cause.cause
            self.cause_type = cause.cause_type
            self.full_trace = cause.full_trace
            return

        self.cause = cause
        self.cause_type = type(cause)
        try:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_value is cause:
                self._tb = _extract_from_tb(exc_tb)
                self._stack = _extract_from_frame(exc_tb.tb_frame)
                full_trace = self._stack[:-1] + self._tb
                self.full_trace = full_trace
                #pprint(self.full_trace)
        finally:
            del exc_tb

    def __str__(self):
        ret = []
        if self.full_trace:
            ret.append('Traceback (most recent call last):\n')
            ret.extend(traceback.format_list(self.full_trace))
        ret.append(self.__class__.__name__)
        ret.append(' caused by ')
        ret.extend(traceback.format_exception_only(self.cause_type,
                                                   self.cause))
        return ''.join(ret)


_BaseTBItem = namedtuple('_BaseTBItem', 'filename, lineno, name, line')


class _TBItem(_BaseTBItem):
    def __repr__(self):
        ret = super(_TBItem, self).__repr__()
        ret += ' <%r>' % self.frame_id
        return ret


class _DeferredLine(object):
    def __init__(self, filename, lineno, module_globals=None):
        self.filename = filename
        self.lineno = lineno
        module_globals = module_globals or {}
        self.module_globals = dict([(k, v) for k, v in module_globals.items()
                                    if k in ('__name__', '__loader__')])

    def __eq__(self, other):
        return (self.lineno, self.filename) == (other.lineno, other.filename)

    def __ne__(self, other):
        return (self.lineno, self.filename) != (other.lineno, other.filename)

    def __str__(self):
        if hasattr(self, '_line'):
            return self._line
        linecache.checkcache(self.filename)
        line = linecache.getline(self.filename,
                                 self.lineno,
                                 self.module_globals)
        if line:
            line = line.strip()
        else:
            line = None
        self._line = line
        return line

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return len(str(self))

    def strip(self):
        return str(self).strip()


def _extract_from_frame(f=None, limit=None):
    ret = []
    if f is None:
        f = sys._getframe(1)  # cross-impl yadayada
    if limit is None:
        limit = getattr(sys, 'tracebacklimit', 1000)
    n = 0
    while f is not None and n < limit:
        filename = f.f_code.co_filename
        lineno = f.f_lineno
        name = f.f_code.co_name
        line = _DeferredLine(filename, lineno, f.f_globals)
        item = _TBItem(filename, lineno, name, line)
        item.frame_id = id(f)
        ret.append(item)
        f = f.f_back
        n += 1
    ret.reverse()
    return ret


def _extract_from_tb(tb, limit=None):
    ret = []
    if limit is None:
        limit = getattr(sys, 'tracebacklimit', 1000)
    n = 0
    while tb is not None and n < limit:
        filename = tb.tb_frame.f_code.co_filename
        lineno = tb.tb_lineno
        name = tb.tb_frame.f_code.co_name
        line = _DeferredLine(filename, lineno, tb.tb_frame.f_globals)
        item = _TBItem(filename, lineno, name, line)
        item.frame_id = id(tb.tb_frame)
        ret.append(item)
        tb = tb.tb_next
        n += 1
    return ret


class MathError(ExceptionCauseMixin):
    pass


def whoops_math():
    return 1/0


def math_lol(n=0):
    if n < 3:
        return math_lol(n=n+1)
    try:
        return whoops_math()
    except ZeroDivisionError as zde:
        exc = MathError(cause=zde)
        raise exc

def main():
    try:
        math_lol()
    except MathError as me:
        exc = MathError(cause=me)
    print str(exc)
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    try:
        main()
    except:
        import pdb;pdb.post_mortem()
        raise
