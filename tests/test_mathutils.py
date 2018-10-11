
from pytest import raises
from boltons.mathutils import clamp, ceil, floor
import math

INF, NAN = float('inf'), float('nan')

OPTIONS = [1618, 1378, 166, 1521, 2347, 2016, 879, 2123,
           269.3, 1230, 66, 425.2, 250, 2399, 2314, 439,
           247, 208, 379, 1861]
OPTIONS_SORTED = sorted(OPTIONS)
OUT_OF_RANGE_LOWER = 60
OUT_OF_RANGE_UPPER = 2500
VALID_LOWER = 247
VALID_UPPER = 2314
VALID_BETWEEN = 248.5

def test_clamp_examples():
    """some examples for clamp()"""
    assert 0 == clamp(0, 0, 1) == clamp(-1, 0, 1)
    assert 0 == clamp(-1, lower=0)
    assert 1 == clamp(1, 0, 1) == clamp(5, 0, 1)
    assert 1 == clamp(5, upper=1)
    assert 0.5 == clamp(7, upper=0.5)
    assert 1 == clamp(7.7, upper=1)

def test_clamp_transparent():
    """clamp(x) should equal x because both limits are omitted"""
    assert clamp(0) == 0
    assert clamp(1) == 1
    assert clamp(10**100) == 10**100
    assert clamp(INF) == INF
    assert clamp(-INF) == -INF
    assert math.isnan(clamp(NAN))


def test_ceil_basic():
    assert ceil(VALID_LOWER, OPTIONS) == VALID_LOWER
    assert ceil(VALID_UPPER, OPTIONS) == VALID_UPPER
    assert ceil(VALID_BETWEEN, OPTIONS) == 250


def test_ceil_sorted():
    assert ceil(VALID_LOWER, OPTIONS) == ceil(VALID_LOWER, OPTIONS_SORTED)
    assert ceil(VALID_UPPER, OPTIONS) == ceil(VALID_UPPER, OPTIONS_SORTED)
    assert ceil(VALID_BETWEEN, OPTIONS) == ceil(VALID_BETWEEN, OPTIONS_SORTED)


def test_ceil_oor_lower():
    assert min(OPTIONS) == ceil(OUT_OF_RANGE_LOWER, OPTIONS)


def test_ceil_oor_upper():
    with raises(ValueError):
        ceil(OUT_OF_RANGE_UPPER, OPTIONS)


def test_floor_basic():
    assert floor(VALID_LOWER, OPTIONS) == VALID_LOWER
    assert floor(VALID_UPPER, OPTIONS) == VALID_UPPER
    assert floor(VALID_LOWER, OPTIONS) == 247


def test_floor_sorted():
    assert floor(VALID_LOWER, OPTIONS) == floor(VALID_LOWER, OPTIONS_SORTED)
    assert floor(VALID_UPPER, OPTIONS) == floor(VALID_UPPER, OPTIONS_SORTED)
    assert floor(VALID_BETWEEN, OPTIONS) == floor(VALID_BETWEEN, OPTIONS_SORTED)


def test_floor_oor_upper():
    assert max(OPTIONS) == floor(OUT_OF_RANGE_UPPER, OPTIONS)


def test_floor_oor_lower():
    with raises(ValueError):
        floor(OUT_OF_RANGE_LOWER, OPTIONS)
