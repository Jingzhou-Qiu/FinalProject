import random

# Node of treap: stores key, heap priority, and children
class Node:
    def __init__(self, key, priority=None):
        self.key = key
        self.priority = priority if priority is not None else random.random()
        self.left = None
        self.right = None


class Treap:
    def __init__(self):
        self.root = None

    # Right rotate to fix heap violation
    #       y              x
    #      / \            / \
    #     x   γ   =>     α   y
    #    / \                / \
    #   α   β              β   γ
    def _rotate_right(self, y):
        x = y.left
        y.left = x.right
        x.right = y
        return x

    # Left rotate to fix heap violation
    #     x                  y
    #    / \                / \
    #   α   y    =>       x   γ
    #      / \           / \
    #     β   γ         α   β
    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        return y

    # Insert a key with optional priority
    # Standard BST insert, then rotate if heap violated
    def _insert(self, node, key, priority=None):
        if node is None:
            # Reached a null position, create new node
            return Node(key, priority)

        if key < node.key:
            node.left = self._insert(node.left, key, priority)
            if node.left.priority < node.priority:
                # If the left child has a higher priority (smaller number), rotate right
                node = self._rotate_right(node)

        elif key > node.key:
            node.right = self._insert(node.right, key, priority)
            if node.right.priority < node.priority:
                # If the right child has a higher priority, rotate left
                node = self._rotate_left(node)

        return node

    def insert(self, key, priority=None):
        self.root = self._insert(self.root, key, priority)

    # Delete key by BST search, then rotate to leaf
    def _delete(self, node, key):
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # Node found, now handle 0, 1, or 2 children cases
            if node.left is None and node.right is None:
                # Case 1: Leaf node
                return None
            elif node.left and node.right:
                # Case 3: Two children → rotate child with smaller priority
                if node.left.priority < node.right.priority:
                    node = self._rotate_right(node)
                    node.right = self._delete(node.right, key)
                else:
                    node = self._rotate_left(node)
                    node.left = self._delete(node.left, key)
            else:
                # Case 2: One child → replace node with child
                node = node.left or node.right
        return node

    def delete(self, key):
        self.root = self._delete(self.root, key)

    # Standard BST search
    def search(self, key):
        cur = self.root
        while cur:
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return True  # Key found
        return False

    # Split treap into two treaps based on key
    # Left treap has keys < key, right treap has keys >= key
    def _split(self, node, key):
        if node is None:
            return (None, None)

        if key <= node.key:
            L, R = self._split(node.left, key)
            node.left = R  # Attach leftover right split to node
            return (L, node)
        else:
            L, R = self._split(node.right, key)
            node.right = L  # Attach leftover left split to node
            return (node, R)

    def split(self, key):
        L, R = self._split(self.root, key)
        left_t, right_t = Treap(), Treap()
        left_t.root, right_t.root = L, R
        return (left_t, right_t)

    # Merge two treaps: left < right, heap priority decides root
    def _merge_nodes(self, left, right):
        if left is None or right is None:
            return left or right  # One tree is empty

        if left.priority < right.priority:
            # Left root has higher priority → attach merge to its right
            left.right = self._merge_nodes(left.right, right)
            return left
        else:
            # Right root has higher priority → attach merge to its left
            right.left = self._merge_nodes(left, right.left)
            return right

    @staticmethod
    def merge(left_treap: "Treap", right_treap: "Treap") -> "Treap":
        t = Treap()
        t.root = t._merge_nodes(left_treap.root, right_treap.root)
        return t

    # In-order traversal for sorted keys
    def inorder(self, node=None):
        if node is None:
            node = self.root
        res = []
        def _rec(n):
            if not n:
                return
            _rec(n.left)         # Traverse left subtree
            res.append(n.key)    # Visit node
            _rec(n.right)        # Traverse right subtree
        _rec(node)
        return res


# Parse and execute commands on a treap
def run_treap_ops(lines):
    t = Treap()
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == "Insert":
            t.insert(int(parts[1]))
        elif cmd == "Delete":
            t.delete(int(parts[1]))
        elif cmd == "Search":
            found = t.search(int(parts[1]))
            print(f"Search {parts[1]}: {'Found' if found else 'Not Found'}")
        elif cmd == "Inorder":
            print("Inorder:", t.inorder())
    return t

# Main function: read mode and input, execute treap ops
def main():
    import sys
    file_path = sys.argv[1]
    with open(file_path, "r") as f:
        lines = f.readlines()

    mode = lines[0].strip()
    args = lines[1].strip()

    if mode == "Merge":
        # Merge two separate treaps
        n1, n2 = map(int, args.split())
        ops1 = lines[2:2+n1]
        ops2 = lines[2+n1:2+n1+n2]
        t1 = run_treap_ops(ops1)
        t2 = run_treap_ops(ops2)
        merged = Treap.merge(t1, t2)
        print("Merged inorder:", merged.inorder())

    elif mode == "Split":
        # Split a single treap
        n = int(args)
        ops = lines[2:2+n]
        split_key = int(lines[2+n])
        t = run_treap_ops(ops)
        L, R = t.split(split_key)
        print("Left treap inorder:", L.inorder())
        print("Right treap inorder:", R.inorder())

    elif mode == "Basic":
        # Just basic operations
        n = int(args)
        ops = lines[2:2+n]
        t = run_treap_ops(ops)

if __name__ == "__main__":
    main()
