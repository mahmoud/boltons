import math

import pytest

from boltons.statsutils import Stats, mode


@pytest.mark.parametrize('data', [(1.0, 2.0, 5.0), (-1.0, 0.0, 1.0), (0.0, 1.0, 3.0, 9.0)])
@pytest.mark.parametrize('name,scale', [
    ('skewness', 1e120), ('skewness', -1e120),
    ('skewness', 1e-120), ('skewness', -1e-120),
    ('skewness', 1e-105), ('skewness', -1e-105),
    ('kurtosis', 1e90), ('kurtosis', -1e90),
    ('kurtosis', 1e-90), ('kurtosis', -1e-90),
    ('kurtosis', 1e-80), ('kurtosis', -1e-80),
    ('skewness', 1.0), ('skewness', 1e30), ('skewness', 1e-30),
    ('kurtosis', 1.0), ('kurtosis', 1e30), ('kurtosis', 1e-30),
])
def test_scaled_moments(data, name, scale):
    expected = getattr(Stats(data), name)
    if name == 'skewness' and scale < 0:
        expected = -expected
    stats = Stats([value * scale for value in data])
    assert math.isfinite(stats.std_dev) and stats.std_dev > 0
    assert getattr(stats, name) == pytest.approx(expected, rel=1e-12, abs=1e-14)


@pytest.mark.parametrize('name,data,scale', [
    ('skewness', [-1.0] * 100 + [1.0] * 100, 1.5e102),
    ('skewness', [-1.0] * 100 + [2.0] * 50, 1e102),
    ('kurtosis', [0.0, 2.0] * 100, 1e77),
])
def test_moment_accumulation_range(name, data, scale):
    expected = getattr(Stats(data), name)
    assert getattr(Stats([value * scale for value in data]), name) == pytest.approx(expected)


@pytest.mark.parametrize('data', [[], [1.0], [1.0, 1.0]])
def test_undefined_moment_controls(data):
    assert Stats(data).skewness == 0.0
    assert Stats(data).kurtosis == 0.0


@pytest.mark.parametrize('name', ['skewness', 'kurtosis'])
def test_moment_custom_deviation_errors_propagate(name):
    class CustomDeviation(float):
        def __pow__(self, power):
            raise OverflowError('custom deviation failure')

    stats = Stats([1.0, 2.0, 5.0])
    stats.std_dev = CustomDeviation(2.0)
    with pytest.raises(OverflowError, match='custom deviation failure'):
        getattr(stats, name)


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
