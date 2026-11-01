from fractions import Fraction
import statistics

import pytest

from boltons.statsutils import Stats, mode, std_dev, variance


def test_stats_basic():
    da = Stats(range(20))
    assert da.mean == 9.5
    assert round(da.std_dev, 2) == 5.77
    assert da.variance == 33.25
    assert da.skewness == 0
    assert round(da.kurtosis, 1) == 1.9
    assert da.median == 9.5


@pytest.mark.parametrize('offset', [0, 2**53, 10**20, -10**20])
@pytest.mark.parametrize('values', [
    [0, 1], [0, 1, 2], [0, 1, 1], [7], [7] * 10,
    [0] * 10 + [100], [-17, 0, 4, 90], [-10**20, 10**20],
])
def test_integer_variance(offset, values):
    data = [offset + value for value in values]
    # Fraction inputs keep the oracle exact even on older Python versions.
    expected = float(statistics.pvariance([Fraction(value) for value in data]))
    for ordered in (data, data[::-1], data[1:] + data[:1]):
        stats = Stats(ordered)
        assert stats.variance == expected
        assert stats.std_dev == pytest.approx(expected ** 0.5)
        assert variance(ordered) == expected
        assert std_dev(ordered) == pytest.approx(expected ** 0.5)


@pytest.mark.parametrize('data', [
    [1.0, 2.0, 4.0, 9.0], [1, 2.5, 7], [0.1, 0.2, 0.3],
    [Fraction(1, 3), Fraction(2, 3), Fraction(4, 3)], [True, False, True],
])
def test_variance_numeric_controls(data):
    expected = float(statistics.pvariance(data))
    stats = Stats(data)
    assert stats.variance == pytest.approx(expected)
    assert stats.std_dev == pytest.approx(expected ** 0.5)
    assert variance(data) == pytest.approx(expected)
    assert std_dev(data) == pytest.approx(expected ** 0.5)


def test_variance_defaults():
    assert Stats([]).variance == variance([]) == 0.0
    assert Stats([]).std_dev == std_dev([]) == 0.0
    assert Stats([], default=None).variance is None
    assert Stats([], default=None).std_dev is None
    assert variance([], default=None) is None
    assert std_dev([], default=None) is None


@pytest.mark.parametrize('make_data', [set, frozenset,
    lambda values: dict(enumerate(values)).values()],
    ids=['set', 'frozenset', 'dict_values'])
@pytest.mark.parametrize('entry', ['variance', 'std_dev',
                                  'Stats.variance', 'Stats.std_dev'])
@pytest.mark.parametrize('values', [
    [1, 2, 3], [10**20, 10**20 + 1], [-10**20, -10**20 + 1],
    [10**1000], [1.0, 2.0, 4.0], [1, 2.5, 7],
    [Fraction(1, 3), Fraction(2, 3), Fraction(4, 3)], [True, False],
])
def test_variance_nonindexable_data(make_data, entry, values):
    data = make_data(values)
    # Use the actual observations: sets may discard duplicate values.
    expected = float(statistics.pvariance([Fraction(value) for value in data]))
    if entry.startswith('Stats.'):
        result = getattr(Stats(data, use_copy=False), entry.split('.')[1])
    else:
        result = {'variance': variance, 'std_dev': std_dev}[entry](data)
    if entry.endswith('variance'):
        assert result == pytest.approx(expected)
    else:
        assert result == pytest.approx(expected ** 0.5)


@pytest.mark.parametrize('make_data', [set, frozenset,
    lambda values: dict(enumerate(values)).values()],
    ids=['set', 'frozenset', 'dict_values'])
@pytest.mark.parametrize('default', [0.0, None, -1])
def test_variance_nonindexable_empty(make_data, default):
    data = make_data([])
    stats = Stats(data, default=default, use_copy=False)
    assert stats.variance == default
    assert stats.std_dev == default
    assert variance(data, default=default) == default
    assert std_dev(data, default=default) == default


def test_variance_cache_and_trim():
    stats = Stats([10**20, 10**20 + 1], use_copy=False)
    # Reading the rounded mean first must not lose the integer differences.
    assert stats.mean == 1e20
    assert stats.variance == 0.25
    assert stats.std_dev == 0.5
    stats.data.append(10**20 + 2)
    assert stats.variance == 0.25
    assert stats.std_dev == 0.5
    stats.clear_cache()
    assert stats.variance == 2 / 3
    assert stats.std_dev == pytest.approx((2 / 3) ** 0.5)

    stats = Stats([10**20 + value for value in [0, 1, 2, 3, 100]])
    assert stats.variance == 1553.36
    stats.trim_relative(0.2)
    assert stats.variance == 2 / 3
    assert stats.std_dev == pytest.approx((2 / 3) ** 0.5)


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
