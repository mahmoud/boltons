import pytest

from boltons.iterutils import soft_sorted


@pytest.mark.parametrize('reverse', [False, True])
def test_soft_sorted_overlapping_priorities_keep_each_input_once(reverse):
    values = ['a', 'z', 'b', 'a', 'c']
    assert soft_sorted(values, first=['a'], last=['a', 'z'], reverse=reverse) == (
        ['a', 'a'] + sorted(['b', 'c'], reverse=reverse) + ['z'])
    assert values == ['a', 'z', 'b', 'a', 'c']


def test_soft_sorted_overlap_uses_key_criteria():
    assert soft_sorted(['A', 'b', 'a', 'Z'], first=['a'], last=['a', 'z'],
                       key=str.lower) == ['A', 'a', 'b', 'Z']
