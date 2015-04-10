# -*- coding: utf-8 -*-
"""Python's :mod:`datetime` module provides some of the most complex
and powerful primitives in the Python standard library. Time is
nontrivial, but thankfully its support is first-class in
Python. ``dateutils`` provides some additional tools for working with
time.

See :mod:`tzutils` for handy timezone-related boltons.
"""


import re
import bisect
import datetime
from datetime import timedelta


__all__ = ['total_seconds', 'parse_td', 'relative_time',
           'decimal_relative_time']


def total_seconds(td):
    """For those with older versions of Python, a pure-Python
    implementation of Python 2.7's :meth:`timedelta.total_seconds`.

    Args:
        td (datetime.timedelta): The timedelta to convert to seconds.
    Returns:
        float: total number of seconds

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


def parse_timedelta(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s')
    datetime.timedelta(1, 7410)

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day')
    datetime.timedelta(15)

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s')
    datetime.timedelta(-11, 43400)
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


parse_td = parse_timedelta  # legacy alias


def _cardinalize_time_unit(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit + 's'


def decimal_relative_time(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`datetime` objects or one :class:`datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.datetime.utcnow()
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')
    """
    if other is None:
        other = datetime.datetime.utcnow()
    diff = other - d
    diff_seconds = total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def relative_time(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`datetime` objects or one :class:`datetime` and
    now. Handles past and future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.datetime.utcnow()
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return '%g %s %s' % (abs(drt), unit, phrase)
