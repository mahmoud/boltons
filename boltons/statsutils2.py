 # -*- coding: utf-8 -*-
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

class _AnalyzerProperty(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        # TODO: del func off orig object?

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not obj.data:
            return obj.default
        try:
            return getattr(obj, self.internal_name)
        except AttributeError:
            setattr(obj, self.internal_name, self.func(obj))
            return getattr(obj, self.internal_name)


class DataAnalyzer(object):
    def __init__(self, data, default=0.0, use_copy=True):
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default

    def _calc_mean(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.
        """
        return sum(self.data, 0.0) / len(self.data)
    mean = _AnalyzerProperty('mean', _calc_mean)

    def _calc_median(self):
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
        sorted_data, size = sorted(self.data), len(self.data)
        mid = size // 2  # aka floor division
        if size % 2 == 1:
            return sorted_data[mid]
        else:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0
    median = _AnalyzerProperty('median', _calc_median)

    def _calc_variance(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        return mean(self._get_pow_diffs(self.data, 2))
    variance = _AnalyzerProperty('variance', _calc_variance)

    def _calc_std_dev(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance ** 0.5
    std_dev = _AnalyzerProperty('std_dev', _calc_std_dev)

    def _calc_median_abs_dev(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))
        return median([abs(x - v) for v in sorted_vals])
    median_abs_dev = _AnalyzerProperty('median_abs_dev', _calc_median_abs_dev)

    def _calc_rel_std_dev(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> round(rel_std_dev(range(97)), 3)
        0.583
        """
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default
    rel_std_dev = _AnalyzerProperty('rel_std_dev', _calc_rel_std_dev)

    def _calc_skewness(self):
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
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(data, 3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default
    skewness = _AnalyzerProperty('skewness', _calc_skewness)

    def _calc_kurtosis(self):
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
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(data, 4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0
    kurtosis = _AnalyzerProperty('kurtosis', _calc_kurtosis)

    def trim_relative(self, trim=0.25):
        """
        A utility function used to cut a proportion of values off each end
        of a list of values. When sorted, this has the effect of limiting
        the effect of outliers.

        >>> trim_sample(range(12), 0.25)
        [3, 4, 5, 6, 7, 8]
        """
        if trim > 0.0:
            trim = float(trim)
            size = len(self.vals)
            size_diff = int(size * trim)
            vals = self.vals[size_diff:-size_diff]
        return vals

    def _get_pow_diffs(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v - m) ** power for v in self.data]


for attr_name, attr in DataAnalyzer.__dict__.items():
    if isinstance(attr, _AnalyzerProperty):
        func = lambda data: getattr(DataAnalyzer(data), attr_name)
        globals()[attr_name] = func


#da = DataAnalyzer(range(20))
#print median_abs_dev([5] * 10)


def get_pearson_type(mean, std_dev, skewness, kurtosis, precision=0):
    beta1 = skewness ** 2.0
    beta2 = kurtosis * 1.0

    # TODO: range checks?

    c0 = (4 * beta2) - (3 * beta1)
    c1 = skewness * (beta2 + 3)
    c2 = (2 * beta2) - (3 * beta1) - 6
    print beta1, beta2, c0, c1, c2

    if round(c1, precision) == 0:
        if round(beta2, precision) == 3:
            return 0  # normal
        else:
            if beta2 < 3:
                return 2  # Symmetric Beta
            elif beta2 > 3:
                return 7
    elif round(c2, precision) == 0:
        return 3  # Gamma
    else:
        k = c1 ** 2 / (4 * c0 * c2)
        print 'k:', k
        if k < 0:
            return 1  # Beta
    raise RuntimeError('missed a spot')


import random
from statsutils import mean, std_dev, skewness, kurtosis


def get_pt(dist):
    vals = [dist() for x in xrange(10000)]
    pt = get_pearson_type(mean(vals),
                          std_dev(vals),
                          skewness(vals),
                          kurtosis(vals))
    return pt

if __name__ == '__main__':
    for x in range(3):
        # pt = get_pt(dist=lambda: random.normalvariate(15, 5))  # expect 0, normal
        # pt = get_pt(dist=lambda: random.weibullvariate(2, 3))  # gets 1, beta, weibull not specifically supported
        # pt = get_pt(dist=lambda: random.gammavariate(2, 3))  # expect 3, gamma
        # pt = get_pt(dist=lambda: random.betavariate(2, 3))  # expect 1, beta
        # pt = get_pt(dist=lambda: random.expovariate(0.2))  # expect 3, beta
        pt = get_pt(dist=lambda: random.uniform(0.0, 10.0))  # gets 2
        print 'pearson type:', pt

        import pdb;pdb.set_trace()
