# -*- coding: utf-8 -*-

import re
import string
import unicodedata

from compat import str, unicode, basestring, bytes

_punct_ws_str = string.punctuation + string.whitespace
_punct_re = re.compile('[' + _punct_ws_str + ']+')
_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def slugify(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by `delim`, which defaults to '_'.

    The `ascii` convenience flag will asciify the slug if you require
    ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'
    >>> slugify("Kurt Gödel's pretty cool.", ascii=True)
    'kurt_goedel_s_pretty_cool'
    """
    ret = delim.join(split_punct_ws(text))
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


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


def asciify(text, ignore=False):
    """
    Converts a unicode or bytestring into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a _utility_, primarily meant
    for slugification. Whenever possible, make your application work
    _with_ unicode, not against it.

    >>> asciify('Beyoncé')
    'Beyonce'
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


class DeaccenterDict(dict):
    def __missing__(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(unichr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch

    try:
        from collections import defaultdict
    except ImportError:
        # no defaultdict means that __missing__ isn't supported in
        # this version of python, so we define __getitem__
        def __getitem__(self, key):
            try:
                return super(DeaccenterDict, self).__getitem__(key)
            except KeyError:
                return self.__missing__(key)
    else:
        del defaultdict


_BASE_DEACCENT_MAP = {
    0xc6: u"AE", # Æ LATIN CAPITAL LETTER AE
    0xd0: u"D",  # Ð LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # Ø LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # Þ LATIN CAPITAL LETTER THORN
    0xc4: u'Ae', # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
    0xd6: u'Oe', # Ö LATIN CAPITAL LETTER O WITH DIAERESIS
    0xdc: u'Ue', # Ü LATIN CAPITAL LETTER U WITH DIAERESIS
    0xc0: u"A",  # À LATIN CAPITAL LETTER A WITH GRAVE
    0xc1: u"A",  # Á LATIN CAPITAL LETTER A WITH ACUTE
    0xc3: u"A",  # Ã LATIN CAPITAL LETTER A WITH TILDE
    0xc7: u"C",  # Ç LATIN CAPITAL LETTER C WITH CEDILLA
    0xc8: u"E",  # È LATIN CAPITAL LETTER E WITH GRAVE
    0xc9: u"E",  # É LATIN CAPITAL LETTER E WITH ACUTE
    0xca: u"E",  # Ê LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xcc: u"I",  # Ì LATIN CAPITAL LETTER I WITH GRAVE
    0xcd: u"I",  # Í LATIN CAPITAL LETTER I WITH ACUTE
    0xd2: u"O",  # Ò LATIN CAPITAL LETTER O WITH GRAVE
    0xd3: u"O",  # Ó LATIN CAPITAL LETTER O WITH ACUTE
    0xd5: u"O",  # Õ LATIN CAPITAL LETTER O WITH TILDE
    0xd9: u"U",  # Ù LATIN CAPITAL LETTER U WITH GRAVE
    0xda: u"U",  # Ú LATIN CAPITAL LETTER U WITH ACUTE
    0xdf: u"ss", # ß LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # æ LATIN SMALL LETTER AE
    0xf0: u"d",  # ð LATIN SMALL LETTER ETH
    0xf8: u"oe", # ø LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # þ LATIN SMALL LETTER THORN,
    0xe4: u'ae', # ä LATIN SMALL LETTER A WITH DIAERESIS
    0xf6: u'oe', # ö LATIN SMALL LETTER O WITH DIAERESIS
    0xfc: u'ue', # ü LATIN SMALL LETTER U WITH DIAERESIS
    0xe0: u"a",  # à LATIN SMALL LETTER A WITH GRAVE
    0xe1: u"a",  # á LATIN SMALL LETTER A WITH ACUTE
    0xe3: u"a",  # ã LATIN SMALL LETTER A WITH TILDE
    0xe7: u"c",  # ç LATIN SMALL LETTER C WITH CEDILLA
    0xe8: u"e",  # è LATIN SMALL LETTER E WITH GRAVE
    0xe9: u"e",  # é LATIN SMALL LETTER E WITH ACUTE
    0xea: u"e",  # ê LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xec: u"i",  # ì LATIN SMALL LETTER I WITH GRAVE
    0xed: u"i",  # í LATIN SMALL LETTER I WITH ACUTE
    0xf2: u"o",  # ò LATIN SMALL LETTER O WITH GRAVE
    0xf3: u"o",  # ó LATIN SMALL LETTER O WITH ACUTE
    0xf5: u"o",  # õ LATIN SMALL LETTER O WITH TILDE
    0xf9: u"u",  # ù LATIN SMALL LETTER U WITH GRAVE
    0xfa: u"u",  # ú LATIN SMALL LETTER U WITH ACUTE
    0x2018: u"'",  # ‘ LEFT SINGLE QUOTATION MARK
    0x2019: u"'",  # ’ RIGHT SINGLE QUOTATION MARK
    0x201c: u'"',  # “ LEFT DOUBLE QUOTATION MARK
    0x201d: u'"',  # ” RIGHT DOUBLE QUOTATION MARK
    }


DEACCENT_MAP = DeaccenterDict(_BASE_DEACCENT_MAP)


if __name__ == '__main__':
    b = asciify(u'Beyoncé')
    print ord(b[-1])
    print b
    print DEACCENT_MAP
