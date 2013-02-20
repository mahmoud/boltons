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

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'
    """
    return delim.join(split_punct_ws(text)).lower()


def split_punct_ws(text):
    """
    str.split() will split on whitespace, split_punct_ws will
    split on punctuation and whitespace. This is mostly here
    for use by slugify(), above.

    >>> split_punct_ws('First post! Hi!!!!~1    ')
    ['First', 'post', 'Hi', '1']
    """
    return [w for w in _punct_re.split(text) if w]


def camel2under(camel_string):
    """
    Converts a camelcased string to underscores. Useful for
    turning a class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()


def under2camel(under_string):
    """
    Converts an underscored string to camelcased. Useful for
    turning a function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split('_'))
