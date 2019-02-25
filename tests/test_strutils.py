# -*- coding: utf-8 -*-

import re
import uuid
from unittest import TestCase

from boltons import strutils


def test_asciify():
    ref = u'Beyoncé'
    b = strutils.asciify(ref)
    assert len(b) == len(b)
    assert b[-1:].decode('ascii') == 'e'


def test_indent():
    to_indent = '\nabc\ndef\n\nxyz\n'
    ref = '\n  abc\n  def\n\n  xyz\n'
    assert strutils.indent(to_indent, '  ') == ref


def test_assemble():
    assert strutils.assemble('-', 1, 'b') == '1-b'


def test_is_uuid():
    assert strutils.is_uuid(uuid.uuid4()) == True
    assert strutils.is_uuid(uuid.uuid4(), version=1) == False
    assert strutils.is_uuid(str(uuid.uuid4())) == True
    assert strutils.is_uuid(str(uuid.uuid4()), version=1) == False
    assert strutils.is_uuid(set('garbage')) == False


def test_parse_int_list():
    assert strutils.parse_int_list("1,3,5-8,10-11,15") == [1, 3, 5, 6, 7, 8, 10, 11, 15]

    assert strutils.parse_int_list("1,3,5-8,10-11,15,") == [1, 3, 5, 6, 7, 8, 10, 11, 15]
    assert strutils.parse_int_list(",1,3,5-8,10-11,15") == [1, 3, 5, 6, 7, 8, 10, 11, 15]
    assert strutils.parse_int_list(" 1, 3 ,5-8,10-11,15 ") == [1, 3, 5, 6, 7, 8, 10, 11, 15]
    assert strutils.parse_int_list("3,1,5-8,10-11,15") == [1, 3, 5, 6, 7, 8, 10, 11, 15]

    assert strutils.parse_int_list("5-8") == [5, 6, 7, 8]
    assert strutils.parse_int_list("8-5") == [5, 6, 7, 8]

def test_format_int_list():
    assert strutils.format_int_list([1, 3, 5, 6, 7, 8, 10, 11, 15]) == '1,3,5-8,10-11,15'
    assert strutils.format_int_list([5, 6, 7, 8]) == '5-8'

    assert strutils.format_int_list([1, 3, 5, 6, 7, 8, 10, 11, 15], delim_space=True) == '1, 3, 5-8, 10-11, 15'
    assert strutils.format_int_list([5, 6, 7, 8], delim_space=True) == '5-8'


class TestMultiReplace(TestCase):

    def test_simple_substitutions(self):
        """Test replacing multiple values."""
        m = strutils.MultiReplace({r'cat': 'kedi', r'purple': 'mor', })
        self.assertEqual(m.sub('The cat is purple'), 'The kedi is mor')

    def test_shortcut_function(self):
        """Test replacing multiple values."""
        self.assertEqual(
            strutils.multi_replace(
                'The cat is purple',
                {r'cat': 'kedi', r'purple': 'mor', }
            ),
            'The kedi is mor'
        )

    def test_substitutions_in_word(self):
        """Test replacing multiple values that are substrings of a word."""
        m = strutils.MultiReplace({r'cat': 'kedi', r'purple': 'mor', })
        self.assertEqual(m.sub('Thecatispurple'), 'Thekediismor')

    def test_sub_with_regex(self):
        """Test substitutions with a regular expression."""
        m = strutils.MultiReplace({
            r'cat': 'kedi',
            r'purple': 'mor',
            r'q\w+?t': 'dinglehopper'
        }, regex=True)
        self.assertEqual(
            m.sub('The purple cat ate a quart of jelly'),
            'The mor kedi ate a dinglehopper of jelly'
        )

    def test_sub_with_list(self):
        """Test substitutions from an iterable instead of a dictionary."""
        m = strutils.MultiReplace([
            (r'cat', 'kedi'),
            (r'purple', 'mor'),
            (r'q\w+?t', 'dinglehopper'),
        ], regex=True)
        self.assertEqual(
            m.sub('The purple cat ate a quart of jelly'),
            'The mor kedi ate a dinglehopper of jelly'
        )

    def test_sub_with_compiled_regex(self):
        """Test substitutions where some regular expressiosn are compiled."""
        exp = re.compile(r'q\w+?t')
        m = strutils.MultiReplace([
            (r'cat', 'kedi'),
            (r'purple', 'mor'),
            (exp, 'dinglehopper'),
        ])
        self.assertEqual(
            m.sub('The purple cat ate a quart of jelly'),
            'The mor kedi ate a dinglehopper of jelly'
        )

    def test_substitutions_with_regex_chars(self):
        """Test replacing values that have special regex characters."""
        m = strutils.MultiReplace({'cat.+': 'kedi', r'purple': 'mor', })
        self.assertEqual(m.sub('The cat.+ is purple'), 'The kedi is mor')
