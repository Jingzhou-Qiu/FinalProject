import unittest
import random
from treap import Treap


class TestTreap(unittest.TestCase):
    @staticmethod
    def _check_heap(node):
        """Return True iff every parent priority ≤ its children’s."""
        if node is None:
            return True
        if node.left and node.left.priority < node.priority:
            return False
        if node.right and node.right.priority < node.priority:
            return False
        return TestTreap._check_heap(node.left) and TestTreap._check_heap(node.right)

    def setUp(self):
            self.data = random.sample(range(5000), 1000)
            self.t = Treap()
            for x in self.data:
                self.t.insert(x)

    def test_heap_property_initial(self):
        """The whole tree must respect the min‑heap priority rule."""
        self.assertTrue(self._check_heap(self.t.root), "Treap violates heap order on priorities")

    def test_inorder_sorted(self):
        self.assertEqual(self.t.inorder(), sorted(self.data))
        self.test_heap_property_initial()

    def test_search(self):
        for x in random.sample(range(5100), 50):
            if x in self.data:
                self.assertTrue(self.t.search(x))
            else:
                self.assertFalse(self.t.search(x))

    def test_delete(self):
        to_delete = random.sample(self.data, 50)
        for x in to_delete:
            self.t.delete(x)
        remaining = sorted(set(self.data) - set(to_delete))
        self.assertEqual(self.t.inorder(), remaining)

    def test_split_merge(self):
        remaining = sorted(self.data)
        # perform deletes first
        to_delete = random.sample(self.data, 20)
        for x in to_delete:
            self.t.delete(x)
        remaining = sorted(set(self.data) - set(to_delete))
        k = random.choice(remaining)
        left_t, right_t = self.t.split(k)
        L_keys, R_keys = left_t.inorder(), right_t.inorder()
        self.assertTrue(all(x < k for x in L_keys))
        self.assertTrue(all(x >= k for x in R_keys))
        # merge back and compare
        merged_t = self.t.merge(left_t, right_t)
        self.assertEqual(merged_t.inorder(), remaining)


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)