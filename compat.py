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
