import re

import pytest

from boltons.strutils import MultiReplace


@pytest.mark.parametrize('compiled', [False, True])
@pytest.mark.parametrize('pairs,text,expected', [
    ([(r'(a)\1', 'X')], 'aa a', 'X a'),
    ([(r'(x)', 'Y'), (r'(a)\1', 'X')], 'aa x', 'X Y'),
    ([(r'(a)?(?(1)b|c)', 'X')], 'ab c', 'X X'),
    ([(r'(?P<word>cat)', 'X'), (r'(?P<word>dog)', 'Y')], 'cat dog', 'X Y'),
    ([(r'(?P<group0>cat)', 'X')], 'cat', 'X'),
])
def test_multireplace_preserves_independent_capture_groups(compiled, pairs, text, expected):
    if compiled:
        pairs = [(re.compile(pattern), replacement) for pattern, replacement in pairs]
    assert MultiReplace(pairs, regex=True).sub(text) == expected


@pytest.mark.parametrize('pattern', [r'()', r'(x*)|a', r'(a*)', r'(?=(a))', r'(a)?'])
@pytest.mark.parametrize('text', ['', 'a', 'aba', 'xxa'])
def test_capture_replacement_empty_matches_follow_re_sub(pattern, text):
    assert MultiReplace([(pattern, 'X')], regex=True).sub(text) == re.sub(pattern, lambda m: 'X', text)


@pytest.mark.parametrize('pairs,text,expected', [
    ([(r'(ab|b)', 'X'), ('a', 'Y')], 'ab', 'X'),
    ([('a', 'Y'), (r'(ab|b)', 'X')], 'ab', 'YX'),
    ([(r'()', 'X'), ('a', 'Y')], 'a', 'XYX'),
    ([(r'(a)', 'aa'), ('aa', 'X')], 'a', 'aa'),
])
def test_capture_replacement_priority_and_original_text(pairs, text, expected):
    assert MultiReplace(pairs, regex=True).sub(text) == expected


def test_capture_replacement_preserves_scoped_flags():
    pairs = [(re.compile(r'(cat)', re.I), 'X'), ('dog', 'Y')]
    assert MultiReplace(pairs).sub('CAT cat DOG dog') == 'X X DOG Y'
    pairs = [(re.compile('(c) a t # comment', re.X), 'X'), ('dog', 'Y')]
    assert MultiReplace(pairs).sub('cat dog') == 'X Y'
