
from pytest import raises
from boltons.mathutils import ceil, floor


OPTIONS = [1618, 1378, 166, 1521, 2347, 2016, 879, 2123,
           269.3, 1230, 66, 425.2, 250, 2399, 2314, 439,
           247, 208, 379, 1861]
OPTIONS_SORTED = sorted(OPTIONS)
OUT_OF_RANGE_LOWER = 60
OUT_OF_RANGE_UPPER = 2500
VALID_LOWER = 247
VALID_UPPER = 2314
VALID_BETWEEN = 248.5


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
