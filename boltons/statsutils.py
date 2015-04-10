 # -*- coding: utf-8 -*-
"""``statsutils`` provides statistical functionality, such as mean
(average), median, and variance, for basic data analysis.

The :class:`Stats` type provides all the main functionality of the
``statsutils`` module. A :class:`Stats` object wraps a given dataset,
providing all statistical measures as property attributes. These
attributes cache their results, which allows efficient computation of
multiple measures, as many measures rely on other measures. For
example, relative standard deviation (:meth:`Stats.rel_std_dev`) relies
on both the mean and standard deviation.

The :class:`Stats` type's methods have a module-level counterpart for
convenience when the computation reuse advantages do not apply.

>>> stats = Stats(range(42))
>>> stats.mean
20.5
>>> mean(range(42))
20.5

Statistical moments
-------------------

Python programmers are probably familiar with the concept of the
*mean* or *average*, which gives a rough quantitiative middle value by
which a sample can be can be generalized. However, the mean is just
the first of four `moment`_-based measures by which a sample or
distribution can be measured.

The four `Standardized moments`_ are:

  1. `Mean`_ - :func:`mean` - theoretical middle value
  2. `Variance`_ - :func:`variance` - width of value dispersion
  3. `Skewness`_ - :func:`skewness` - symmetry of distribution
  4. `Kurtosis`_ - :func:`kurtosis` - "peakiness" or "long-tailed"-ness

For more information check out `the Moment article on Wikipedia`_.

.. _moment: http://en.wikipedia.org/wiki/Moment_(mathematics)
.. _Standardied moments: https://en.wikipedia.org/wiki/Standardized_moment
.. _Mean: https://en.wikipedia.org/wiki/Mean
.. _Variance: https://en.wikipedia.org/wiki/Variance
.. _Skewness: https://en.wikipedia.org/wiki/Skewness
.. _Kurtosis: https://en.wikipedia.org/wiki/Kurtosis

Keep in mind that while these moments can give a bit more insight into
the shape and distribution of data, they do not guarantee a complete
picture. Wildly different datasets can have the same values for all
four moments, so generalize wisely.

Robust statistics
-----------------

Moment-based statistics are notorious for being easily skewed by
outliers. The whole field of robust statistics aims to mitigate this
dilemma. ``statsutils`` also includes several robust statistical methods:

  * `Median`_ - The middle value of a sorted dataset
  * `Trimean`_ - Another robust measure of the data's central tendency
  * `Median Absolute Deviation`_ (MAD) - A robust measure of
    variability, a natural counterpart to :func:`variance`.
  * `Trimming`_ - Reducing a dataset to only the middle majority of
    data is a simple way of making other estimators more robust.

.. _Median: https://en.wikipedia.org/wiki/Median
.. _Trimean: https://en.wikipedia.org/wiki/Trimean
.. _Median Absolute Deviation: https://en.wikipedia.org/wiki/Median_absolute_deviation
.. _Trimming: https://en.wikipedia.org/wiki/Trimmed_estimator

Online and Offline Statistics
-----------------------------

Unrelated to computer networking, `online`_ statistics involve
calculating statistics in a `streaming`_ fashion, without all the data
being available. The :class:`Stats` type is meant for the more
traditional offline statistics when all the data is available. For
pure-Python online statistics accumulators, look at the `Lithoxyl`_
system instrumentation package.

.. _Online: https://en.wikipedia.org/wiki/Online_algorithm
.. _streaming: https://en.wikipedia.org/wiki/Streaming_algorithm
.. _Lithoxyl: https://github.com/mahmoud/lithoxyl
"""

from __future__ import print_function

from math import floor, ceil


class _StatsProperty(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.internal_name = '_' + name

        doc = func.__doc__ or ''
        pre_doctest_doc, _, _ = doc.partition('>>>')
        self.__doc__ = pre_doctest_doc

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


class Stats(object):
    """The ``Stats`` type is used to represent a group of unordered
    statistical datapoints for calculations such as mean, median, and
    variance.
    """
    def __init__(self, data, default=0.0, use_copy=True):
        # float('nan') could also be a good default
        self._use_copy = use_copy
        self._is_sorted = False
        if use_copy:
            self.data = list(data)
        else:
            self.data = data

        self.default = default
        cls = self.__class__
        self._prop_attr_names = [a for a in dir(self)
                                 if isinstance(getattr(cls, a, None),
                                               _StatsProperty)]
        self._pearson_precision = 0

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def _get_sorted_data(self):
        """When using a copy of the data, it's better to have that copy be
        sorted, but we do it lazily using this method, in case no
        sorted measures are used. I.e., if median is never called,
        sorting would be a waste.

        When not using a copy, it's presumed that all optimizations
        are on the user.
        """
        if not self._use_copy:
            return sorted(self.data)
        elif not self._is_sorted:
            self.data.sort()
        return self.data

    def clear_cache(self):
        for attr_name in self._prop_attr_names:
            delattr(self, getattr(self.__class__, attr_name).internal_name)

    def _calc_mean(self):
        """
        The arithmetic mean, or "average". Sum of the values divided by
        the number of values.

        >>> mean(range(20))
        9.5
        >>> mean(list(range(19)) + [949])  # 949 is an arbitrary outlier
        56.0
        """
        return sum(self.data, 0.0) / len(self.data)
    mean = _StatsProperty('mean', _calc_mean)

    def _calc_median(self):
        """
        The median is either the middle value or the average of the two
        middle values of a sample. Compared to the mean, it's generally
        more resilient to the presence of outliers in the sample.

        >>> median([2, 1, 3])
        2
        >>> median(range(97))
        48
        >>> median(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48
        """
        return self._get_quantile(self._get_sorted_data(), 0.5)
    median = _StatsProperty('median', _calc_median)

    def _calc_trimean(self):
        """
        >>> trimean([2, 1, 3])
        2.0
        >>> trimean(range(97))
        48.0
        >>> trimean(list(range(96)) + [1066])  # 1066 is an arbitrary outlier
        48.0
        """
        sorted_data = self._get_sorted_data()
        gq = lambda q: self._get_quantile(sorted_data, q)
        return (gq(0.25) + (2 * gq(0.5)) + gq(0.75)) / 4.0
    trimean = _StatsProperty('trimean', _calc_trimean)

    def _calc_variance(self):
        """\
        Variance is the average of the squares of the difference between
        each value and the mean.

        >>> variance(range(97))
        784.0
        """
        return mean(self._get_pow_diffs(2))
    variance = _StatsProperty('variance', _calc_variance)

    def _calc_std_dev(self):
        """\
        Standard deviation. Square root of the variance.

        >>> std_dev(range(97))
        28.0
        """
        return self.variance ** 0.5
    std_dev = _StatsProperty('std_dev', _calc_std_dev)

    def _calc_median_abs_dev(self):
        """\
        Median Absolute Deviation is a robust measure of statistical
        dispersion: http://en.wikipedia.org/wiki/Median_absolute_deviation

        >>> median_abs_dev(range(97))
        24.0
        """
        sorted_vals = sorted(self.data)
        x = float(median(sorted_vals))  # programmatically defined below
        return median([abs(x - v) for v in sorted_vals])
    median_abs_dev = _StatsProperty('median_abs_dev', _calc_median_abs_dev)

    def _calc_rel_std_dev(self):
        """\
        Standard deviation divided by the absolute value of the average.

        http://en.wikipedia.org/wiki/Relative_standard_deviation

        >>> print('%1.3f' % rel_std_dev(range(97)))
        0.583
        """
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default
    rel_std_dev = _StatsProperty('rel_std_dev', _calc_rel_std_dev)

    def _calc_skewness(self):
        """\
        Indicates the asymmetry of a curve. Positive values mean the bulk
        of the values are on the left side of the average and vice versa.

        http://en.wikipedia.org/wiki/Skewness

        See the module docstring for more about statistical moments.

        >>> skewness(range(97))  # symmetrical around 48.0
        0.0
        >>> left_skewed = skewness(list(range(97)) + list(range(10)))
        >>> right_skewed = skewness(list(range(97)) + list(range(87, 97)))
        >>> round(left_skewed, 3), round(right_skewed, 3)
        (0.114, -0.114)
        """
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self._get_pow_diffs(3)) /
                    float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default
    skewness = _StatsProperty('skewness', _calc_skewness)

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
            return (sum(self._get_pow_diffs(4)) /
                    float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0
    kurtosis = _StatsProperty('kurtosis', _calc_kurtosis)

    def _calc_pearson_type(self):
        precision = self._pearson_precision
        skewness = self.skewness
        kurtosis = self.kurtosis
        beta1 = skewness ** 2.0
        beta2 = kurtosis * 1.0

        # TODO: range checks?

        c0 = (4 * beta2) - (3 * beta1)
        c1 = skewness * (beta2 + 3)
        c2 = (2 * beta2) - (3 * beta1) - 6

        if round(c1, precision) == 0:
            if round(beta2, precision) == 3:
                return 0  # Normal
            else:
                if beta2 < 3:
                    return 2  # Symmetric Beta
                elif beta2 > 3:
                    return 7
        elif round(c2, precision) == 0:
            return 3  # Gamma
        else:
            k = c1 ** 2 / (4 * c0 * c2)
            if k < 0:
                return 1  # Beta
        raise RuntimeError('missed a spot')
    pearson_type = _StatsProperty('pearson_type', _calc_pearson_type)

    @staticmethod
    def _get_quantile(sorted_data, q):
        data, n = sorted_data, len(sorted_data)
        idx = q / 1.0 * (n - 1)
        idx_f, idx_c = int(floor(idx)), int(ceil(idx))
        if idx_f == idx_c:
            return data[idx_f]
        return (data[idx_f] * (idx_c - idx)) + (data[idx_c] * (idx - idx_f))

    def get_quantile(self, q):
        """
        >>> Stats(range(100)).get_quantile(0.5)
        49.5
        """
        q = float(q)
        if not 0.0 <= q <= 1.0:
            raise ValueError('expected q between 0.0 and 1.0, not %r' % q)
        return self._get_quantile(self._get_sorted_data(), q)

    def trim_relative(self, amount=0.15):
        """A utility function used to cut a proportion of values off each end
        of a list of values. This has the effect of limiting the
        effect of outliers.

        .. note:

            This operation modifies the data in-place. It does not
            make or return a copy.
        """
        trim = float(amount)
        if not 0.0 <= trim <= 1.0:
            raise ValueError('expected amount between 0.0 and 1.0, not %r'
                             % trim)
        size = len(self.data)
        size_diff = int(size * trim)
        if size_diff == 0.0:
            return
        self.data = self._get_sorted_data()[size_diff:-size_diff]
        self.clear_cache()

    def _get_pow_diffs(self, power):
        """
        A utility function used for calculating statistical moments.
        """
        m = self.mean
        return [(v - m) ** power for v in self.data]


def _get_conv_func(attr_name):
    def stats_helper(data, default=0.0):
        return getattr(Stats(data, default=default, use_copy=False),
                       attr_name)
    return stats_helper


for attr_name, attr in list(Stats.__dict__.items()):
    if isinstance(attr, _StatsProperty):
        func = _get_conv_func(attr_name)
        func.__doc__ = attr.func.__doc__
        globals()[attr_name] = func
        delattr(Stats, '_calc_' + attr_name)
# cleanup
del attr
del attr_name
del func


if __name__ == '__main__':
    da = Stats(range(20))
    print(da.mean)

    import random

    def get_pt(dist):
        vals = [dist() for x in range(10000)]
        pt = pearson_type(vals)
        return pt

    for x in range(3):
        # pt = get_pt(dist=lambda: random.normalvariate(15, 5))  # expect 0, normal
        # pt = get_pt(dist=lambda: random.weibullvariate(2, 3))  # gets 1, beta, weibull not specifically supported
        # pt = get_pt(dist=lambda: random.gammavariate(2, 3))  # expect 3, gamma
        # pt = get_pt(dist=lambda: random.betavariate(2, 3))  # expect 1, beta
        # pt = get_pt(dist=lambda: random.expovariate(0.2))  # expect 3, beta
        pt = get_pt(dist=lambda: random.uniform(0.0, 10.0))  # gets 2
        print('pearson type:', pt)

        # import pdb;pdb.set_trace()
