# -*- coding: utf-8 -*-
"""\
New-style string formatting (i.e., bracket-style/{}-style) brought a
lot of power and features over old-style (%-style) string formatting,
but it is far from without its own faults. Besides being more verbose
and substantially slower, it is lacking a lot of useful
instrumentation. The `formatutils` module provides useful format
string introspection and manipulation functions.
"""


import re
from string import Formatter
from collections import namedtuple


_pos_farg_re = re.compile('({{)|'         # escaped open-brace
                          '(}})|'         # escaped close-brace
                          '({[:!.\[}])')  # anon positional format arg


def construct_format_field_str(fname, fspec, conv):
    """
    Constructs a format field string from the field name, spec, and
    conversion character (``fname``, ``fspec``, ``conv``). See Python
    String Formatting for more info.
    """
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def split_format_str(fstr):
    """\
    Does very basic spliting of a format string, returns a list of
    strings. For full tokenization, see :func:`tokenize_format_str`.
    """
    ret = []
    for lit, fname, fspec, conv in fstr._formatter_parser():
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def infer_positional_format_args(fstr):
    """\
    Takes format strings with anonymous positional arguments, (e.g.,
    "{}" and {:d}), and converts them into numbered ones for explicitness and
    compatibility with 2.6.

    Returns a string with the inferred positional arguments.
    """
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += '{%s%s' % (max_anon, group[1:])
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


_INTCHARS = 'bcdoxXn'
_FLOATCHARS = 'eEfFgGn%'
_TYPE_MAP = dict([(x, int) for x in _INTCHARS] +
                 [(x, float) for x in _FLOATCHARS])
_TYPE_MAP['s'] = str


def get_format_args(fstr):
    """
    Turn a format string into two lists of arguments referenced by the
    format string. One is positional arguments, and the other is named
    arguments. Each element of the list includes the name and the
    nominal type of the field.

    >>> get_format_args("{noun} is {1:d} years old{punct}")
    ([(1, <type 'int'>)], [('noun', <type 'str'>), ('punct', <type 'str'>)])
    """
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def tokenize_format_str(fstr, resolve_pos=True):
    """\
    Takes a format string, turns it into a list of alternating string
    literals and :class:`BaseFormatField` tokens. By default, also
    infers anonymous positional references into explict, numbered
    positional references. To disable this behavior set `resolve_pos`
    to `False`.
    """
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


class BaseFormatField(object):
    """\
    A class representing a reference to an argument inside of a
    new-style format string. For instance, in "{greeting}, world!",
    there is a field called "greeting".

    These fields can have a lot of options applied to them. See the
    Python docs on Format String Syntax for the full details:
    https://docs.python.org/2/library/string.html#formatstrings
    """
    def __init__(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(conv)

    def set_fname(self, fname):
        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def set_fspec(self, fspec):
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in fspec._formatter_parser():
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def set_conv(self, conv):
        "!s and !r, etc."
        # TODO
        self.conv = conv
        self.conv_func = None  # TODO

    @property
    def fstr(self):
        return construct_format_field_str(self.fname, self.fspec, self.conv)

    def __repr__(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return '%s(%s)' % (cn, args_repr)

    def __str__(self):
        return self.fstr


_UNSET = object()


class DeferredValue(object):
    """DeferredValue is a wrapper type, used to defer computing values
    which would otherwise be expensive to stringify and format. This
    is most valuable in areas like logging, where one would not want
    to waste time formatting a value for a log message which will
    subsequently be filtered because the message's log level was DEBUG
    and the logger was set to only emit CRITICAL messages.

    The DeferredValue is initialized with a callable that takes no
    arguments and returns the value, which can be of any type. By
    default DeferredValue only calls that callable once, and future
    references will get a cached value. This behavior can be disabled
    by setting `cache_value` to `False`.

    >>> import sys
    >>> dv = DeferredValue(lambda: len(sys._current_frames()))
    >>> output = "works great in all {0} threads!".format(dv)

    PROTIP: from formatutils import DeferredValue as DV  # keeps lines shorter
    """
    def __init__(self, func, cache_value=True):
        self.func = func
        self.cache_value = True
        self._value = _UNSET

    def get_value(self):
        if self._value is _UNSET or not self.cache_value:
            value = self.func()
        if self.cache_value:
            self._value = value
        return value

    def __int__(self):
        return int(self.get_value())

    def __float__(self):
        return float(self.get_value())

    def __str__(self):
        return str(self.get_value())

    def __unicode__(self):
        return unicode(self.get_value())

    def __repr__(self):
        return repr(self.get_value())

    def __format__(self, fmt):
        value = self.get_value()

        pt = fmt[-1:]  # presentation type
        type_conv = _TYPE_MAP.get(pt, str)

        try:
            return value.__format__(fmt)
        except (ValueError, TypeError):
            # TODO: this may be overkill
            return type_conv(value).__format__(fmt)


# tests follow

if __name__ == '__main__':

    PFAT = namedtuple("PositionalFormatArgTest", "fstr arg_vals res")

    _PFATS = [PFAT('{} {} {}', ('hi', 'hello', 'bye'), "hi hello bye"),
              PFAT('{:d} {}', (1, 2), "1 2"),
              PFAT('{!s} {!r}', ('str', 'repr'), "str 'repr'"),
              PFAT('{[hi]}, {.__name__!r}', ({'hi': 'hi'}, re), "hi, 're'"),
              PFAT('{{joek}} ({} {})', ('so', 'funny'), "{joek} (so funny)")]

    def test_pos_infer():
        for i, (tmpl, args, res) in enumerate(_PFATS):
            converted = infer_positional_format_args(tmpl)
            assert converted.format(*args) == res


    _TEST_TMPLS = ["example 1: {hello}",
                   "example 2: {hello:*10}",
                   "example 3: {hello:*{width}}",
                   "example 4: {hello!r:{fchar}{width}}, {width}, yes",
                   "example 5: {0}, {1:d}, {2:f}, {1}",
                   "example 6: {}, {}, {}, {1}"]

    def test_get_fstr_args():
        results = []
        for t in _TEST_TMPLS:
            inferred_t = infer_positional_format_args(t)
            res = get_format_args(inferred_t)
            #print res
            results.append(res)
        return results

    def test_split_fstr():
        results = []
        for t in _TEST_TMPLS:
            res = split_format_str(t)
            #print res
            results.append(res)
        return results

    def test_tokenize_format_str():
        results = []
        for t in _TEST_TMPLS:
            res = tokenize_format_str(t)
            print ''.join([str(r) for r in res])
            results.append(res)
        return results

    test_tokenize_format_str()
    test_split_fstr()
    test_pos_infer()
    test_get_fstr_args()
