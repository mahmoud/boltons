import re
import uuid
from unittest import TestCase

from boltons import strutils


def test_strip_ansi():
    assert strutils.strip_ansi(
        '\x1b[0m\x1b[1;36mart\x1b[46;34m\xdc') == 'art\xdc'
    assert strutils.strip_ansi(
        '\x1b[0m\x1b[1;36mart\x1b[46;34m\xdc') == 'artÜ'
    assert strutils.strip_ansi(
        '╒══════╕\n│ \x1b[1mCell\x1b[0m │\n╘══════╛') == (
            '╒══════╕\n'
            '│ Cell │\n'
            '╘══════╛')
    assert strutils.strip_ansi(
        'ls\r\n\x1B[00m\x1b[01;31mfile.zip\x1b[00m\r\n\x1b[01;31m') == \
        'ls\r\nfile.zip\r\n'
    assert strutils.strip_ansi(
        '\t\u001b[0;35mIP\u001b[0m\t\u001b[0;36m192.1.0.2\u001b[0m') == \
        '\tIP\t192.1.0.2'
    assert strutils.strip_ansi('(╯°□°)╯︵ \x1b[1m┻━┻\x1b[0m') == (
        '(╯°□°)╯︵ ┻━┻')
    assert strutils.strip_ansi('(╯°□°)╯︵ \x1b[1m┻━┻\x1b[0m') == (
        '(╯°□°)╯︵ ┻━┻')
    assert strutils.strip_ansi(
        b'(\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0)\xe2\x95\xaf\xef\xb8'
        b'\xb5 \x1b[1m\xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb\x1b[0m') == (
            b'(\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0)\xe2\x95\xaf\xef\xb8'
            b'\xb5 \xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb')
    assert strutils.strip_ansi(
        bytearray('(╯°□°)╯︵ \x1b[1m┻━┻\x1b[0m', 'utf-8')) == \
        bytearray(
            b'(\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0)\xe2\x95\xaf\xef\xb8'
            b'\xb5 \xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb')


def test_asciify():
    ref = 'Beyoncé'
    b = strutils.asciify(ref)
    assert len(b) == len(b)
    assert b[-1:].decode('ascii') == 'e'


def test_indent():
    to_indent = '\nabc\ndef\n\nxyz\n'
    ref = '\n  abc\n  def\n\n  xyz\n'
    assert strutils.indent(to_indent, '  ') == ref


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


def test_human_readable_list():
    """Test the human_readable_list function with various inputs."""
    
    # Test empty list
    assert strutils.human_readable_list([]) == ''
    
    # Test single item
    assert strutils.human_readable_list(['apple']) == 'apple'
    
    # Test two items (no Oxford comma applies)
    assert strutils.human_readable_list(['apple', 'banana']) == 'apple and banana'
    
    # Test three items with Oxford comma (default)
    assert strutils.human_readable_list(['apple', 'banana', 'cherry']) == 'apple, banana, and cherry'
    
    # Test three items without Oxford comma
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], oxford=False) == 'apple, banana and cherry'
    
    # Test four items with Oxford comma
    assert strutils.human_readable_list(['apple', 'banana', 'cherry', 'date']) == 'apple, banana, cherry, and date'
    
    # Test four items without Oxford comma
    assert strutils.human_readable_list(['apple', 'banana', 'cherry', 'date'], oxford=False) == 'apple, banana, cherry and date'
    
    # Test custom delimiter
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], delimiter=';') == 'apple; banana; and cherry'
    
    # Test custom conjunction
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], conjunction='or') == 'apple, banana, or cherry'
    
    # Test custom delimiter and conjunction
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], delimiter='|', conjunction='plus') == 'apple| banana| plus cherry'
    
    # Test custom conjunction without Oxford comma
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], conjunction='or', oxford=False) == 'apple, banana or cherry'
    
    # Test delimiter with extra spaces (should be stripped)
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], delimiter=' , ') == 'apple, banana, and cherry'
    
    # Test conjunction with extra spaces (should be stripped)
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], conjunction=' or ') == 'apple, banana, or cherry'
    
    # Test with empty strings in the list
    assert strutils.human_readable_list(['apple', '', 'cherry']) == 'apple, , and cherry'
    
    # Test with whitespace strings
    assert strutils.human_readable_list(['apple', '  ', 'cherry']) == 'apple,   , and cherry'
    
    # Test with special characters
    assert strutils.human_readable_list(['apple & pear', 'banana/plantain', 'cherry-bomb']) == 'apple & pear, banana/plantain, and cherry-bomb'
    
    # Test with unicode characters
    assert strutils.human_readable_list(['🍎', '🍌', '🍒']) == '🍎, 🍌, and 🍒'
    
    # Test with numbers as strings
    assert strutils.human_readable_list(['1', '2', '3']) == '1, 2, and 3'
    
    # Test edge case with only delimiter character as items
    assert strutils.human_readable_list([',', ',', ',']) == ',, ,, and ,'
    
    # Test long list to ensure pattern consistency
    long_list = ['a', 'b', 'c', 'd', 'e', 'f']
    assert strutils.human_readable_list(long_list) == 'a, b, c, d, e, and f'
    assert strutils.human_readable_list(long_list, oxford=False) == 'a, b, c, d, e and f'

    # Edge cases
    # Test with empty delimiter
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], delimiter='') == 'applebananaand cherry'
    
    # Test with empty conjunction
    assert strutils.human_readable_list(['apple', 'banana', 'cherry'], conjunction='') == 'apple, banana,  cherry'
    
    # Test two items with custom delimiter and conjunction
    assert strutils.human_readable_list(['apple', 'banana'], delimiter=';', conjunction='or') == 'apple or banana'
    
    # Test single item with custom parameters (should ignore them)
    assert strutils.human_readable_list(['apple'], delimiter='|', conjunction='plus', oxford=False) == 'apple'
    
    # Test very long strings
    long_item1 = 'a' * 100
    long_item2 = 'b' * 100
    result = strutils.human_readable_list([long_item1, long_item2])
    assert result == f'{long_item1} and {long_item2}'


def test_human_readable_list_type_annotations():
    """Test that the function works with different sequence types."""
    
    # Test with tuple
    assert strutils.human_readable_list(('apple', 'banana', 'cherry')) == 'apple, banana, and cherry'
    
    # Test with list (already tested above, but for completeness)
    assert strutils.human_readable_list(['apple', 'banana', 'cherry']) == 'apple, banana, and cherry'
    
    # Test with generator (converted to list for the test)
    def fruit_generator():
        yield 'apple'
        yield 'banana' 
        yield 'cherry'
    
    # Convert generator to list since the function expects a Sequence
    fruits = list(fruit_generator())
    assert strutils.human_readable_list(fruits) == 'apple, banana, and cherry'


def test_roundzip():
    aaa = b'a' * 10000
    assert strutils.gunzip_bytes(strutils.gzip_bytes(aaa)) == aaa

    assert strutils.gunzip_bytes(strutils.gzip_bytes(b'')) == b''
