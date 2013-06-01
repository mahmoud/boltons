# -*- coding: utf-8 -*-

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


import bisect

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
    """
    if other is None:
        other = datetime.datetime.utcnow()
    diff = other - d
    diff_seconds = total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect_left(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    float_diff = diff_seconds / total_seconds(bunit)
    rounded_diff = round(float_diff, ndigits)
    return rounded_diff, cardinalize(rounded_diff, bname)


def relative_time(d, other=None):
    # TODO: add decimal rounding factor (default 0)
    if other is None:
        other = datetime.datetime.utcnow()
    diff = other - d
    s, days = diff.seconds, diff.days
    if days > 7 or days < 0:
        return d.strftime('%d %b %y')
    elif days == 1:
        return '1 day ago'
    elif days > 1:
        return '{0} days ago'.format(diff.days)
    elif s < 5:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s / 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s / 3600)


if __name__ == '__main__':
    print decimal_relative_time(datetime.datetime.utcnow(), ndigits=5)
    print decimal_relative_time(datetime.datetime.utcnow() - timedelta(days=1, seconds=3600))
