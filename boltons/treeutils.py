
"""
Below you will find the best damn pure-Python AVL tree implementation
known to humankind. Co-authored by Kurt Rose and Mahmoud Hashemi.

NOTES:

maintains insertion order on equal values by going right when equal,
but does not maintain insertion order on deletes. Imagine inserting A,
B, C with key values 0, 0, 0, then removing one node with key 0. Upon
traversal you will see one of [A, B], [B, C], or [A, C].

TODO/ideas:

- key_index is a thing, what about val_index? currently values (when
  present) are always returned as lists (from slicing)
- limit individual node size
- more perf tests
- .keys(), .values(), .items()
- counter for identical nodes?
- tunable balance factor (AVL is by default 1)
"""
import operator


def _get_indices(key_size, val_size):
    try:
        key_size, val_size = operator.index(key_size), operator.index(val_size)
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


class Tree(object):
    def __init__(self, iterable=None, **kw):
        self._dbg_nodes = []
        self.root = None
        self.node_count = 0
        key_size, val_size = kw.pop('key_size', 1), kw.pop('val_size', 0)
        ki, vi = _get_indices(key_size, val_size)
        self._ki_vs_vi_lrh = (ki, key_size, vi, -3, -2, -1)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw)
        # ki = key index; vi = val index; left, right, height
        if iterable:
            self.insert_many(iterable)

    def insert_many(self, iterable):
        for item in iterable:
            self.insert(*item)

    def insert(self, *a):
        KI, VS, VI, L, R, _ = self._ki_vs_vi_lrh
        for key_item in a[:VS]:
            hash(key_item)  # mutable items will break the tree invariant
        item = list(a)
        key = item[KI]
        item.extend([None, None, 1])
        self._dbg_nodes.append(item)
        cur = self.root
        if not cur:
            self.root = item
            self.node_count += 1
            return
        stack = []
        while 1:
            stack.append(cur)
            if key < cur[KI]:
                cur = cur[L]
            else:
                cur = cur[R]
            if not cur:
                break
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
        old_len, old_list_len = len(self), len(list(self))
        key, cur, stack = list(a)[KI], self.root, []
        child_side = None  # search target side relative to parent
        while cur:
            stack.append(cur)
            if key == cur[KI]:
                while cur[R] and key == cur[R][KI]:
                    cur = cur[R]
                    stack.append(cur)
                break
            if key < cur[KI]:
                cur, child_side = cur[L], L
            else:
                cur, child_side = cur[R], R
        if not cur:
            raise KeyError("key not in tree: " + repr(key))
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
            height = max(0, node[L] and node[L][H], node[R] and node[R][H]) + 1
            #if height == node[H]:
            #    return  # if height unchanged, the rest of the tree is balanced
            node[H] = height
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

    def iternodes(self):
        cur = self.root
        stack = []
        _, _, _, L, R, _ = self._ki_vs_vi_lrh
        while stack or cur:
            if cur:
                stack.append(cur)
                cur = cur[L]
            else:
                cur = stack.pop()
                yield cur
                cur = cur[R]

    def iteritems(self):
        KI, _, VI, _, _, _ = self._ki_vs_vi_lrh
        if VI:
            return ((n[KI],) for n in self.iternodes())
        return ((n[KI], n[VI]) for n in self.iternodes())

    def iterkeys(self):
        KI, _, _, _, _, _ = self._ki_vs_vi_lrh
        return (node[KI] for node in self.iternodes())

    __iter__ = iterkeys

    def itervalues(self):
        _, _, VI, _, _, _ = self._ki_vs_vi_lrh
        return (n[VI] for n in self.iternodes())

    ## TODOs below

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


    def pop(self): pass

    def popleft(self): pass

    def __len__(self):
        return self.node_count


#### Testing stuff follows


def _sorted_compare_test(vals):
    tree = Tree()
    sorted_vals = sorted(vals)
    #offset, old_tree = 0, Tree()
    treed_vals = None
    for i, v in enumerate(vals):
        #print i, v
        tree.insert(v)
        #treed_vals = list(tree)
        #new_offset = len(treed_vals) - (i + 1)
        #if new_offset != offset:
        #    offset = new_offset
        #    import pdb;pdb.set_trace()
        #old_tree.insert(v)
    treed_vals = list(tree)
    print len(vals), len(treed_vals)
    return sorted(vals) == sorted_vals


def test_insert_gauntlet():
    import os
    range_100 = range(100)
    value_sets = [range_100,
                  list(reversed(range_100)),
                  range(2048),
                  sorted(range_100 * 20),
                  [ord(x) for x in os.urandom(2048)]]
    results = []
    for val_set in value_sets:
        results.append(_sorted_compare_test(val_set))
    return all(results)


def test_drop():
    cur_state = [156,
                 [45,
                  [20, None, None, 1],
                  [148,
                   [91, None, None, 1], None, 2], 3],
                 [212,
                  [159, None, None, 1],
                  [240, None, None, 1], 2], 4]
    tree = Tree()
    tree.root = cur_state
    tree.node_count = 8
    assert len(list(tree)) == len(tree)
    tree.insert(136)
    return len(list(tree)) == len(tree) == 9


def test_multi_value_nodes():
    mtree = Tree()
    rr = list(reversed(range(10000))) * 2
    for r1, r2 in zip(rr, rr[1:]):
        mtree.insert(r2, r1)
    mtree_pairs = list(tuple(x[:2]) for x in mtree.iternodes())
    print mtree_pairs[:10]
    return len(mtree_pairs) == (len(rr) - 1)


def test_wide_key():
    import os
    mtree = Tree(key_size=2)
    rr = list(reversed(range(1000))) * 2
    rands = [ord(x) for x in os.urandom(2000)]
    rr_triples = zip(rr, rr[1:], rands)
    for r1, r2, r3 in rr_triples:
        mtree.insert(r2, r1, r3)
    mtree_triples = list(tuple(x[:3]) for x in mtree.iternodes())
    print mtree_triples[:16]
    return len(mtree_triples) == len(rr_triples)


def test_contains():
    import os
    tree = Tree()
    vals = range(1000)
    for v in vals:
        tree.insert(v)
    assert len(tree) == 1000
    contains_rands = [ord(x) in tree for x in os.urandom(1000)]
    not_contains_rands = [((1000 + ord(x)) not in tree)
                          for x in os.urandom(1000)]
    return all(not_contains_rands + contains_rands)


def test_delete_plain():
    import os
    tree, size = Tree(), 1000
    vals = [(x % 9, x) for x in range(1000)] # [ord(x) % 3 for x in os.urandom(size)]
    for v in vals:
        tree.insert(*v)
    assert len(tree) == len(vals)
    for v in vals:
        tree.delete(v[0])
    assert len(tree) == 0
    return tree.root is None


if __name__ == '__main__':
    import signal, pdb
    def pdb_int_handler(sig, frame):
        pdb.set_trace()
    signal.signal(signal.SIGINT, pdb_int_handler)
    tests = [(k, v) for k, v in globals().items()
             if k.startswith('test_') and callable(v)]
    res = {}
    for test_name, test_func in tests:
        try:
            res[test_name] = test_func()
        except:
            import pdb;pdb.post_mortem()
            raise
    if all(res.values()):
        print 'tests pass'
    else:
        print 'tests failed: %r' % [k for k, v in res.items() if not v]
