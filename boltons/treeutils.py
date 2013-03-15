# 0 = item
# 1 = left
# 2 = right
# 3 = height

"""
maintains insertion order on equal values by going right when equal.
"""


class Tree(object):
    def __init__(self, **kw):
        self.root = None
        self.node_count = 0
        self.node_size = max(1, kw.pop('node_size', 1))
        self._lrh = (-3, -2, -1)  # left, right, height

    def insert(self, *a):
        item = list(a)
        hash(item[0])  # mutable items will break the tree invariant
        item.extend([None, None, 1])
        cur = self.root
        if not cur:
            self.root = item
            self.node_count += 1
            return
        L, R, _ = self._lrh
        stack = []
        while cur:
            stack.append(cur)
            if item < cur[0]:
                cur = cur[L]
            else:
                cur = cur[R]
        cur = stack[-1]
        if item < cur[0]:
            cur[L] = item
        else:
            cur[R] = item
        self.node_count += 1
        self._rebalance(stack)

    def delete(self, item):
        stack = []
        cur = self.root
        while cur:
            if item == cur[0]:
                break
            stack.append(cur)
            if item < cur[0]:
                cur = cur[1]
            else:
                cur = cur[2]
        if not cur:
            raise ValueError("item not in tree: %r" % item)
        if not cur[1] or not cur[2]: #no left child or no right child
            if not cur[1]: #no left child
                replace = cur[2]
            elif not cur[2]: #no right child
                replace = cur[1]
            if stack[-1][1] is cur: #if left child
                stack[-1][1] = replace #replace left child
            elif stack[-1][2] is cur: #if right child
                stack[-1][2] = replace #replace right child
        else: #both children exist
            stack.append(cur)
            pred = cur[1] #find in-order predecessor; could also use successor is arbitrary
            while pred[2]: #go right as long as possible
                stack.append(pred)
                pred = cur[2]
            stack[-1][2] = pred[1] #remove predecessor node from tree
            cur[0] = pred[0] #replace cur value with predecessor value
        self.node_count -= 1
        self._rebalance(stack)

    def _rebalance(self, stack):
        L, R, H = self._lrh
        for i in reversed(range(len(stack))):
            node = stack[i]
            height = max(0, node[L] and node[L][H], node[R] and node[R][H]) + 1
            if height == node[H]:
                return
            node[3] = height
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
        L, R, _ = self._lrh
        while stack or cur:
            if cur:
                stack.append(cur)
                cur = cur[L]  # left
            else:
                cur = stack.pop()
                yield cur
                cur = cur[R]  # right

    def __iter__(self):
        return (node[0] for node in self.iternodes())

    def __contains__(self, item): pass

    def pop(self): pass

    def popleft(self): pass

    def __len__(self):
        return self.node_count


def sorted_compare_test(vals):
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
        results.append(sorted_compare_test(val_set))
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


if __name__ == '__main__':
    import signal, pdb
    def pdb_int_handler(sig, frame):
        pdb.set_trace()
    signal.signal(signal.SIGINT, pdb_int_handler)
    try:
        res = test_insert_gauntlet()
    except:
        import pdb;pdb.post_mortem()
        raise
    if res:
        print 'tests pass'
    else:
        print 'tests failed'



"""


+ 136

= [156, [45, [20, None, None, 1], None, 2], [212, [159, None, None, 1], [240, None, None, 1], 2], 3]
"""
