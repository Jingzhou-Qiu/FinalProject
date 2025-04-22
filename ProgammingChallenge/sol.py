import sys
import threading
import random

sys.setrecursionlimit(1 << 25)

class Node:
    def __init__(self, p, t):
        self.p = p
        self.t = t
        self.left = None
        self.right = None
        self.priority = random.randint(1, 1 << 30)
        self.size = 1

def update_size(node):
    if node:
        node.size = 1 + (node.left.size if node.left else 0) + (node.right.size if node.right else 0)

def split(node, key):
    if not node:
        return (None, None)
    if key < node.p:
        left, right = split(node.left, key)
        node.left = right
        update_size(node)
        return (left, node)
    else:
        left, right = split(node.right, key)
        node.right = left
        update_size(node)
        return (node, right)

def merge(a, b):
    if not a or not b:
        return a or b
    if a.priority > b.priority:
        a.right = merge(a.right, b)
        update_size(a)
        return a
    else:
        b.left = merge(a, b.left)
        update_size(b)
        return b

def insert(node, new_node):
    if not node:
        return new_node
    if new_node.priority > node.priority:
        left, right = split(node, new_node.p)
        new_node.left = left
        new_node.right = right
        update_size(new_node)
        return new_node
    if new_node.p < node.p:
        node.left = insert(node.left, new_node)
    else:
        node.right = insert(node.right, new_node)
    update_size(node)
    return node

def remove(node, key):
    if not node:
        return None
    if node.p == key:
        return merge(node.left, node.right)
    elif key < node.p:
        node.left = remove(node.left, key)
    else:
        node.right = remove(node.right, key)
    update_size(node)
    return node

def simulate(node, T):
    stack = []
    cur = node
    time = 0
    pos = 0
    cnt = 0

    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        move = cur.p - pos
        time += move
        pos = cur.p
        if time > T:
            break
        if time >= cur.t:
            cnt += 1
        elif cur.t <= T:
            time = cur.t
            cnt += 1
        else:
            cur = cur.right
            continue
        cur = cur.right
    return cnt

def main():
    import sys
    input = sys.stdin.readline
    q = int(input())
    root = None
    for _ in range(q):
        tok = input().strip().split()
        if tok[0] == "ADD":
            p, t = int(tok[1]), int(tok[2])
            root = insert(root, Node(p, t))
        elif tok[0] == "REMOVE":
            p = int(tok[1])
            root = remove(root, p)
        elif tok[0] == "QUERY":
            T = int(tok[1])
            print(simulate(root, T))

threading.Thread(target=main).start()