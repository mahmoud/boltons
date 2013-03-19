# -*- coding: utf-8 -*-

import sys

IS_PY2 = sys.version_info[0] == 2
IS_PY3 = sys.version_info[0] == 3


if IS_PY2:
    from StringIO import StringIO
    unicode, str, bytes, basestring = unicode, str, str, basestring
elif IS_PY3:
    from io import StringIO
    unicode, str, bytes, basestring = str, bytes, bytes, str
else:
    raise NotImplementedError('welcome to the future, I guess. (report this)')


def make_sentinel(name='_MISSING', var_name=None):
    class Sentinel(object):
        def __init__(self):
            self.name = name
            self.var_name = var_name
        def __repr__(self):
            if self.var_name:
                return self.var_name
            return '%s(%r)' % (self.__class__.__name__, self.name)
        if var_name:
            def __reduce__(self):
                return self.var_name
        def __nonzero__(self):
            return False
    return Sentinel()
