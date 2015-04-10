# -*- coding: utf-8 -*-
"""The Python :mod:`datetime` module's documentation describes how
to create a :class:`datetime.datetime`-compatible
:class:`datetime.tzinfo` subtype. It even provides a few examples.

The following module defines usable forms of the timezones in those
docs, as well as a couple other useful ones, :data:`UTC` (aka GMT) and
:data:`LocalTZ` (representing the local timezone). For timezones
beyond these, as well as a higher degree of accuracy, check out `pytz`_.

.. _pytz: https://pypi.python.org/pypi/pytz

"""


import time
from datetime import tzinfo, timedelta, datetime

# Basic timezones cribbed from etavta and Python docs.

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


# copied from timeutils for tzutils independence:
def total_seconds(td):
    """For those with older versions of Python, a pure-Python
    implementation of Python 2.7's :meth:`timedelta.total_seconds`.

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


class ConstantTZInfo(tzinfo):
    """
    A :class:`datetime.tzinfo` subtype whose *offset* remains constant
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


class LocalTZInfo(tzinfo):
    """The ``LocalTZInfo`` type takes data available in the time module about
    the local timezone and makes a practical tzinfo to represent the
    timezone settings of the operating system.
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
