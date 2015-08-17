# -*- coding: utf-8 -*-
"""Python's :mod:`datetime` module provides some of the most complex
and powerful primitives in the Python standard library. Time is
nontrivial, but thankfully its support is first-class in
Python. ``dateutils`` provides some additional tools for working with
time.

Additionally, timeutils provides a few basic utilities for working
with timezones in Python. The Python :mod:`datetime` module's
documentation describes how to create a
:class:`~datetime.datetime`-compatible :class:`~datetime.tzinfo`
subtype. It even provides a few examples.

The following module defines usable forms of the timezones in those
docs, as well as a couple other useful ones, :data:`UTC` (aka GMT) and
:data:`LocalTZ` (representing the local timezone as configured in the
operating system). For timezones beyond these, as well as a higher
degree of accuracy in corner cases, check out `pytz`_.

.. _pytz: https://pypi.python.org/pypi/pytz
"""

import re
import time
import bisect
from datetime import tzinfo, timedelta, datetime


def total_seconds(td):
    """For those with older versions of Python, a pure-Python
    implementation of Python 2.7's :meth:`~datetime.timedelta.total_seconds`.

    Args:
        td (datetime.timedelta): The timedelta to convert to seconds.
    Returns:
        float: total number of seconds

    >>> td = timedelta(days=4, seconds=33)
    >>> total_seconds(td)
    345633.0
    """
    a_milli = 1000000.0
    td_ds = td.seconds + (td.days * 86400)  # 24 * 60 * 60
    td_micro = td.microseconds + (td_ds * a_milli)
    return td_micro / a_milli


def dt_to_timestamp(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> abs(round(time.time() - dt_to_timestamp(datetime.utcnow()), 2))
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt - EPOCH_NAIVE
    return total_seconds(td)


_NONDIGIT_RE = re.compile('\D')


def isoparse(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.utcfromtimestamp(0)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.utcnow()
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = [int(p) for p in _NONDIGIT_RE.split(iso_str)]
    return datetime(*dt_args)


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
    :class:`~datetime.datetime` objects or one :class:`~datetime.datetime` and now.

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

    >>> now = datetime.utcnow()
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')
    """
    if other is None:
        other = datetime.utcnow()
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
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.utcnow()
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


# Timezone support (brought in from tzutils)


ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class ConstantTZInfo(tzinfo):
    """
    A :class:`~datetime.tzinfo` subtype whose *offset* remains constant
    (no daylight savings).

    Args:
        name (str): Name of the timezone.
        offset (datetime.timedelta): Offset of the timezone.
    """
    def __init__(self, name="ConstantTZ", offset=ZERO):
        self.name = name
        self.offset = offset

    @property
    def utcoffset_hours(self):
        return total_seconds(self.offset) / (60 * 60)

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(name=%r, offset=%r)' % (cn, self.name, self.offset)


UTC = ConstantTZInfo('UTC')
EPOCH_AWARE = datetime.fromtimestamp(0, UTC)
EPOCH_NAIVE = datetime.utcfromtimestamp(0)


class LocalTZInfo(tzinfo):
    """The ``LocalTZInfo`` type takes data available in the time module
    about the local timezone and makes a practical
    :class:`datetime.tzinfo` to represent the timezone settings of the
    operating system.

    For a more in-depth integration with the operating system, check
    out `tzlocal`_. It builds on `pytz`_ and implements heuristics for
    many versions of major operating systems to provide the official
    ``pytz`` tzinfo, instead of the LocalTZ generalization.

    .. _tzlocal: https://pypi.python.org/pypi/tzlocal
    .. _pytz: https://pypi.python.org/pypi/pytz

    """
    _std_offset = timedelta(seconds=-time.timezone)
    _dst_offset = _std_offset
    if time.daylight:
        _dst_offset = timedelta(seconds=-time.altzone)

    def is_dst(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def utcoffset(self, dt):
        if self.is_dst(dt):
            return self._dst_offset
        return self._std_offset

    def dst(self, dt):
        if self.is_dst(dt):
            return self._dst_offset - self._std_offset
        return ZERO

    def tzname(self, dt):
        return time.tzname[self.is_dst(dt)]

    def __repr__(self):
        return '%s()' % self.__class__.__name__


LocalTZ = LocalTZInfo()


def _first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


# US DST Rules
#
# This is a simplified (i.e., wrong for a few cases) set of rules for US
# DST start and end times. For a complete and up-to-date set of DST rules
# and timezone definitions, visit the Olson Database (or try pytz):
# http://www.twinsun.com/tz/tz-link.htm
# http://sourceforge.net/projects/pytz/ (might not be up-to-date)
#
# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday in March, which is the first Sunday on or after Mar 8.
DSTSTART_2007 = datetime(1, 3, 8, 2)
# and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
DSTEND_2007 = datetime(1, 11, 1, 1)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday in April and to end at 2am (DST time; 1am standard time) on the last
# Sunday of October, which is the first Sunday on or after Oct 25.
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 1)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday in April (the one on or after April 24) and to end at 2am (DST time;
# 1am standard time) on the last Sunday of October, which is the first Sunday
# on or after Oct 25.
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006


class USTimeZone(tzinfo):
    """Copied directly from the Python docs, the ``USTimeZone`` is a
    :class:`datetime.tzinfo` subtype used to create the
    :data:`Eastern`, :data:`Central`, :data:`Mountain`, and
    :data:`Pacific` tzinfo types.
    """
    def __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO


Eastern = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific = USTimeZone(-8, "Pacific",  "PST", "PDT")
