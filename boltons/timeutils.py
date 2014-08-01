# -*- coding: utf-8 -*-

import re
import bisect
import datetime
from datetime import timedelta
from strutils import cardinalize


def total_seconds(td):
    """\
    A pure-Python implementation of Python 2.7's timedelta.total_seconds().

    Accepts a timedelta object, returns number of total seconds.

    >>> td = datetime.timedelta(days=4, seconds=33)
    >>> total_seconds(td)
    345633.0
    """
    a_milli = 1000000.0
    td_ds = td.seconds + (td.days * 86400)  # 24 * 60 * 60
    td_micro = td.microseconds + (td_ds * a_milli)
    return td_micro / a_milli


_BOUNDS = [(0, timedelta(seconds=1), 'second'),
           (1, timedelta(seconds=60), 'minute'),
           (1, timedelta(seconds=3600), 'hour'),
           (1, timedelta(days=1), 'day'),
           (1, timedelta(days=7), 'week'),
           (2, timedelta(days=30), 'month'),
           (1, timedelta(days=365), 'year')]
_BOUNDS = [(b[0] * b[1], b[1], b[2]) for b in _BOUNDS]
_BOUND_DELTAS = [b[0] for b in _BOUNDS]

_FLOAT_PATTERN = r'[+-]?\ *(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
_PARSE_TD_RE = re.compile("((?P<value>%s)\s*(?P<unit>\w)\w*)" % _FLOAT_PATTERN)
_PARSE_TD_KW_MAP = dict([(unit[0], unit + 's')
                         for _, _, unit in reversed(_BOUNDS[:-2])])


def parse_td(text):
    """\
    Robustly parses a short text description of a time period into a
    timedelta. Supports weeks, days, hours, minutes, and seconds.

    >>> parse_td('1d 2h 3.5m 0s')
    datetime.timedelta(1, 7410)

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day')
    datetime.timedelta(15)

    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def decimal_relative_time(d, other=None, ndigits=0):
    """\
    >>> now = datetime.datetime.utcnow()
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now - timedelta(days=1000), now, ndigits=1)
    (2.7, 'years')
    """
    if other is None:
        other = datetime.datetime.utcnow()
    diff = other - d
    diff_seconds = total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    #f_diff, f_mod = divmod(diff_seconds, total_seconds(bunit))
    f_diff = diff_seconds / total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    return rounded_diff, cardinalize(bname, abs(rounded_diff))


def relative_time(d, other=None, ndigits=0):
    """\
    >>> now = datetime.datetime.utcnow()
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'
    """
    drt, unit = decimal_relative_time(d, other, ndigits)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return '%g %s %s' % (abs(drt), unit, phrase)
