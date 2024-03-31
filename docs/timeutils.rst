``timeutils`` - ``datetime`` additions
======================================

.. automodule:: boltons.timeutils

.. autofunction:: daterange
.. autofunction:: isoparse
.. autofunction:: parse_timedelta
.. autofunction:: strpdate
.. autofunction:: total_seconds
.. autofunction:: dt_to_timestamp

.. autofunction:: relative_time
.. autofunction:: decimal_relative_time

General timezones
-----------------

By default, :class:`datetime.datetime` objects are "naïve", meaning
they lack attached timezone information. These objects can be useful
for many operations, but many operations require timezone-aware
datetimes.

The two most important timezones in programming are Coordinated
Universal Time (`UTC`_) and the local timezone of the host running
your code. Boltons provides two :class:`datetime.tzinfo` subtypes for
working with them:

.. _UTC: https://en.wikipedia.org/wiki/Coordinated_Universal_Time

.. note::

    These days, Python has a `built-in UTC`_, and the UTC tzinfo here, 
    while equivalent, is just for backwards compat.

.. autoattribute:: boltons.timeutils.UTC
.. autodata:: boltons.timeutils.LocalTZ

.. autoclass:: boltons.timeutils.ConstantTZInfo

.. _built-in UTC: https://docs.python.org/3/library/datetime.html#datetime.timezone.utc

US timezones
------------

These four US timezones were implemented in the :mod:`datetime`
documentation and have been reproduced here in boltons for
convenience. More in-depth support is provided by `dateutil`_ and `pytz`_.

.. _dateutil: https://dateutil.readthedocs.io/en/stable/index.html
.. _pytz: https://pypi.python.org/pypi/pytz

.. autoattribute:: boltons.timeutils.Eastern
.. autoattribute:: boltons.timeutils.Central
.. autoattribute:: boltons.timeutils.Mountain
.. autoattribute:: boltons.timeutils.Pacific

.. autoclass:: boltons.timeutils.USTimeZone
