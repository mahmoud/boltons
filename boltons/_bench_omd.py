# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/mahmoud/projects/lithoxyl/')

import time
import lithoxyl
from lithoxyl import sinks, logger

from dictutils import OMD
from werkzeug.datastructures import MultiDict, OrderedMultiDict as WOMD
from collections import OrderedDict as OD

q_sink = lithoxyl.sinks.QuantileSink()
log = lithoxyl.logger.BaseLogger('bench_stats', sinks=[q_sink])

try:
    profile
except NameError:
    times = 5
    size = 6000
    redun = 2
else:
    times = 1
    size = 10000
    redun = 10

_rng = range(size / redun) * redun
_unique_keys = set(_rng)
_bad_rng = range(size, size + size)
_pairs = zip(_rng, _rng)


def bench():
    for impl in (OMD, WOMD, MultiDict, OD, dict):
        q_sink = lithoxyl.sinks.QuantileSink()
        log = lithoxyl.logger.BaseLogger('bench_stats', sinks=[q_sink])
        print
        print '+ %s.%s' % (impl.__module__, impl.__name__)
        for i in range(times):
            with log.info('bench_omd') as r:
                # initialization
                d = impl(_pairs)
                # just iteration
                for j in range(times):
                    [_ for _ in d.iteritems()]

                # access existent keys
                for j in range(times):
                    for k in _rng:
                        d[k]
                # access non-existent keys
                for k in _bad_rng:
                    try:
                        d[k]
                    except KeyError:
                        pass
                # pop
                for k in _unique_keys:
                    d.pop(k)
                assert not d

        best_msecs = q_sink.min * 1000
        median_msecs = q_sink.median * 1000
        print ' > ran %d loops of %d items each, best time: %g ms, median time: %g ms' % (times, size, best_msecs, median_msecs)

    print
    return


if __name__ == '__main__':
    bench()
