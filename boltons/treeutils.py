
"""
Below you will find the best damn pure-Python AVL tree implementation
known to humankind. Co-authored by Kurt Rose and Mahmoud Hashemi.

maintains insertion order on equal values (sort "stability"), by going
right when equal.

TODO:
- .keys(), .values(), .items()
- .pop(), .popleft()
"""
import operator
from bisect import insort, bisect


class BisectTree(object):
    def __init__(self, iterable=None, **kw):
        self.keys = []
        self.val_map = None
        self._node_count = 0
        key_size, value_size = kw.pop('key_size', 1), kw.pop('val_size', 1)
        ki, vi = self._get_indices(key_size, value_size)
        self._ki_vs_vi = ki, key_size, vi
        if value_size > 0:
            self.val_map = {}
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw)
        if iterable:
            self.insert_many(iterable)

    @property
    def root(self):
        return self.keys and self.keys[0] or None

    def insert_many(self, iterable):
        if not iterable:
            return
        items = iter(iterable)
        try:
            iter(next(items))
        except StopIteration:
            return
        except TypeError:
            for item in iterable:
                self.insert(item)
        else:
            for item in iterable:
                self.insert(*item)

    def insert(self, *a):
        KI, VS, VI = self._ki_vs_vi
        for key_item in a[:VS]:
            hash(key_item)  # mutable items will break the tree invariant
        key = a[KI]
        if self.val_map is not None:
            self.val_map.setdefault(key, []).append(a[VI])
        insort(self.keys, key)
        self._node_count += 1

    def delete(self, *a):
        key = a[self._ki_vs_vi[0]]
        if self.val_map is not None:
            val_list = self.val_map[key]
            val_list.pop()
            if not val_list:
                self.val_map.pop(key)
            idx = bisect(self.keys, key) - 1
        else:
            idx = bisect(self.keys, key) - 1
            if idx >= 0 or self.keys[idx] != key:
                raise KeyError('tree does not contain %r' % (key,))
        self.keys.pop(idx)
        self._node_count -= 1

    @classmethod
    def _get_indices(cls, key_size, val_size):
        try:
            key_size, val_size = (operator.index(key_size),
                                  operator.index(val_size))
        except AttributeError:
            raise ValueError('key and value sizes must be integers')
        if key_size < 1:
            raise ValueError('key size must be greater than 1')
        if val_size < 0:
            raise ValueError('value size must be a positive integer')
        key_index = 0
        if key_size > 1:
            key_index = slice(0, key_size)
        val_index = 0
        if val_size > 0:
            val_index = key_size
            if val_size > 1:
                val_index = slice(key_size, key_size + val_size)
        return key_index, val_index

    def iterkeys(self):
        return iter(self.keys)

    def itervalues(self):
        return (v for (k, v) in self.iteritems())

    __iter__ = iterkeys

    def iteritems(self):
        if self.val_map is not None:
            for k in self.keys:
                for v in self.val_map[k]:
                    yield (k, v)
        else:
            for k in self.keys:
                yield k

    def __contains__(self, key):
        if not self.keys:
            return False
        if self.val_map is not None:
            return key in self.val_map
        idx = bisect(self.keys, key)
        return self.keys[idx - 1] == key

    def __len__(self):
        return self._node_count


class AVLTree(object):
    def __init__(self, iterable=None, **kw):
        self.root = None
        self.node_count = 0
        key_size, val_size = kw.pop('key_size', 1), kw.pop('val_size', 0)
        ki, vi = self._get_indices(key_size, val_size)
        self._ki_vs_vi_lrh = (ki, key_size, vi, -3, -2, -1)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw)
        # ki = key index; vi = val index; left, right, height
        if iterable:
            self.insert_many(iterable)

    def insert_many(self, iterable):
        if not iterable:
            return
        items = iter(iterable)
        try:
            iter(next(items))
        except StopIteration:
            return
        except TypeError:
            for item in iterable:
                self.insert(item)
        else:
            for item in iterable:
                self.insert(*item)

    def insert(self, *a):
        KI, VS, VI, L, R, _ = self._ki_vs_vi_lrh
        for key_item in a[:VS]:
            hash(key_item)  # mutable items will break the tree invariant
        item = list(a)
        key = item[KI]
        item.extend([None, None, 1])
        cur = self.root
        if not cur:
            self.root = item
            self.node_count += 1
            return
        stack = []
        while cur:
            stack.append(cur)
            if key < cur[KI]:
                cur = cur[L]
            else:
                cur = cur[R]
        cur = stack[-1]
        if key < cur[KI]:
            cur[L] = item
        else:
            cur[R] = item
        self.node_count += 1
        self._rebalance(stack)
        return

    def delete(self, *a):
        KI, _, _, L, R, _ = self._ki_vs_vi_lrh
        key, cur, stack = list(a)[KI], self.root, []
        while cur:
            stack.append(cur)
            if key == cur[KI]:
                while cur[R] and key == cur[R][KI]:
                    cur = cur[R]
                    stack.append(cur)
                break
            if key < cur[KI]:
                cur = cur[L]
            else:
                cur = cur[R]
        if not cur:
            raise KeyError("key not in tree: %r" % (key,))
        if cur[L] and cur[R]:
            replace = cur[R]   # find successor
            stack.append(replace)
            if not replace[L]:
                stack[-2][R] = replace[R]
            else:
                while replace[L]:  # go left as long as possible
                    replace = replace[L]
                    stack.append(replace)
                stack[-2][L] = replace[R]
            cur[:L] = replace[:L]  # replace cur key/val with predecessor's
        else:
            replace = cur[L] or cur[R]
            if cur is self.root:
                self.root = replace
            elif stack[-2][L] is cur:
                stack[-2][L] = replace
            else:
                stack[-2][R] = replace
        self.node_count -= 1
        self._rebalance(stack)
        return

    def _rebalance(self, stack):
        KI, _, _, L, R, H = self._ki_vs_vi_lrh
        while stack:
            node = stack.pop()
            parent = stack and stack[-1] or None
            node[H] = max(node[L] and node[L][H],
                          node[R] and node[R][H], 0) + 1
            while 1:
                balance = (node[L] and node[L][H] or 0) - (node[R] and node[R][H] or 0)
                if abs(balance) < 2:
                    break  # we're balanced
                rel_side = balance / abs(balance)  # -1: rotate left
                side, other_side = -((balance > 0) + 2), -((balance < 0) + 2)
                child = node[side]
                cbal = (child[L] and child[L][H] or 0) - (child[R] and child[R][H] or 0)

                if (rel_side * cbal) < 0:
                    grandchild = child[other_side]
                    node[side] = grandchild
                    child[other_side] = grandchild[side]
                    grandchild[side] = child
                    child[H] = max(child[L] and child[L][H],
                                   child[R] and child[R][H], 0) + 1
                    child = node[side]  # we're done with the old child

                if node is self.root:
                    self.root = child
                else:
                    if parent[L] is node:
                        parent[L] = child
                    else:
                        parent[R] = child

                node[side] = child[other_side]
                node[H] = max(node[L] and node[L][H],
                              node[R] and node[R][H], 0) + 1
                child[other_side] = node
                child[H] = max(child[L] and child[L][H],
                               child[R] and child[R][H], 0) + 1
                if parent is None:
                    break
                parent[H] = max(parent[L] and parent[L][H],
                                parent[R] and parent[R][H], 0) + 1
        return

    def _iternodes(self):
        cur, stack = self.root, []
        _, _, _, L, R, _ = self._ki_vs_vi_lrh
        while stack or cur:
            if cur:
                stack.append(cur)
                cur = cur[L]
            else:
                cur = stack.pop()
                yield cur
                cur = cur[R]

    @classmethod
    def _get_indices(cls, key_size, val_size):
        try:
            key_size, val_size = (operator.index(key_size),
                                  operator.index(val_size))
        except AttributeError:
            raise ValueError('key and value sizes must be integers')
        if key_size < 1:
            raise ValueError('key size must be greater than 1')
        if val_size < 0:
            raise ValueError('value size must be a positive integer')
        key_index = 0
        if key_size > 1:
            key_index = slice(0, key_size)
        val_index = 0
        if val_size > 0:
            val_index = key_size
            if val_size > 1:
                val_index = slice(key_size, key_size + val_size)
        return key_index, val_index

    ########
    # Pythonic wrappers below
    ########

    def iteritems(self):
        KI, _, VI, _, _, _ = self._ki_vs_vi_lrh
        if VI:
            return ((n[KI],) for n in self._iternodes())
        return ((n[KI], n[VI]) for n in self._iternodes())

    def iterkeys(self):
        KI = self._ki_vs_vi_lrh[0]
        return (node[KI] for node in self._iternodes())

    __iter__ = iterkeys

    def itervalues(self):
        VI = self._ki_vs_vi_lrh[2]
        return (n[VI] for n in self._iternodes())

    def __contains__(self, *a):
        KI, _, _, L, R, _ = self._ki_vs_vi_lrh
        key, cur = list(a)[KI], self.root
        while cur:
            if key == cur[KI]:
                break
            if key < cur[KI]:
                cur = cur[L]
            else:
                cur = cur[R]
        if cur:
            return True
        return False

    def __len__(self):
        return self.node_count

    ## TODOs below

    def pop(self): pass

    def popleft(self): pass





#### Testing stuff follows
_DEFAULT_SIZE = 10000


def _sorted_compare_test(tree_type, vals):
    tree = tree_type(vals, val_size=0)
    sorted_vals = sorted(vals)
    return sorted(list(tree)) == sorted_vals


def test_insert_gauntlet(tree_type, size=_DEFAULT_SIZE):
    import os
    range_vals = range(size)
    rev_range = list(reversed(range_vals))
    sorted_range_dups = sorted((range_vals * 2)[:size])
    many_dups = [x % 6 for x in range(size)]
    randoms = [ord(x) for x in os.urandom(2048)]
    value_sets = [range_vals, rev_range, sorted_range_dups, many_dups, randoms]
    results = []
    for val_set in value_sets:
        results.append(_sorted_compare_test(tree_type, val_set))
    return all(results)


def test_value_nodes(tree_type, size=_DEFAULT_SIZE):
    mtree = tree_type(val_size=2)
    rev_range = list(reversed(range(size))) * 2
    rev_pairs = zip(rev_range, rev_range[1:])
    for i, pair in enumerate(rev_pairs):
        mtree.insert(i, *pair)
    mtree_vals = [x for x in mtree.itervalues()]
    return len(mtree_vals) == (len(rev_range) - 1)


def test_wide_key(tree_type, size=_DEFAULT_SIZE):
    import os
    mtree = tree_type(key_size=2)
    rr = list(reversed(range(size))) * 2
    rands = [ord(x) for x in os.urandom(size * 2)]
    rr_triples = zip(rr, rr[1:], rands)
    for triple in rr_triples:
        mtree.insert(*triple)
    mtree_triples = [x for x in mtree.iterkeys()]
    return len(mtree_triples) == len(rr_triples)


def test_contains(tree_type, size=_DEFAULT_SIZE):
    import os
    vals = range(256)
    tree = tree_type(vals, val_size=0)
    contains_rands = [ord(x) in tree for x in os.urandom(size)]
    not_contains_rands = [(256 + x not in tree) for x in range(size)]
    return all(not_contains_rands + contains_rands)


def test_delete(tree_type, size=_DEFAULT_SIZE):
    import os
    tree = tree_type()
    vals = [(x % 9, x) for x in range(size)]
    for v in vals:
        tree.insert(*v)
    assert len(tree) == len(vals)
    for v in vals:
        tree.delete(v[0])
    assert len(tree) == 0
    rands = [(ord(x), i) for i, x in enumerate(os.urandom(size))]
    tree.insert_many(rands)
    for r, _ in rands:
        tree.delete(r)
    assert len(tree) == 0
    return tree.root is None


if __name__ == '__main__':
    import signal, pdb, time, pprint
    def pdb_int_handler(sig, frame):
        pdb.set_trace()
    signal.signal(signal.SIGINT, pdb_int_handler)
    tests = [(k, v) for k, v in globals().items()
             if k.startswith('test_') and callable(v)]
    res = {}
    for tree_type in (BisectTree, AVLTree):
        type_name = tree_type.__name__
        for test_name, test_func in tests:
            start_time = time.time()
            try:
                print type_name, test_name
                t_ret = test_func(tree_type)
            except:
                import pdb;pdb.post_mortem()
                raise
            end_time = time.time() - start_time
            res[type_name, test_name] = t_ret and (round(end_time, 3) or 0.001)
    if all(res.values()):
        print '\nTimings:'
        pprint.pprint(res)
    else:
        print 'tests failed: %r' % [k for k, v in res.items() if not v]
