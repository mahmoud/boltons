# -*- coding: utf-8 -*-
import re
import string

_punct_ws_str = string.punctuation + string.whitespace
_punct_re = re.compile('[' + _punct_ws_str + ']+')
_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def slugify(text, delim='_'):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by 'delim', which defaults to '_'.

    >>> 'First post! Hi!!!!~1    '
    'first_post_hi_1'
    """
    return delim.join(split_punct_ws(text)).lower()


def split_punct_ws(text):
    return [w for w in _punct_re.split(text) if w]


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))
