# -*- coding: utf-8 -*-

import re
from string import Formatter
from collections import namedtuple


_pos_farg_re = re.compile('({{)|'         # escaped open-brace
                          '(}})|'         # escaped close-brace
                          '({[:!.\[}])')  # anon positional format arg


def construct_format_field_str(fname, fspec, conv):
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
    ret = []
    for lit, fname, fspec, conv in fstr._formatter_parser():
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def infer_positional_format_args(fstr):
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


# tests follow

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


if __name__ == '__main__':
    test_tokenize_format_str()
    test_split_fstr()
    test_pos_infer()
    test_get_fstr_args()
