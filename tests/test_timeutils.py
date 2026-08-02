from datetime import timedelta, date, datetime, timezone

import pytest

from boltons.timeutils import daterange, Eastern


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
