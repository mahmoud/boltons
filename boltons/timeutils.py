# -*- coding: utf-8 -*-

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


def decimal_relative_time(d, other=None, ndigits=0):
    """\
    >>> now = datetime.datetime.utcnow()
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> '%g %s' % _
    '0.002 seconds'
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
