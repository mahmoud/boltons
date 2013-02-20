# -*- coding: utf-8 -*-
import re
import string

_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
_punct_ws_str = string.punctuation + string.whitespace


def slugify(text, delim='_'):
    return delim.join(split_punct_ws(text).lower())


def split_punct_ws(text, _punct=_punct_ws_str):
    return [w for w in text.split(_punct) if w]


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))
