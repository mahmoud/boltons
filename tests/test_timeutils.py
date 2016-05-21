
from datetime import timedelta, date
from boltons.timeutils import total_seconds, daterange


def test_float_total_seconds():
    """Check for floating point precision loss per
    http://bugs.python.org/issue8644 and tests in the corresponding
    diff, spurred by
    https://github.com/mahmoud/boltons/pull/13#issuecomment-93835612 .

    The funny thing is that floating point precision loss is
    definitely happening. With or without true division, in Python
    2.7's native timedelta.total_seconds() as well as
    dateutils.total_seconds. The constants in the tests below are from
    manual tests on Python 2.7.6 final. 2.6 does vary slightly, but it
    might just be a repr change.

    With these tests in mind, I'm not sure why the Python issue got
    created in the first place.

    """
    assert total_seconds(timedelta(microseconds=1)) == 1e-06
    assert total_seconds(timedelta(microseconds=-1)) == -1e-06
    assert total_seconds(timedelta(microseconds=-2)) == -2e-06
    assert total_seconds(timedelta(days=2 ** 29, microseconds=1)) == 46385646796800.0

    assert total_seconds(timedelta(seconds=123456.789012)) == 123456.789012
    assert total_seconds(timedelta(seconds=-123456.789012)) == -123456.789012


def test_daterange_years():
    new_year = date(2017, 1, 1)
    bit_rollover = date(2038, 1, 19)

    new_years_remaining = daterange(new_year, bit_rollover, step=(1, 0, 0))
    assert len(list(new_years_remaining)) == 22

    y2025 = date(2025, 1, 1)
    bakers_new_years_til_2025 = daterange(new_year, y2025, step=(1, 1, 0))
    assert len(list(bakers_new_years_til_2025)) == 8
