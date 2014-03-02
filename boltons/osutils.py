# -*- coding: utf-8 -*-

import os
import re
import errno
import fnmatch


_CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def iter_find_files(directory, patterns):
    """
    Finds files under a directory match a pattern (or list of
    patterns) using "glob" syntax (e.g., "*.txt").

    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> filenames[-1].split('/')[-1]
    'tzutils.py'
    """
    if isinstance(patterns, basestring):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if pats_re.match(basename):
                filename = os.path.join(root, basename)
                yield filename
    return


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
    return
