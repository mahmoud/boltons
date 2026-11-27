import math

import pytest

from boltons.statsutils import Stats, median, mode


_MIN_SUBNORMAL = float.fromhex('0x0.0000000000001p-1022')


@pytest.mark.parametrize('left,right,expected_quartiles', [
    (1, 1, (1, 1, 1)),
    (1, 2, (1, 2, 2)),
    (2, 3, (2, 2, 3)),
    (-3, -3, (-3, -3, -3)),
    (-2, -1, (-2, -2, -1)),
    (-1, 1, (0, 0, 0)),
    (2**52 + 1, 2**52 + 2, (2**52 + 1, 2**52 + 2, 2**52 + 2)),
    (-2**52 - 2, -2**52 - 1, (-2**52 - 2, -2**52 - 2, -2**52 - 1)),
])
@pytest.mark.parametrize('index,q', list(enumerate((0.25, 0.5, 0.75))))
def test_subnormal_quantiles(left, right, expected_quartiles, index, q):
    data = [left * _MIN_SUBNORMAL, right * _MIN_SUBNORMAL]
    assert Stats(data).get_quantile(q) == expected_quartiles[index] * _MIN_SUBNORMAL


@pytest.mark.parametrize('left,right,expected', [
    (1, 1, 1), (1, 2, 2), (2, 3, 2), (-3, -3, -3), (-2, -1, -2),
    (2**52 + 1, 2**52 + 2, 2**52 + 2),
    (-2**52 - 2, -2**52 - 1, -2**52 - 2),
])
def test_subnormal_medians(left, right, expected):
    data = [left * _MIN_SUBNORMAL, right * _MIN_SUBNORMAL]
    assert Stats(data).median == expected * _MIN_SUBNORMAL
    assert median(data) == expected * _MIN_SUBNORMAL


@pytest.mark.parametrize('q,index', [(0.0, 0), (1.0, 1)])
def test_subnormal_quantile_endpoints(q, index):
    data = [_MIN_SUBNORMAL, 2 * _MIN_SUBNORMAL]
    assert Stats(data).get_quantile(q) == data[index]


@pytest.mark.parametrize('data,expected', [
    ([_MIN_SUBNORMAL, float('inf')], float('inf')),
    ([float('-inf'), -_MIN_SUBNORMAL], float('-inf')),
    ([0.0, 2.0], 1.0),
])
def test_quantile_nonfinite_and_normal_controls(data, expected):
    assert Stats(data).get_quantile(0.5) == expected


def test_quantile_nan_and_negative_zero_controls():
    assert math.isnan(Stats([float('nan'), _MIN_SUBNORMAL]).get_quantile(0.5))
    assert math.copysign(1.0, Stats([-0.0, -0.0]).get_quantile(0.5)) == -1.0


def test_stats_basic():
    da = Stats(range(20))
    assert da.mean == 9.5
    assert round(da.std_dev, 2) == 5.77
    assert da.variance == 33.25
    assert da.skewness == 0
    assert round(da.kurtosis, 1) == 1.9
    assert da.median == 9.5


def test_pearson_type_covers_kappa_ge_zero():
    assert Stats([8, 4, 4, 4, 5, 1, 6, 5]).pearson_type == 4
    assert Stats([5, 5, 2, 4, 5, 9, 5, 5]).pearson_type == 5
    assert Stats([0, 0, 0, 0, 0, 0, -11, 17]).pearson_type == 6


def test_mode():
    assert Stats([2, 1, 3, 1]).mode == 1
    # ties resolve to the value seen first in the data
    assert mode([1, 1, 2, 2, 3]) == 1
    # non-numeric, categorical data is supported
    assert mode(['a', 'b', 'b', 'c', 'c', 'c']) == 'c'
    # empty data falls back to the configured default
    assert Stats([], default=None).mode is None


def test_pearson_type_zero_denominator():
    # Supply exact moments to exercise c0 == 0, c2 == 0, and the
    # normal-distribution boundary without sampling noise.
    for skewness, kurtosis, expected in ((2.0, 3.0, 1),
                                         (2.0, 9.0, 3),
                                         (0.0, 3.0, 0)):
        stats = Stats([0])
        stats.skewness = skewness
        stats.kurtosis = kurtosis
        assert stats.pearson_type == expected


def test_histogram_zero_interquartile_range():
    for data in ([5] * 10, [0] * 10 + [100]):
        counts = Stats(data).get_histogram_counts()
        assert counts == [(float(min(data)), len(data))]


def test_sorted_measures_keep_data_order():
    # see #534
    stats = Stats([2, 1, 2, 1])
    assert stats.median == 1.5
    assert stats.mode == 2
    assert stats.data == [2, 1, 2, 1]


def test_clear_cache_resets_is_sorted():
    # see #570
    stats = Stats([1, 2, 3], is_sorted=True)
    assert stats.min == 1
    stats.data.append(0)
    stats.clear_cache()
    assert stats.min == 0
    assert stats.median == 1.5


def test_format_histogram_counts_all_zero():
    # see #529
    from boltons.statsutils import format_histogram_counts

    assert format_histogram_counts([(0.0, 0), (1.0, 0)]) == '0.0: 0 |\n1.0: 0 |'
