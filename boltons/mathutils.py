"""This module provides useful math functions on top of Python's built-in :mod:`math` module.
"""


def ceil_from_list(lst, x, allow_equal=True):
    """
    Return the ceiling of x, the smallest integer or float from lst that is greater than [or equal to] x.

    Args:
        lst (list): List of arbitrary numbers (ints or floats).
        x (int or float): Number to be tested.
        allow_equal (bool): Defaults to ``True``. Allows equality to be ignored if set to ``False``.

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> ceil_from_list(VALID_CABLE_CSA, 3.5)
    4
    >>> ceil_from_list(VALID_CABLE_CSA, 4)
    4
    >>> ceil_from_list(VALID_CABLE_CSA, 4, allow_equal=False)
    6
    """

    return min(filter(lambda y: y >= x if allow_equal else y > x, lst))


def floor_from_list(lst, x, allow_equal=True):
    """
    Return the floor of x, the largest integer or float from lst that is less than [or equal to] x.

    Args:
        lst (list): List of arbitrary numbers (ints or floats).
        x (int or float): Number to be tested.
        allow_equal (bool): Defaults to ``True``. Allows equality to be ignored if set to ``False``.

    >>> VALID_CABLE_CSA = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    >>> floor_from_list(VALID_CABLE_CSA, 3.5)
    2.5
    >>> floor_from_list(VALID_CABLE_CSA, 2.5)
    2.5
    >>> floor_from_list(VALID_CABLE_CSA, 2.5, allow_equal=False)
    1.5
    """

    return max(filter(lambda y: y <= x if allow_equal else y < x, lst))