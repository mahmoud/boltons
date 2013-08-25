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
    times = 100
    size = 1000
    redun = 10
else:
    times = 1
    size = 10000
    redun = 10

_rng = range(size / redun) * redun
_pairs = zip(_rng, _rng)

for i in range(times):
    with log.info('bench_omd') as r:
        OMD(_pairs)

#from pprint import pprint
#pprint(q_sink.get_histogram())
best_msecs = q_sink.min * 1000
median_msecs = q_sink.median * 1000
print 'ran %d loops of %d items each, best time: %g ms, median time: %g ms' % (times, size, best_msecs, median_msecs)
