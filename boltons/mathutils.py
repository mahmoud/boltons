"""This module provides useful math functions on top of Python's built-in :mod:`math` module.
"""
import bisect


def ceil_from_iter(src, x, allow_equal=True, sorted_src=False):
    """
    Return the ceiling of *x*, the smallest integer or float from *src* that is greater than [or equal to] *x*.

    Args:
        src (iterable):     Iterable of arbitrary numbers (ints or floats).
        x (int or float):   Number to be tested.
        allow_equal (bool): Defaults to ``True``. Allows equality to be ignored if set to ``False``.
        sorted_src (bool):  Defaults to ``False``. Allows potential performance increase for large *src* iterable if set
                            to ``False``, as long as *src* is pre-sorted.

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil_from_iter(VALID_CABLE_CSA, 3.5)
    4
    >>> ceil_from_iter(VALID_CABLE_CSA, 4)
    4
    >>> ceil_from_iter(VALID_CABLE_CSA, 4, allow_equal=False)
    6
    """

    if not sorted_src:
        src = sorted(src)

    if allow_equal:
        i = bisect.bisect_left(src, x)
        if i != len(src):
            return src[i]
        raise ValueError("No ceiling value in source iterable greater than or equal to:", x)
    else:
        i = bisect.bisect_right(src, x)
        if i != len(src):
            return src[i]
        raise ValueError("No ceiling value in source iterable greater than:", x)


def floor_from_iter(src, x, allow_equal=True, sorted_src=False):
    """
    Return the floor of *x*, the largest integer or float from *src* that is less than [or equal to] *x*.

    Args:
        src (iterable):     Iterable of arbitrary numbers (ints or floats).
        x (int or float):   Number to be tested.
        allow_equal (bool): Defaults to ``True``. Allows equality to be ignored if set to ``False``.
        sorted_src (bool):  Defaults to ``False``. Allows potential performance increase for large *src* iterable if set
                            to ``False``, as long as *src* is pre-sorted.

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor_from_iter(VALID_CABLE_CSA, 3.5)
    2.5
    >>> floor_from_iter(VALID_CABLE_CSA, 2.5)
    2.5
    >>> floor_from_iter(VALID_CABLE_CSA, 2.5, allow_equal=False)
    1.5
    """

    if not sorted_src:
        src = sorted(src)

    if allow_equal:
        i = bisect.bisect_right(src, x)
        if i:
            return src[i-1]
        raise ValueError("No floor value in source iterable less than or equal to:", x)
    else:
        i = bisect.bisect_left(src, x)
        if i:
            return src[i-1]
        raise ValueError("No floor value in source iterable less than:", x)