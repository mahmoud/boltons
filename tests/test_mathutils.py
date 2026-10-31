from datetime import date
from itertools import product

from pytest import raises, mark
from boltons.mathutils import clamp, ceil, floor, Bits, range_union, range_intersection
import math

INF, NAN = float('inf'), float('nan')

OPTIONS = [1618, 1378, 166, 1521, 2347, 2016, 879, 2123,
           269.3, 1230, 66, 425.2, 250, 2399, 2314, 439,
           247, 208, 379, 1861]
OPTIONS_SORTED = sorted(OPTIONS)
OUT_OF_RANGE_LOWER = 60
OUT_OF_RANGE_UPPER = 2500
VALID_LOWER = 247
VALID_UPPER = 2314
VALID_BETWEEN = 248.5


@mark.parametrize('ranges, union, intersection', [
    ([(1, 5), (2, 6), (1, 4)], [(1, 6)], (2, 4)),  # overlapping ranges merge
    ([(1, 5), (6, 8), (7, 9)], [(1, 5), (6, 9)], None),  # disjoint ranges
    ([], [], None),  # empty input
    ([(2, 2)], [(2, 2)], (2, 2)),  # single point range
    ([(3, 5), (1, 3)], [(1, 5)], (3, 3)),  # touching at endpoint (closed semantics)
    ([(1, 9), (2, 3), (1, 9)], [(1, 9)], (2, 3)),  # duplicates and containment
    ([(5, 6), (-3, -1), (0, 2)], [(-3, -1), (0, 2), (5, 6)], None),  # unsorted input
    ([(0.5, 1.5), (1.0, 2.5)], [(0.5, 2.5)], (1.0, 1.5)),  # float endpoints
    ([(float('-inf'), 0), (0, float('inf'))], [(float('-inf'), float('inf'))], (0, 0)),  # infinite ranges
    ([('a', 'f'), ('c', 'z')], [('a', 'z')], ('c', 'f')),  # string endpoints
])
def test_range_operations(ranges, union, intersection):
    assert range_union(ranges) == union
    assert range_intersection(ranges) == intersection


def test_range_operations_dates():
    """
    Range operations work with any comparable type, including dates.
    """
    ranges = [(date(2026, 10, 1), date(2026, 10, 5)), (date(2026, 10, 3), date(2026, 10, 8))]
    assert range_union(ranges) == [(date(2026, 10, 1), date(2026, 10, 8))]
    assert range_intersection(ranges) == (date(2026, 10, 3), date(2026, 10, 5))


def test_range_operations_negative_and_touching_floats():
    """
    Negative floats, and floats touching at a shared endpoint, merge
    and intersect at exactly that endpoint.
    """
    ranges = [(-0.1, 0.3), (-1.5, -0.1)]
    assert range_union(ranges) == [(-1.5, 0.3)]
    assert range_intersection(ranges) == (-0.1, -0.1)


def test_range_operations_many_float_ranges():
    """
    Large float inputs, such as measurement windows, are handled in any order.
    """
    # each window overlaps the next one, so everything merges into one range
    overlapping = [(i * 0.5, i * 0.5 + 0.75) for i in range(1000)]
    assert range_union(overlapping) == [(0.0, 500.25)]
    assert range_union(reversed(overlapping)) == [(0.0, 500.25)]
    # the first and last windows are far apart, so nothing is shared
    assert range_intersection(overlapping) is None

    # each window leaves a gap before the next one, so none of them merge
    disjoint = [(i * 2.0, i * 2.0 + 0.5) for i in range(1000)]
    assert range_union(reversed(disjoint)) == disjoint
    assert range_intersection(disjoint) is None

    # windows that all contain 100.0 share exactly the narrowest span
    nested = [(100.0 - i * 0.25, 100.0 + i * 0.25) for i in range(1, 1000)]
    assert range_intersection(nested) == (99.75, 100.25)
    assert range_union(nested) == [(100.0 - 999 * 0.25, 100.0 + 999 * 0.25)]


def test_range_operations_generators_and_no_mutation():
    """
    Range operations accept generators and don't mutate input.
    """
    ranges = [[6, 9], [1, 4], [3, 7]]
    assert range_union(iter(ranges)) == [(1, 9)]
    assert range_intersection(iter(ranges)) is None
    assert ranges == [[6, 9], [1, 4], [3, 7]]


@mark.parametrize('operation', [range_union, range_intersection])
@mark.parametrize('ranges', [
    [(3, 1)],
    [(0, 1), (4, 5), (8, 2)],
    [(1,)],
    [(1, 2, 3)],
    [(NAN, 1)],
    [(0, NAN)],
    [(NAN, NAN)],
    [(0, NAN), (3, 4)],
    [(0, 1), (NAN, 4)],
    [(0, 1), (3, 4), (5, NAN)],
])
def test_range_operations_invalid_ranges(operation, ranges):
    with raises(ValueError):
        operation(iter(ranges))


@mark.parametrize('operation', [range_union, range_intersection])
def test_range_operations_incomparable_endpoints(operation):
    with raises(TypeError):
        operation([(1, 'two')])


def test_range_operations_less_than_only():
    """
    Range operations work with objects that only implement __lt__ (<).
    """
    class Endpoint:
        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            return self.value < other.value

    first = Endpoint(1)
    middle = Endpoint(3)
    last = Endpoint(5)
    ranges = [(middle, last), (first, middle)]
    assert range_union(ranges) == [(first, last)]
    assert range_intersection(ranges) == (middle, middle)


def test_range_operations_exhaustive_membership():
    """
    Exhaustive verification of range union and intersection properties.

    The test strategy is based on boundary-value analysis:
    - Enumerate all three-range combinations from a small interval domain.
    - Sample at half-step intervals to test boundaries, interiors and invalid regions.
    - Verify set-theoretic properties including membership, idempotence and canonical form.

    Half-step sampling (e.g. -0.5, 0, 0.5, ..., 3.5) ensures:
    - On-point testing. Exact boundary values (0, 1, 2, 3)
    - Off-point testing. Values just outside valid range (-0.5, 3.5)
    - Interior testing. Values between boundaries (0.5, 1.5, 2.5)

    This detects off-by-one errors and closed vs open interval bugs.

    References:
    - Boundary-value analysis: https://en.wikipedia.org/wiki/Boundary-value_analysis
    - Algebra of sets: https://en.wikipedia.org/wiki/Algebra_of_sets
    """
    intervals = [(lower, upper) for lower in range(4) for upper in range(lower, 4)]
    for ranges in product(intervals, repeat=3):
        union = range_union(ranges)
        intersection = range_intersection(ranges)
        for point in (value / 2 for value in range(-1, 8)):
            # membership property: x in union iff x in some input
            assert any(lower <= point <= upper for lower, upper in union) == \
                   any(lower <= point <= upper for lower, upper in ranges)
            # membership property: x in intersection iff x in all inputs
            assert (intersection is not None and intersection[0] <= point <= intersection[1]) == \
                   all(lower <= point <= upper for lower, upper in ranges)
        # canonical form: output sorted and non-overlapping
        assert all(previous[1] < following[0] for previous, following in zip(union, union[1:]))
        # idempotence: union(union(x)) = union(x)
        assert range_union(union) == union


def test_clamp_examples():
    """some examples for clamp()"""
    assert 0 == clamp(0, 0, 1) == clamp(-1, 0, 1)
    assert 0 == clamp(-1, lower=0)
    assert 1 == clamp(1, 0, 1) == clamp(5, 0, 1)
    assert 1 == clamp(5, upper=1)
    assert 0.5 == clamp(7, upper=0.5)
    assert 1 == clamp(7.7, upper=1)

def test_clamp_transparent():
    """clamp(x) should equal x because both limits are omitted"""
    assert clamp(0) == 0
    assert clamp(1) == 1
    assert clamp(10**100) == 10**100
    assert clamp(INF) == INF
    assert clamp(-INF) == -INF
    assert math.isnan(clamp(NAN))


def test_ceil_basic():
    assert ceil(VALID_LOWER, OPTIONS) == VALID_LOWER
    assert ceil(VALID_UPPER, OPTIONS) == VALID_UPPER
    assert ceil(VALID_BETWEEN, OPTIONS) == 250


def test_ceil_sorted():
    assert ceil(VALID_LOWER, OPTIONS) == ceil(VALID_LOWER, OPTIONS_SORTED)
    assert ceil(VALID_UPPER, OPTIONS) == ceil(VALID_UPPER, OPTIONS_SORTED)
    assert ceil(VALID_BETWEEN, OPTIONS) == ceil(VALID_BETWEEN, OPTIONS_SORTED)


def test_ceil_oor_lower():
    assert min(OPTIONS) == ceil(OUT_OF_RANGE_LOWER, OPTIONS)


def test_ceil_oor_upper():
    with raises(ValueError):
        ceil(OUT_OF_RANGE_UPPER, OPTIONS)


def test_floor_basic():
    assert floor(VALID_LOWER, OPTIONS) == VALID_LOWER
    assert floor(VALID_UPPER, OPTIONS) == VALID_UPPER
    assert floor(VALID_LOWER, OPTIONS) == 247


def test_floor_sorted():
    assert floor(VALID_LOWER, OPTIONS) == floor(VALID_LOWER, OPTIONS_SORTED)
    assert floor(VALID_UPPER, OPTIONS) == floor(VALID_UPPER, OPTIONS_SORTED)
    assert floor(VALID_BETWEEN, OPTIONS) == floor(VALID_BETWEEN, OPTIONS_SORTED)


def test_floor_oor_upper():
    assert max(OPTIONS) == floor(OUT_OF_RANGE_UPPER, OPTIONS)


def test_floor_oor_lower():
    with raises(ValueError):
        floor(OUT_OF_RANGE_LOWER, OPTIONS)


def test_bits():
    def chk(a, b):
        assert a == b, a
    chk(Bits('10')[:1], Bits('1'))
    chk(Bits('10')[1:], Bits('0'))
    chk(Bits('10')[0], True)
    chk(Bits('10')[1], False)
    chk(Bits('0000100')[4], True)
    chk(Bits('10')[-1], False)
    chk(Bits('10')[-2], True)
    chk(Bits('0000100')[-3], True)
    with raises(IndexError):
        Bits('10')[-3]
    chk(Bits('10').as_list(), [True, False])
    chk(Bits('10').as_int(), 2)
    chk(Bits('10').as_bin(), '10')
    chk(Bits('1111').as_hex(), '0F')
    chk(Bits('10'), Bits([True, False]))
    chk(Bits('10'), Bits(2))
    chk(Bits('01') | Bits('10'), Bits('11'))
    chk(Bits('01') & Bits('10'), Bits('00'))
    chk(Bits('11') >> 1, Bits('1'))
    chk(Bits('1') << 1, Bits('10'))
    assert Bits('0') != Bits('00')
    # test roundtrip as_/from_hex
    chk(Bits.from_hex(Bits('10101010').as_hex()),
        Bits('10101010'))
    # test roundtrip as_/from_bytes
    chk(
        Bits.from_bytes(Bits('10101010').as_bytes()),
        Bits('10101010'))
    # pile of roundtripping
    chk(Bits.from_int(
            Bits.from_bin(
                Bits.from_list(
                    Bits('101').as_list()
                ).as_bin()
            ).as_int()
        ),
        Bits('101'))


def test_bits_len_bound():
    # The largest value representable in n bits is 2 ** n - 1, so 2 ** n must
    # be rejected rather than silently producing an over-long Bits.
    # Largest value that fits is accepted and round-trips.
    assert Bits(3, 2).as_bin() == '11'
    # 2 ** len_ does not fit in len_ bits and must raise.
    with raises(ValueError):
        Bits(4, 2)
    with raises(ValueError):
        Bits(1, 0)


def test_empty_bits_conversions():
    for bits in (Bits(''), Bits([]), Bits('101')[:0], Bits(0, 0)):
        assert len(bits) == 0
        assert bits.as_bin() == ''
        assert bits.as_list() == []
        assert bits.as_hex() == ''
        assert bits.as_bytes() == b''
        assert Bits.from_bin(bits.as_bin()) == bits
        assert Bits.from_hex(bits.as_hex()) == bits
        assert Bits.from_bytes(bits.as_bytes()) == bits


def test_empty_bits_rejects_non_hex_inputs():
    for value in (None, 0, False):
        with raises(AttributeError):
            Bits.from_hex(value)


def test_bits_negative_len():
    with raises(ValueError):
        Bits(0, -1)


def test_bits_rshift_past_width():
    shifted = Bits('101') >> 4
    assert len(shifted) == 0
    assert shifted.as_bin() == ''
    assert Bits('101') >> 1 == Bits('10')
