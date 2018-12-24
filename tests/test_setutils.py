# -*- coding: utf-8 -*-

from boltons.setutils import IndexedSet, _MISSING, complement


def test_indexed_set_basic():
    zero2nine = IndexedSet(range(10))
    five2nine = zero2nine & IndexedSet(range(5, 15))
    x = IndexedSet(five2nine)
    x |= set([10])

    assert list(zero2nine) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert set(zero2nine) == set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert list(five2nine) == [5, 6, 7, 8, 9]
    assert x == IndexedSet([5, 6, 7, 8, 9, 10])
    assert x[-1] == 10

    assert zero2nine ^ five2nine == IndexedSet([0, 1, 2, 3, 4])

    assert x[:3] == IndexedSet([5, 6, 7])
    assert x[2:4:-1] == IndexedSet([8, 7])


def test_indexed_set_mutate():
    thou = IndexedSet(range(1000))
    assert (thou.pop(), thou.pop()) == (999, 998)
    assert (thou.pop(499), thou.pop(499)) == (499, 500)

    ref = [495, 496, 497, 498, 501, 502, 503, 504, 505, 506]
    assert [thou[i] for i in range(495, 505)] == ref

    assert len(thou) == 996
    while len(thou) > 600:
        dead_idx_len = len(thou.dead_indices)
        dead_idx_count = thou._dead_index_count
        thou.pop(0)
        new_dead_idx_len = len(thou.dead_indices)
        if new_dead_idx_len < dead_idx_len:
            assert dead_idx_count > 0
            # 124, 109, 95
    assert len(thou) == 600
    assert thou._dead_index_count == 67

    assert not any([thou[i] is _MISSING for i in range(len(thou))])

    thou &= IndexedSet(range(500, 503))

    assert thou == IndexedSet([501, 502])
    return


def big_popper():
    # more of a benchmark than a test
    from os import urandom
    import time
    big_set = IndexedSet(range(100000))
    rands = [ord(r) for r in urandom(len(big_set))]
    start_time, start_size = time.time(), len(big_set)
    while len(big_set) > 10000:
        if len(big_set) % 10000 == 0:
            print(len(big_set) / 10000)
        rand = rands.pop()
        big_set.pop(rand)
        big_set.pop(-rand)
    end_time, end_size = time.time(), len(big_set)
    print()
    print('popped %s items in %s seconds' % (start_size - end_size,
                                             end_time - start_time))


def test_complement_set():
    '''exercises a bunch of code-paths but doesn't really confirm math identities'''
    assert complement(complement(set())) == set()
    sn = {1, 2, 3}
    c_sn = complement(sn)
    sa = set('abc')
    c_sa = complement(sa)
    assert repr(sn) in repr(c_sn)
    # non-mutating tests
    assert complement(c_sn) == sn
    assert complement(c_sa) == sa
    assert 1 not in c_sn
    assert 'a' in c_sn
    assert not (c_sn < sn)  # complement never subset of set
    assert not (sn < c_sn)
    assert not (c_sn < sa)
    assert not (c_sn < c_sa)  # not subsets of each other
    assert sa < c_sn
    assert c_sn < (c_sa | c_sn)
    assert (c_sa | c_sn) > c_sn
    assert c_sn > sa
    assert not (c_sn > sn)
    assert not c_sn.isdisjoint(c_sa)  # complements never disjoint
    assert c_sn.isdisjoint(sn)
    assert not c_sn.isdisjoint(sa)
    assert (c_sn | sn) == complement(set())
    assert (c_sn | c_sa) == complement(set())
    assert c_sn - c_sa == sa
    assert c_sn - sn == c_sn
    assert (c_sn ^ c_sa) == (sn | sa)
    # destructive testing
    c_sn ^= sa
    c_sn ^= c_sa
    c_sn &= sa
    c_sn &= c_sa
    c_sn |= sa
    c_sn |= c_sa
    c_sn -= sa
