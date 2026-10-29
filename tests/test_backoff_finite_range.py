import math

import pytest

from boltons.iterutils import backoff, backoff_iter


@pytest.mark.parametrize(
    "factory", [backoff, lambda *a, **kw: list(backoff_iter(*a, **kw))]
)
@pytest.mark.parametrize(
    "factor,expected", [(1e300, [1e-300, 1.0, 1e300]), (1e100, None)]
)
def test_inferred_count_with_overflowing_finite_ratio(factory, factor, expected):
    values = factory(1e-300, 1e300, factor=factor)
    assert values[0] == 1e-300
    assert values[-1] == 1e300
    assert all(math.isfinite(value) for value in values)
    assert values == sorted(values)
    if expected is not None:
        assert values == expected
    else:
        assert len(values) == 7


def test_exact_power_of_two_extremes():
    values = backoff(math.ldexp(1.0, -1022), math.ldexp(1.0, 1023))
    assert len(values) == 2046
    assert values[-1] == math.ldexp(1.0, 1023)


def test_normal_inferred_and_explicit_count_controls():
    assert backoff(1, 16) == [1, 2, 4, 8, 16]
    assert backoff(1e-300, 1e300, count=2, factor=1e300) == [1e-300, 1.0]


@pytest.mark.parametrize(
    "stop,factor,error",
    [(float("inf"), 2, OverflowError), (1e300, float("inf"), ValueError)],
)
def test_nonfinite_inferred_count_errors_unchanged(stop, factor, error):
    with pytest.raises(error):
        backoff(1e-300, stop, factor=factor)
