# 0 = item
# 1 = left
# 2 = right
# 3 = height

"""
maintains insertion order on equal values by going right when equal.
"""


class Tree(object):
    def __init__(self):
        self.root = None
        self.node_count = 0

    def insert(self, item):
        hash(item)
        cur = self.root
        if not cur:
            self.root = [item, None, None, 1]
            self.node_count += 1
            return
        stack = []
        while cur:
            stack.append(cur)
            if item < cur[0]:
                cur = cur[1]
            else:
                cur = cur[2]
        cur = stack[-1]
        if item < cur[0]:
            cur[1] = [item, None, None, 1]
        else:
            cur[2] = [item, None, None, 1]
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
        for i in reversed(range(len(stack))):
            node = stack[i]
            left, right = node[1], node[2]
            height = max(0, left and left[3], right and right[3]) + 1
            #if height == node[3]:
            #    # if we have not changed heights, we're done rotating
            #    return
            #print 'i: %s, height: %s, new height: %s' % (i, node[3], height)
            node[3] = height
            while 1:
                balance = (node[1] and node[1][3] or 0) - (node[2] and node[2][3] or 0)
                if abs(balance) < 2:
                    break  # we're balanced
                rel_side = balance / abs(balance)  # -1: rotate left
                side, other_side = (balance < 0) + 1, (balance > 0) + 1
                child = node[side]
                cbal = (child[1] and child[1][3] or 0) - (child[2] and child[2][3] or 0)
                #print balance, cbal

                if (rel_side * cbal) < 0:
                    print ['', 'left', 'right'][side]
                    grandchild = child[other_side]
                    node[side] = grandchild
                    child[other_side] = grandchild[side]
                    grandchild[side] = child
                    #gc = grandchild
                    #gc[3] = max(0, gc[1] and gc[1][3], gc[2] and gc[2][3]) + 1
                    child[3] = max(0, child[1] and child[1][3], child[2] and child[2][3]) + 1
                    child = node[side]  # we're done with the old child

                #for k, v in locals().items():
                #    try:
                #        if v[0] == 91 and k != 'v':
                #            import pdb;pdb.set_trace()
                #    except (TypeError, IndexError):
                #        pass

                if i == 0:
                    self.root = child
                else:
                    parent = stack[i - 1]
                    if parent[1] is node:
                        parent[1] = child
                    if parent[2] is node:
                        parent[2] = child
                node[side] = child[other_side]
                ns = node[side]
                if ns:
                    ns[3] = max(ns[1] and ns[1][3], ns[2] and ns[2][3], 0) + 1

                child[other_side] = node
                cos = child[other_side]
                if cos:
                    cos[3] = max(cos[1] and cos[1][3], cos[2] and cos[2][3], 0) + 1

                node = parent if i > 0 else self.root
                node[3] = max(node[1] and node[1][3], node[2] and node[2][3], 0) + 1
                # continue inner while
            # continue outer for
        return

    def __iter__(self):
        cur = self.root
        stack = []
        while stack or cur:
            if cur:
                stack.append(cur)
                cur = cur[1] #left
            else:
                cur = stack.pop()
                yield cur[0] #item
                cur = cur[2] #right

    def __contains__(self, item): pass

    def pop(self): pass

    def popleft(self): pass

    def __len__(self):
        return self.node_count


def general_test():
    import os
    vals = [ord(x) for x in os.urandom(2048)]
    #vals = range(2048)
    #vals = sorted(range(100) * 20)
    #vals = list(reversed(range(100)))
    tree, old_tree = Tree(), Tree()
    sorted_vals = sorted(vals)
    offset = 0
    treed_vals = None
    for i, v in enumerate(vals):
        print i, v
        tree.insert(v)

        treed_vals = list(tree)
        new_offset = len(treed_vals) - (i + 1)
        if new_offset != offset:  # sorted_vals[:i]:
            offset = new_offset
            import pdb;pdb.set_trace()
        old_tree.insert(v)

    #treed_vals = list(tree)
    print len(vals), len(treed_vals)
    return sorted(vals) == sorted_vals


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
        res = drop_test()
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
