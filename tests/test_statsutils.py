import pytest

from boltons.statsutils import Stats, mode


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


@pytest.mark.parametrize('base', [10 ** 20, -(10 ** 20), 10 ** 100])
def test_variance_of_nearby_large_integers(base):
    stats = Stats([base, base + 1])
    assert stats.variance == 0.25
    assert stats.std_dev == 0.5


def test_variance_is_independent_of_integer_translation():
    values = [0, 2, 4, 6]
    assert Stats(values).variance == 5.0
    assert Stats([10 ** 20 + value for value in values]).variance == 5.0
