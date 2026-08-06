from datetime import timedelta, date, datetime

import pytest

from boltons.timeutils import daterange, isoparse


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