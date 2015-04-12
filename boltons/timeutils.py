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
import math
import time
import datetime
from datetime import timedelta

# optional dependency: monotonic time
try:
    # python3.3 added monotonic time to stdlib
    monotonic = time.monotonic
except AttributeError:
    try:
        from importlib import import_module
    except ImportError:
        monotonic = None # py2.6
    else:
        # lib name, function that gets value given module (in order of preference)
        _monotonic_libs = [
            ('monotonic', lambda module: module.monotonic()),
            ('monotime', lambda module: module.monotonic()),
            ('monoclock', lambda module: module.nano_count() / 1e9),
        ]
        for _lib, _func in _monotonic_libs:
            try:
                _monotonic_module = import_module(_lib)
            except (ImportError, RuntimeError):
                # "monotonic" will raise RuntimeError if no implementation for platform
                continue
            monotonic = lambda: _func(_monotonic_module)
            break
        else:
            monotonic = None


__all__ = ['total_seconds', 'parse_td', 'relative_time',
           'decimal_relative_time', 'DecayCounter']


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


class DecayCounter(object):
    """Implements a counter whose value decays over time

    DecayCounter() objects store a float, which decays over time with the given decay rate.
    Decay rate is expressed as a half-life, ie. after half_life seconds, the value is halved.
    The decay is automatically accounted for on a get() operation, no background thread or
    other out-of-band timekeeping is used.

    Note that while a set() operation is provided, it is not safe to use
    in a read-modify-write pattern, as you would lose the decay that should have occurred
    between the read and the write.
    You should instead use modify() for such operations, which takes a callable that
    should perform the operation and return the result, eg:
    >>> import time
    >>> approx_equal = lambda x, y: abs(x - y) < 0.1
    >>> counter = DecayCounter(halflife=1, initial=10)
    >>> time.sleep(1)
    >>> approx_equal(counter.get(), 5)
    True
    >>> # counter.set(counter.get() * 2)  # BAD!
    >>> counter.modify(lambda value: value * 2)  # GOOD!
    >>> approx_equal(counter.get(), 10)
    True

    If one of the following libraries is installed, monotonic time will be used by default:
        Monotime
        Monoclock
        monotonic
        (or if python version is >= 3.3)
    If you would like to enforce this as a requirement, set the use_monotonic=True flag.
    Conversely, if you would like to force the use of wall clock time.time()
    even when monotonic is available, set use_monotonic=False. Note this is probably a bad idea
    (for example, your values will jump up wildly if the system time is changed backwards).
    """

    def __init__(self, halflife, initial=0, use_monotonic=None):
        """Half-life is expressed in seconds.
        If use_monotonic is given and True, force the use of monotonic time or fail with ValueError().
        If use_monotonic is given and False, force the use of time.time() even if monotonic time is available.
        If use_monotonic is not given, use monotonic time if available, else time.time().
        """
        if use_monotonic and monotonic is None:
            raise ValueError("System does not support monotonic time")
        self._halflife = halflife
        self._monotonic = (monotonic is not None) if use_monotonic is None else use_monotonic
        self._update(initial, self._get_time())

    @property
    def halflife(self):
        return self._halflife
    @halflife.setter
    def halflife(self, halflife):
        # we want to apply the old half life up until now, then change it.
        value, time = self._get()
        self._update(value, time)
        self._halflife = halflife

    def get(self):
        """Returns the current value, taking into account any decay since last set"""
        value, time = self._get()
        return value

    def modify(self, func):
        """Safely read, modify, then write the value. Func should be a callable that takes one arg,
        the current value, and returns the new value.
        For example:
            def double(counter):
                counter.modify(lambda value: value * 2)
        """
        value, time = self._get()
        value = func(value)
        self._update(value, time)

    def copy(self):
        """Return a new instance of DecayCounter() with the same halflife as the current counter,
        and initially the same value."""
        return DecayCounter(self.halflife, self.get(), monotonic=self._monotonic)

    def set(self, value):
        """Sets the value. Note that this method is only safe when setting to a constant value
        ie. it is not safe to read the value, modify it, then set it. This will cause there to be no
        decay applied for the period of time between your get() and your set()."""
        # As it turns out, set is really just a special case of modify
        self.modify(lambda old: value)

    def add(self, amount):
        """Add amount to value (amount can be negative). A shortcut for modify(lambda value: value + amount)."""
        self.modify(lambda value: value + amount)

    def _get_time(self):
        """Returns the current time, by whatever counting method is in use.
        Subclasses should override this to implement alternate timekeeping.
        """
        return monotonic() if self._monotonic else time.time()

    def _get(self):
        """Returns the current value, along with the point in time when that value was taken"""
        # We calculate the current value based on decay and time since last set
        # We could update on every get, but there's no need (and I suspect it might lead to floating
        #  point errors if you get() in rapid succession)
        decay_exponent = -math.log(2) / self.halflife
        current_time = self._get_time()
        elapsed = current_time - self._time
        current_value = self._value * math.exp(decay_exponent * elapsed)
        return current_value, current_time

    def _update(self, value, time):
        """Underlying function that updates the value and time"""
        self._value = value
        self._time = time

