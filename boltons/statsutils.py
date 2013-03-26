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
four moments, so generalize wisely. (And read up on robust statistics)
"""


def mean(vals):
    if vals:
        return sum(vals, 0.0) / len(vals)
    else:
        return 0.0


def median(vals):
    if not vals:
        return 0.0
    sorted_vals, size = sorted(vals), len(vals)
    if size % 2 == 1:
        return sorted_vals[(size - 1) / 2]
    else:
        mid = size / 2
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def variance(vals):
    return mean(_pow_diff(vals, 2))


def std_dev(vals):
    return variance(vals) ** 0.5


def median_abs_dev(vals):
    """\
    Median Absolute Deviation is a robust measure of statistical
    dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation
    """
    sorted_vals = sorted(vals)
    x = median(sorted_vals)
    return median([abs(x - v) for v in sorted_vals])


def rel_std_dev(vals):
    """\
    Standard deviation divided by the absolute value of the average.

    http://en.wikipedia.org/wiki/Relative_standard_deviation
    """
    abs_mean = abs(mean(vals))
    if val_mean:
        return std_dev(vals) / abs_mean
    else:
        return 0.0


def skewness(vals):
    """\

    Indicates the asymmetry of a curve. Positive values mean the bulk
    of the values are on the left side of the average and vice versa.

    http://en.wikipedia.org/wiki/Skewness

    See the module docstring for more about statistical moments.
    """
    s_dev = std_dev(vals)
    if len(vals) > 1 and s_dev > 0:
        return (sum(_pow_diff(vals, 3)) /
                float((len(vals) - 1) * (s_dev ** 3)))
    else:
        return 0.0


def kurtosis(vals):
    s_dev = std_dev(vals)
    if len(vals) > 1 and s_dev > 0:
        return (sum(_pow_diff(vals, 4)) /
                float((len(vals) - 1) * (s_dev ** 4)))
    else:
        return 0.0


def trim(vals, trim=0.25):
    if trim > 0.0:
        trim = float(trim)
        size = len(vals)
        size_diff = int(size * trim)
        vals = vals[size_diff:-size_diff]
    return vals


def _pow_diff(vals, power):
    m = mean(vals)
    return [(v - m) ** power for v in vals]
