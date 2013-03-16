
"""
maintains insertion order on equal values by going right when equal.

comparing tuples to tuples is faster than comparing lists to lists,
and comparing a tuple to a list is faster than lists to lists.
"""
import operator


def get_indices(index):
    try:
        index, value_start = operator.index(index), 1
        if not index == 0:
            raise ValueError('integer key index must be 0')
    except TypeError:
        try:
            if index.start:
                raise ValueError('slice index start must be 0 or None')
            if index.stop is None or index.stop <= 0:
                raise ValueError('slice stop must be a positive integer')
            if index.step is not None and index.step != 1:
                raise ValueError('slice step must be 1 or None')
            if index.stop == 1:
                index, value_start = 0, 1
            else:
                index, value_start = slice(index.stop), index.stop + 1
        except AttributeError as ae:
            print repr(ae)
            raise ValueError('index type must be 0 or slice')
    return index, value_start


class Tree(object):
    def __init__(self, **kw):
        self.root = None
        self.node_count = 0
        ki, vs = get_indices(kw.pop('key_index', 0))
        self._ki_vs_lrh = (ki, vs, -3, -2, -1)
        if kw:
            raise TypeError('unexpected keyword arguments: %r' % kw)
        # ki = key index; vs = val start; left, right, height

    def insert(self, *a):
        KI, VS, L, R, _ = self._ki_vs_lrh
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
        KI, _, L, R, _ = self._ki_vs_lrh
        cur, stack, key = self.root, [], a[KI]
        child_side = None  # search target side relative to parent
        while cur:
            if key == cur[KI]:
                break
            stack.append(cur)
            if key < cur[KI]:
                cur, child_side = cur[L], L
            else:
                cur, child_side = cur[R], R
        if not cur:
            raise KeyError("key not in tree: %r" % key)
        parent = stack and stack[-1] or self.root
        if cur[L] and cur[R]:
            stack.append(cur)
            replace = cur[L]   # find in-order predecessor
            while replace[R]:  # go right as long as possible
                stack.append(replace)
                replace = cur[R]
            parent[R] = replace[L]  # remove predecessor node from tree
            cur[:L] = replace[:L]   # replace cur key/val with predecessor's
        else:
            replace = cur[L] or cur[R]
            if child_side:
                parent[child_side] = replace
            else:
                self.root = None  # last item, unset root
        self.node_count -= 1
        self._rebalance(stack)
        return

    def _rebalance(self, stack):
        KI, _, L, R, H = self._ki_vs_lrh
        for i in reversed(range(len(stack))):
            node = stack[i]
            height = max(0, node[L] and node[L][H], node[R] and node[R][H]) + 1
            if height == node[H]:
                return  # if height unchanged, the rest of the tree is balanced
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

                if i == 0:
                    self.root = child
                else:
                    parent = stack[i - 1]
                    if parent[L] is node:
                        parent[L] = child
                    elif parent[R] is node:
                        parent[R] = child

                node[side] = child[other_side]
                node[H] = max(node[L] and node[L][H],
                              node[R] and node[R][H], 0) + 1
                child[other_side] = node
                child[H] = max(child[L] and child[L][H],
                               child[R] and child[R][H], 0) + 1
                node = parent if i > 0 else self.root
                node[H] = max(node[L] and node[L][H],
                              node[R] and node[R][H], 0) + 1
        return

    def iternodes(self):
        cur = self.root
        stack = []
        _, _, L, R, _ = self._ki_vs_lrh
        while stack or cur:
            if cur:
                stack.append(cur)
                cur = cur[L]  # left
            else:
                cur = stack.pop()
                yield cur
                cur = cur[R]  # right

    def __iter__(self):
        KI, _, _, _, _ = self._ki_vs_lrh
        return (node[KI] for node in self.iternodes())

    ## TODOs below

    def __contains__(self, item): pass

    def pop(self): pass

    def popleft(self): pass

    #items

    def __len__(self):
        return self.node_count


#### Testing stuff follows


def _sorted_compare_test(vals):
    tree, old_tree = Tree(), Tree()
    sorted_vals = sorted(vals)
    offset = 0
    treed_vals = None
    for i, v in enumerate(vals):
        #print i, v
        tree.insert(v)

        treed_vals = list(tree)
        new_offset = len(treed_vals) - (i + 1)
        if new_offset != offset:
            offset = new_offset
            import pdb;pdb.set_trace()
        old_tree.insert(v)
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


def drop_test():
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


def test_slice_key():
    import os
    mtree = Tree(key_index=slice(2))
    rr = list(reversed(range(10000))) * 2
    rands = [ord(x) for x in os.urandom(20000)]
    rr_triples = zip(rr, rr[1:], rands)
    for r1, r2, r3 in rr_triples:
        mtree.insert(r2, r1, r3)
    mtree_triples = list(tuple(x[:3]) for x in mtree.iternodes())
    print mtree_triples[:16]
    return len(mtree_triples) == len(rr_triples)

if __name__ == '__main__':
    import signal, pdb
    def pdb_int_handler(sig, frame):
        pdb.set_trace()
    signal.signal(signal.SIGINT, pdb_int_handler)
    res = []
    try:
        test_slice_key()
        #res.append(test_multi_value_nodes())
        #res.append(test_insert_gauntlet())
    except:
        import pdb;pdb.post_mortem()
        raise
    if all(res):
        print 'tests pass'
    else:
        print 'tests failed'
