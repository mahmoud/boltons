from datetime import timedelta, date, datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import boltons.timeutils

import pytest

from boltons.timeutils import daterange, isoparse, Eastern


def test_daterange_years():
    new_year = date(2017, 1, 1)
    bit_rollover = date(2038, 1, 19)

    new_years_remaining = daterange(new_year, bit_rollover, step=(1, 0, 0))
    assert len(list(new_years_remaining)) == 22

    y2025 = date(2025, 1, 1)
    bakers_years_til_2025 = list(daterange(new_year, y2025, step=(1, 1, 0)))
    assert len(bakers_years_til_2025) == 8
    assert bakers_years_til_2025[-1] == date(2024, 8, 1)
    assert bakers_years_til_2025[-1] == date(2024, 8, 1)

    years_from_2025 = list(daterange(y2025, new_year, step=(-1, 0, 0),
                                     inclusive=True))

    assert years_from_2025[0] == date(2025, 1, 1)
    assert years_from_2025[-1] == date(2017, 1, 1)


def test_daterange_years_step():
    start_day = date(year=2012, month=12, day=25)
    end_day = date(year=2016, month=1, day=1)
    dates = list(daterange(start_day, end_day, step=(1, 0, 0), inclusive=False))
    expected = [date(year=2012, month=12, day=25), date(year=2013, month=12, day=25), date(year=2014, month=12, day=25), date(year=2015, month=12, day=25)]

    assert dates == expected

    dates = list(daterange(start_day, end_day, step=(0, 13, 0), inclusive=False))
    expected = [date(year=2012, month=12, day=25), date(year=2014, month=1, day=25), date(year=2015, month=2, day=25)]
    assert dates == expected
    
    
def test_daterange_infinite():
    today = date.today()
    infinite_dates = daterange(today, None)
    for i in range(10):
        assert next(infinite_dates) == today + timedelta(days=i)


def test_daterange_with_same_start_stop():
    today = date.today()

    date_range = daterange(today, today)
    with pytest.raises(StopIteration):
        next(date_range)

    date_range_inclusive = daterange(today, today, inclusive=True)
    assert next(date_range_inclusive) == today
    with pytest.raises(StopIteration):
        next(date_range_inclusive)



def test_isoparse_basic():
    dt = datetime(2020, 1, 2, 3, 4, 5)
    assert isoparse(dt.isoformat()) == dt


def test_isoparse_fractional_seconds():
    # isoformat() round-trip at every timespec, not just microseconds
    dt = datetime(2020, 1, 2, 3, 4, 5, 851000)
    assert isoparse(dt.isoformat(timespec='milliseconds')) == dt
    assert isoparse(dt.isoformat(timespec='microseconds')) == dt
    assert isoparse(dt.isoformat()) == dt

    # leading zeros in the fraction scale correctly
    assert isoparse('2020-01-02T03:04:05.051').microsecond == 51000
    assert isoparse('2020-01-02T03:04:05.000001').microsecond == 1


def test_isoparse_fraction_overprecise():
    # digits past microsecond precision (e.g. nanosecond timestamps)
    # truncate rather than raise
    assert isoparse('2020-01-01T00:00:00.123456789').microsecond == 123456


def test_daterange_step_does_not_advance():
    start, stop = date(2020, 1, 1), date(2020, 3, 1)

    with pytest.raises(ValueError):
        list(daterange(start, stop, step=0))

    with pytest.raises(ValueError):
        list(daterange(start, stop, step=(0, 0, 0)))

    # month/day cancellation: +1 month, -31 days is stationary from Jan 1
    with pytest.raises(ValueError):
        list(daterange(start, stop, step=(0, 1, -31)))

    # non-advancing steps raise even for infinite ranges
    with pytest.raises(ValueError):
        list(daterange(start, None, step=0))


def test_daterange_wrong_direction():
    # a step pointed away from stop yields nothing, like range(1, 5, -1)
    assert list(daterange(date(2020, 1, 1), date(2020, 1, 5), step=-1)) == []
    assert list(daterange(date(2020, 1, 5), date(2020, 1, 1), step=1)) == []
    assert list(daterange(date(2020, 1, 1), date(2020, 3, 1),
                          step=(0, -1, 0))) == []


def test_daterange_datetime_hourly():
    # daterange accepts datetimes (datetime subclasses date) with
    # sub-day timedelta steps
    start = datetime(2020, 1, 1, 0)
    stop = datetime(2020, 1, 1, 12)
    hours = list(daterange(start, stop, step=timedelta(hours=3)))
    assert hours == [datetime(2020, 1, 1, 0), datetime(2020, 1, 1, 3),
                     datetime(2020, 1, 1, 6), datetime(2020, 1, 1, 9)]


def test_relative_time_defaults_to_matching_timezone():
    from datetime import datetime, timedelta, timezone
    from boltons.timeutils import decimal_relative_time, relative_time

    for tz in (None, timezone.utc, timezone(timedelta(hours=5, minutes=30))):
        now = (
            datetime.now(tz)
            if tz is not None
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )
        assert decimal_relative_time(now) == (0.0, 'seconds')
        assert relative_time(now) == '0 seconds ago'


def test_us_timezone_dst_fold():
    unfolded = datetime(2011, 11, 6, 1, 30, tzinfo=Eastern, fold=0)
    folded = datetime(2011, 11, 6, 1, 30, tzinfo=Eastern, fold=1)

    assert unfolded.utcoffset() == -4 * timedelta(hours=1)
    assert unfolded.tzname() == 'EDT'
    assert folded.utcoffset() == -5 * timedelta(hours=1)
    assert folded.tzname() == 'EST'


def test_us_timezone_fromutc_sets_fold():
    first = datetime(2011, 11, 6, 5, 30, tzinfo=timezone.utc).astimezone(Eastern)
    second = datetime(2011, 11, 6, 6, 30, tzinfo=timezone.utc).astimezone(Eastern)

    assert first.replace(tzinfo=None) == datetime(2011, 11, 6, 1, 30)
    assert first.fold == 0
    assert first.tzname() == 'EDT'
    assert second.replace(tzinfo=None) == datetime(2011, 11, 6, 1, 30)
    assert second.fold == 1
    assert second.tzname() == 'EST'


# Run with TZ established before importing timeutils, which caches the local
# standard and daylight offsets. The parent process's timezone never changes.
def _local_timezone_probe(tz, local, utc):
    code = """
import json
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, sys.argv[1])
time.tzset()
from boltons.timeutils import LocalTZInfo

zone = LocalTZInfo()
local, utc = json.loads(sys.argv[2])
def describe(dt):
    return [dt.replace(tzinfo=None).isoformat(), dt.fold,
            dt.utcoffset().total_seconds(), dt.dst().total_seconds(),
            dt.tzname(), dt.astimezone(timezone.utc).isoformat()]

result = {'local': [], 'utc': [], 'validation': [], 'system_utc': []}
for values in local:
    for fold in (0, 1):
        dt = datetime(*values, tzinfo=zone, fold=fold)
        result['local'].append(describe(dt))
for values in utc:
    dt = datetime(*values, tzinfo=timezone.utc)
    result['system_utc'].append(datetime.fromtimestamp(dt.timestamp()).isoformat())
    converted = dt.astimezone(zone)
    direct = zone.fromutc(dt.replace(tzinfo=zone))
    stamp = datetime.fromtimestamp(dt.timestamp(), zone)
    result['utc'].append([describe(converted), describe(direct), describe(stamp),
                          converted.tzinfo is zone])
for invalid in (None, 1, datetime(2011, 1, 1),
                datetime(2011, 1, 1, tzinfo=timezone.utc),
                datetime(2011, 1, 1, tzinfo=LocalTZInfo())):
    try:
        zone.fromutc(invalid)
    except Exception as exc:
        result['validation'].append(type(exc).__name__)
    else:
        result['validation'].append(None)
class DateTimeSubclass(datetime):
    pass
value = DateTimeSubclass(2011, 1, 1, microsecond=123456, tzinfo=zone)
converted = zone.fromutc(value)
result['subclass'] = [type(converted).__name__, converted.microsecond,
                      converted.tzinfo is zone]
far = datetime(2500, 1, 1, microsecond=999999, tzinfo=zone)
result['precision'] = zone.fromutc(far).astimezone(timezone.utc).isoformat()
print(json.dumps(result))
"""
    root = str(Path(boltons.timeutils.__file__).resolve().parent.parent)
    output = subprocess.check_output(
        [sys.executable, '-I', '-S', '-B', '-c', code, root,
         json.dumps([local, utc])],
        env=dict(os.environ, TZ=tz), text=True, timeout=20)
    return json.loads(output)


@pytest.mark.skipif(not hasattr(time, 'tzset'), reason='requires time.tzset')
@pytest.mark.parametrize('tz,overlap,gap,offsets,names,dst', [
    ('EST5EDT,M3.2.0/2,M11.1.0/2', (2011, 11, 6, 1, 30),
     (2011, 3, 13, 2, 30), (-14400, -18000), ('EDT', 'EST'), 3600),
    ('LHST-10:30LHDT-11,M10.1.0/2,M4.1.0/2', (2011, 4, 3, 1, 45),
     (2011, 10, 2, 2, 15), (39600, 37800), ('LHDT', 'LHST'), 1800),
])
def test_local_timezone_fold_and_gap(tz, overlap, gap, offsets, names, dst):
    result = _local_timezone_probe(tz, [overlap, gap], [])['local']
    assert [row[2] for row in result] == [*offsets, *reversed(offsets)]
    assert [row[3] for row in result] == [dst, 0, 0, dst]
    assert [row[4] for row in result] == [*names, *reversed(names)]
    # The two occurrences of a repeated wall time denote distinct instants.
    instants = [datetime.fromisoformat(row[5]) for row in result[:2]]
    assert instants[1] - instants[0] == timedelta(seconds=dst)


@pytest.mark.skipif(not hasattr(time, 'tzset'), reason='requires time.tzset')
@pytest.mark.parametrize('tz,utc,expected', [
    ('EST5EDT,M3.2.0/2,M11.1.0/2',
     [(2011, 11, 6, 5, 30, 0, 123456), (2011, 11, 6, 6, 30, 0, 123456),
      (2011, 3, 13, 6, 30), (2011, 3, 13, 7, 30),
      (2011, 11, 6, 5, 59, 59, 999999), (2011, 11, 6, 6),
      (2011, 3, 13, 6, 59, 59, 999999), (2011, 3, 13, 7)],
     [('2011-11-06T01:30:00.123456', 0, -14400, 3600, 'EDT'),
      ('2011-11-06T01:30:00.123456', 1, -18000, 0, 'EST'),
      ('2011-03-13T01:30:00', 0, -18000, 0, 'EST'),
      ('2011-03-13T03:30:00', 0, -14400, 3600, 'EDT'),
      ('2011-11-06T01:59:59.999999', 0, -14400, 3600, 'EDT'),
      ('2011-11-06T01:00:00', 1, -18000, 0, 'EST'),
      ('2011-03-13T01:59:59.999999', 0, -18000, 0, 'EST'),
      ('2011-03-13T03:00:00', 0, -14400, 3600, 'EDT')]),
    ('LHST-10:30LHDT-11,M10.1.0/2,M4.1.0/2',
     [(2011, 4, 2, 14, 45), (2011, 4, 2, 15, 15),
      (2011, 10, 1, 15, 15), (2011, 10, 1, 15, 45)],
     [('2011-04-03T01:45:00', 0, 39600, 1800, 'LHDT'),
      ('2011-04-03T01:45:00', 1, 37800, 0, 'LHST'),
      ('2011-10-02T01:45:00', 0, 37800, 0, 'LHST'),
      ('2011-10-02T02:45:00', 0, 39600, 1800, 'LHDT')]),
])
def test_local_timezone_fromutc(tz, utc, expected):
    result = _local_timezone_probe(tz, [], utc)
    for values, want, (converted, direct, stamp, same_zone) in zip(
            utc, expected, result['utc']):
        assert tuple(converted[:5]) == want
        assert converted == direct == stamp
        assert converted[5] == datetime(*values, tzinfo=timezone.utc).isoformat()
        assert same_zone
    assert result['validation'] == ['TypeError', 'TypeError', 'ValueError',
                                    'ValueError', 'ValueError']
    assert result['subclass'] == ['DateTimeSubclass', 123456, True]
    assert result['precision'] == '2500-01-01T00:00:00.999999+00:00'


@pytest.mark.skipif(not hasattr(time, 'tzset'), reason='requires time.tzset')
@pytest.mark.parametrize('tz,offsets,names,dst', [
    ('EST5EDT,M3.2.0/2,M11.1.0/2', (-18000, -14400), ('EST', 'EDT'), (0, 3600)),
    ('LHST-10:30LHDT-11,M10.1.0/2,M4.1.0/2', (39600, 37800),
     ('LHDT', 'LHST'), (1800, 0)),
    ('NPT-5:45', (20700, 20700), ('NPT', 'NPT'), (0, 0)),
])
def test_local_timezone_ordinary_times(tz, offsets, names, dst):
    dates = [(2011, 1, 15, 12, 0, 0, 999999), (2011, 7, 15, 12, 0, 0, 999999)]
    result = _local_timezone_probe(tz, dates, [])
    for i, values in enumerate(dates):
        first, second = result['local'][2 * i:2 * i + 2]
        assert first[0] == second[0] == datetime(*values).isoformat()
        assert first[2:] == second[2:]
        assert first[2:5] == [offsets[i], dst[i], names[i]]
    assert result['validation'] == ['TypeError', 'TypeError', 'ValueError',
                                    'ValueError', 'ValueError']
    assert result['subclass'] == ['DateTimeSubclass', 123456, True]
    assert result['precision'] == '2500-01-01T00:00:00.999999+00:00'


@pytest.mark.skipif(not hasattr(time, 'tzset'), reason='requires time.tzset')
def test_local_timezone_historical_offset_roundtrip():
    utc = (1985, 1, 1, 0, 0, 0, 123456)
    result = _local_timezone_probe('Asia/Kathmandu', [], [utc])
    # The IANA database is optional. Check its historical rule independently
    # of LocalTZInfo, whose documented generalization uses cached offsets.
    if result['system_utc'] != ['1985-01-01T05:30:00.123456']:
        pytest.skip('requires the historical Asia/Kathmandu timezone data')
    converted, direct, stamp, same_zone = result['utc'][0]
    assert converted == direct == stamp
    assert converted[5] == '1985-01-01T00:00:00.123456+00:00'
    assert same_zone
