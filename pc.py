# parse_and_run.py

import sys

sys.setrecursionlimit(10**7)

class TreapNode:
    def __init__(self, date, priority):
        self.date = date
        self.priority = priority
        self.heap_key = priority
        self.left = None
        self.right = None
        # no size needed for QUERY
        self.max_priority = priority

def update_node(node):
    """Update max_priority from children."""
    node.max_priority = node.priority
    if node.left and node.left.max_priority > node.max_priority:
        node.max_priority = node.left.max_priority
    if node.right and node.right.max_priority > node.max_priority:
        node.max_priority = node.right.max_priority

def split_tree(root, key_date):
    if not root:
        return None, None
    if root.date <= key_date:
        left_sub, right_sub = split_tree(root.right, key_date)
        root.right = left_sub
        update_node(root)
        return root, right_sub
    else:
        left_sub, right_sub = split_tree(root.left, key_date)
        root.left = right_sub
        update_node(root)
        return left_sub, root

def merge_trees(left_root, right_root):
    if not left_root or not right_root:
        return left_root or right_root
    if left_root.heap_key > right_root.heap_key:
        left_root.right = merge_trees(left_root.right, right_root)
        update_node(left_root)
        return left_root
    else:
        right_root.left = merge_trees(left_root, right_root.left)
        update_node(right_root)
        return right_root

def insert_node(root, node):
    if not root:
        return node
    if node.heap_key > root.heap_key:
        left_sub, right_sub = split_tree(root, node.date)
        node.left = left_sub
        node.right = right_sub
        update_node(node)
        return node
    if node.date < root.date:
        root.left = insert_node(root.left, node)
    else:
        root.right = insert_node(root.right, node)
    update_node(root)
    return root

def delete_node(root, date):
    if not root:
        return None
    if root.date == date:
        return merge_trees(root.left, root.right)
    if date < root.date:
        root.left = delete_node(root.left, date)
    else:
        root.right = delete_node(root.right, date)
    update_node(root)
    return root

def find_node(root, date):
    while root:
        if date == root.date:
            return root
        root = root.left if date < root.date else root.right
    return None

def collect_above_threshold(root, threshold, out):
    if not root or root.max_priority <= threshold:
        return
    collect_above_threshold(root.left, threshold, out)
    if root.priority > threshold:
        out.append((root.date, root.priority))
    collect_above_threshold(root.right, threshold, out)



def main():
    data = sys.stdin.read().split()
    it = iter(data)
    try:
        N = int(next(it))
    except StopIteration:
        return
    Q = int(next(it))
    root = None
    # initial events
    for _ in range(N):
        d = int(next(it)); p = int(next(it))
        node = TreapNode(d, p)
        root = insert_node(root, node)
    out_lines = []
    # operations
    for _ in range(Q):
        op = next(it)
        if op == 'ADD':
            d = int(next(it)); p = int(next(it))
            root = insert_node(root, TreapNode(d, p))
        elif op == 'REMOVE':
            d = int(next(it))
            root = delete_node(root, d)
        elif op == 'UPDATE':
            d = int(next(it)); new_p = int(next(it))
            node = find_node(root, d)
            if node:
                root = delete_node(root, d)
                root = insert_node(root, TreapNode(d, new_p))
        elif op == 'QUERY':
            thr = int(next(it)); sd = int(next(it)); ed = int(next(it))
            L, M = split_tree(root, sd - 1)
            M, R = split_tree(M, ed)
            res = []
            collect_above_threshold(M, thr, res)
            res.sort(key=lambda x: x[0])
            out_lines.append(str(len(res)))
            for d, p in res:
                out_lines.append(f"{d} {p}")
            M = merge_trees(M, R)
            root = merge_trees(L, M)
    sys.stdout.write("\n".join(out_lines))

if __name__ == '__main__':
    main()

