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


@pytest.mark.parametrize('use_copy', [True, False])
@pytest.mark.parametrize('measure', ['median', 'iqr', 'trimean', 'quantile',
                                     'histogram', 'describe'])
def test_mode_ties_after_sorted_measure(use_copy, measure):
    data = [2, 1, 2, 1]
    stats = Stats(data, use_copy=use_copy)
    if measure == 'quantile':
        stats.get_quantile(0.75)
    elif measure == 'histogram':
        stats.get_histogram_counts()
    elif measure == 'describe':
        stats.describe()
    else:
        getattr(stats, measure)
    assert stats.mode == 2
    assert data == [2, 1, 2, 1]


@pytest.mark.parametrize('use_copy', [True, False])
def test_mode_ties_survive_cache_refresh(use_copy):
    stats = Stats([2, 1, 2, 1], use_copy=use_copy)
    assert stats.mode == 2
    assert stats.median == 1.5
    stats.clear_cache()
    assert stats.mode == 2
    stats.data.extend([3, 3, 3])
    stats.clear_cache()
    assert stats.median == 2
    assert stats.mode == 3


@pytest.mark.parametrize('use_copy', [True, False])
def test_mode_ties_presorted(use_copy):
    stats = Stats([1, 1, 2, 2], use_copy=use_copy, is_sorted=True)
    assert stats.median == 1.5
    assert stats.mode == 1


def test_median_does_not_require_hashable_values():
    class UnhashableFloat(float):
        __hash__ = None

    assert Stats([UnhashableFloat(2), UnhashableFloat(1)]).median == 1.5


@pytest.mark.parametrize('use_copy', [True, False])
def test_sorted_data_refresh_after_mutation(use_copy):
    stats = Stats([2, 1, 2, 1], use_copy=use_copy)
    assert stats.get_quantile(0.5) == 1.5
    stats.data.extend([-1, 9])
    stats.clear_cache()
    assert stats.get_quantile(0) == -1
    assert stats.get_quantile(1) == 9
    assert stats.mode == 2


@pytest.mark.parametrize('use_copy', [True, False])
def test_sorted_data_refresh_after_trim(use_copy):
    stats = Stats([8, 1, 7, 2, 6, 3, 5, 4], use_copy=use_copy)
    assert stats.mode == 8
    assert stats.get_quantile(0) == 1
    stats.trim_relative(0.25)
    assert stats.data == [3, 4, 5, 6]
    assert stats.get_quantile(0) == 3
    assert stats.get_quantile(1) == 6
    assert stats.mode == 3


def test_no_copy_quantiles_see_external_mutations():
    data = [2, 1, 2, 1]
    stats = Stats(data, use_copy=False)
    assert stats.get_quantile(1) == 2
    data.append(9)
    assert stats.get_quantile(1) == 9


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
