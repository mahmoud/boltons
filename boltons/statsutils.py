"""\
statsutils
~~~~~~~~~~

Provide some really basic stats functions, such as mean/average,
median, variance, the basics. A couple more advanced measures, such as
skewness, kurtosis, and median absolute deviation are also provided,
but if a project needs any more than the functions below, I'd strongly
recommend investigating ``scipy.stats`` or some other NumPy-based
statistics package.

(Note that all functions default to 0.0 when passed no values, which,
while not totally accurate, has usually worked out fine for basic
usage.)

A note on statistical moments
-----------------------------

Most people are probably familiar with the concept of the "mean" or
"average", which gives a sort of quantitiative "middle-ish" value by
which a sample can be can be generalized. But the mean is just the
first of four ways a sample or distribution can be described:

Statistical moments and what they generally describe:

1. Average - theoretical middle value
2. Variance - width of value dispersion
3. Skewness - symmetry of distribution
4. Kurtosis - "peakiness" or long-tailed-ness

For more information it's probably best to read a bit of Wikipedia:

http://en.wikipedia.org/wiki/Moment_(mathematics)

Keep in mind that while these moments can give a bit more insight into
the shape and distribution of data, they do not guarantee a complete
picture. Wildly different datasets can have the same values for all
four moments, so generalize wisely. (And read up on robust statistics
and scipy.stats)
"""

__all__ = ['mean', 'median', 'variance', 'std_dev', 'rel_std_dev',
           'median_abs_dev', 'skewness', 'kurtosis', 'trim_sample']


def mean(vals):
    """
    The arithmetic mean, or "average". Sum of the values divided by
    the number of values.

    >>> mean([1, 2, 3])
    2.0
    >>> mean(range(97))
    48.0
    >>> mean(range(96) + [1066])  # 1066 is an arbitrary outlier
    58.0
    """
    if vals:
        return sum(vals, 0.0) / len(vals)
    else:
        return 0.0


def median(vals):
    """
    The median is either the middle value or the average of the two
    middle values of a sample. Compared to the mean, it's generally
    more resilient to the presence of outliers in the sample.

    >>> median([1, 2, 3])
    2
    >>> median(range(97))
    48
    >>> median(range(96) + [1066])  # 1066 is an arbitrary outlier
    48
    """
    if not vals:
        return 0.0
    sorted_vals, size = sorted(vals), len(vals)
    mid = size // 2  # aka floor division
    if size % 2 == 1:
        return sorted_vals[mid]
    else:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def variance(vals):
    """\
    Variance is the average of the squares of the difference between
    each value and the mean.

    >>> variance(range(97))
    784.0
    """
    return mean(_pow_diff(vals, 2))


def std_dev(vals):
    """\
    Standard deviation. Square root of the variance.

    >>> std_dev(range(97))
    28.0
    """
    return variance(vals) ** 0.5


def median_abs_dev(vals):
    """\
    Median Absolute Deviation is a robust measure of statistical
    dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

    >>> median_abs_dev(range(97))
    24.0
    """
    sorted_vals = sorted(vals)
    x = float(median(sorted_vals))
    return median([abs(x - v) for v in sorted_vals])


def rel_std_dev(vals):
    """\
    Standard deviation divided by the absolute value of the average.

    http://en.wikipedia.org/wiki/Relative_standard_deviation

    >>> round(rel_std_dev(range(97)), 3)
    0.583
    """
    abs_mean = abs(mean(vals))
    if abs_mean:
        return std_dev(vals) / abs_mean
    else:
        return 0.0


def skewness(vals):
    """\
    Indicates the asymmetry of a curve. Positive values mean the bulk
    of the values are on the left side of the average and vice versa.

    http://en.wikipedia.org/wiki/Skewness

    See the module docstring for more about statistical moments.

    >>> skewness(range(97))  # symmetrical around 48.0
    0.0
    >>> left_skewed = skewness(range(97) + range(10))
    >>> right_skewed = skewness(range(97) + range(87, 97))
    >>> round(left_skewed, 3), round(right_skewed, 3)
    (0.114, -0.114)
    """
    s_dev = std_dev(vals)
    if len(vals) > 1 and s_dev > 0:
        return (sum(_pow_diff(vals, 3)) /
                float((len(vals) - 1) * (s_dev ** 3)))
    else:
        return 0.0


def kurtosis(vals):
    """\
    Indicates how much data is in the tails of the distribution. The
    result is always positive, with the normal "bell-curve"
    distribution having a kurtosis of 3.

    http://en.wikipedia.org/wiki/Kurtosis

    See the module docstring for more about statistical moments.

    >>> kurtosis(range(9))
    1.99125

    With a kurtosis of 1.99125, [0, 1, 2, 3, 4, 5, 6, 7, 8] is more
    centrally distributed than the normal curve.
    """
    s_dev = std_dev(vals)
    if len(vals) > 1 and s_dev > 0:
        return (sum(_pow_diff(vals, 4)) /
                float((len(vals) - 1) * (s_dev ** 4)))
    else:
        return 0.0


def trim_sample(vals, trim=0.25):
    """
    A utility function used to cut a proportion of values off each end
    of a list of values. When sorted, this has the effect of limiting
    the effect of outliers.

    >>> trim_sample(range(12), 0.25)
    [3, 4, 5, 6, 7, 8]
    """
    if trim > 0.0:
        trim = float(trim)
        size = len(vals)
        size_diff = int(size * trim)
        vals = vals[size_diff:-size_diff]
    return vals


def _pow_diff(vals, power):
    """
    A utility function used for calculating statistical moments.
    """
    m = mean(vals)
    return [(v - m) ** power for v in vals]
