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
        if item <= cur[0]:
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
            if height == node[3]:
                # if we have not changed heights, we're done rotating
                return
            node[3] = height
            while 1:
                balance = (left and left[3] or 0) - (right and right[3] or 0)
                if abs(balance) < 2:
                    break  # we're balanced
                if balance > 1:
                    leftleft, leftright = left and (left[1], left[2]) or (None, None)
                    leftbalance = (leftleft and leftleft[3] or 0) - (leftright and leftright[3] or 0)
                    if leftbalance < 0:  # left rotate left
                        node[1] = leftright  # left = leftright
                        left[2] = leftright[1]  # left.right = leftright.left
                        leftright[1] = left  # leftright.left = left
                        left = node[1]  # set left to new value for next rotate
                    #right rotate
                    if i > 0:  # right rotate around parent
                        parent = stack[i - 1]
                        if parent[1] is node:
                            parent[1] = left
                        elif parent[2] is node:
                            parent[2] = left
                    else:  # right rotate around root
                        self.root = left
                    node[1] = left[2]  # right = leftright
                    left[2] = node  # leftright = node

                    node = parent if i > 0 else self.root #set node to (new) correct value for balance

                if balance < -1:
                    rightleft = right and right[1]
                    rightright = right and right[2]
                    rightbalance = (rightleft and rightleft[3] or 0) - (rightright and rightright[3] or 0)
                    if rightbalance > 0: #right rotate right
                        node[2] = rightleft #right = rightleft
                        right[1] = rightleft[2] #right.left = rightleft.right
                        rightleft[2] = right #rightleft.right = right
                        right = node[2] #set right to (new) correct value for next rotation
                    #rotate left
                    if i > 0: #left rotate around parent
                        parent = stack[i-1]
                        if parent[1] is node:
                            parent[1] = right
                        elif parent[2] is node:
                            parent[2] = right
                    else: #left rotate around root
                        self.root = right
                    node[2] = right[1] #right = rightleft
                    right[1] = node #rightleft = node

                    node = parent if i > 0 else self.root #set node to (new) correct value for balance

                left = node[1] #update left and right to (new) correct value for balance
                right = node[2]
                if left:
                    for c in (1,2):
                        cur = left[c]
                        if cur:
                            cur[3] = max(cur[1] and cur[1][3] or 0,
                                                cur[2] and cur[2][3] or 0) + 1
                    left[3] = max(left[1] and left[1][3] or 0, left[2] and left[2][3] or 0) + 1
                if right:
                    for c in (1,2):
                        cur = right[c]
                        if cur:
                            cur[3] = max(cur[1] and cur[1][3] or 0,
                                                cur[2] and cur[2][3] or 0) + 1
                    right[3] = max(right[1] and right[1][3] or 0, right[2] and right[2][3] or 0) + 1
                node[3] = max(left and left[3] or 0, right and right[3] or 0) + 1
                # continue inner while
            # continue outer for


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


def test():
    import os
    #vals = [ord(x) for x in os.urandom(2048)]
    vals = range(2048)
    tree = Tree()
    for v in vals:
        tree.insert(v)
    sorted_vals = list(tree)
    import pdb;pdb.set_trace()
    return sorted(vals) == sorted_vals


if __name__ == '__main__':
    import signal, pdb
    def pdb_int_handler(sig, frame):
        pdb.set_trace()
    signal.signal(signal.SIGINT, pdb_int_handler)
    res = test()
    if res:
        print 'tests pass'
    else:
        print 'tests failed'
