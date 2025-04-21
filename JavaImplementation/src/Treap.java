import java.util.*;

public class Treap {

    // ============================ NODE =============================
    // Each node holds a key, a priority (heap), and two children (BST)
    private static final class Node {
        int key;
        double priority;
        Node left, right;

        Node(int key, Double pri, Random rnd) {
            this.key = key;
            this.priority = (pri != null) ? pri : rnd.nextDouble();
        }
    }

    // Split result holds two disjoint treap roots: left and right
    private static final class Split {
        Node left, right;
        Split(Node l, Node r) { left = l; right = r; }
    }

    private Node root;                     // root of the treap
    private final Random rnd = new Random(); // random priority generator

    // ============================ ROTATIONS =============================
    // Restores heap order by rotating a node with its left child
    // Used when left child has higher heap priority (smaller number)
    private Node rotateRight(Node y) {
        Node x = y.left;
        y.left = x.right;
        x.right = y;
        return x;
    }

    // Restores heap order by rotating a node with its right child
    // Used when right child has higher heap priority
    private Node rotateLeft(Node x) {
        Node y = x.right;
        x.right = y.left;
        y.left = x;
        return y;
    }

    // ============================ INSERT =============================
    // Standard BST insert, then perform rotations to preserve heap property
    private Node insert(Node n, int key, Double pri) {
        if (n == null)
            return new Node(key, pri, rnd);  // reached leaf, create new node

        if (key < n.key) {
            n.left = insert(n.left, key, pri);   // insert to left subtree
            if (n.left.priority < n.priority)
                n = rotateRight(n);              // fix heap violation

        } else if (key > n.key) {
            n.right = insert(n.right, key, pri); // insert to right subtree
            if (n.right.priority < n.priority)
                n = rotateLeft(n);               // fix heap violation
        }
        // Ignore duplicate keys
        return n;
    }

    public void insert(int key) {
        root = insert(root, key, null); // use random priority
    }

    public void insert(int key, double pri) {
        root = insert(root, key, pri); // use user-supplied priority
    }

    // ============================ DELETE =============================
    // Find node by key, then rotate its children until leaf, then remove
    private Node delete(Node n, int key) {
        if (n == null) return null; // key not found

        if (key < n.key) {
            n.left = delete(n.left, key); // search left

        } else if (key > n.key) {
            n.right = delete(n.right, key); // search right

        } else {
            // node found
            if (n.left == null || n.right == null)
                return (n.left != null) ? n.left : n.right; // 0 or 1 child

            // rotate smaller priority child up and repeat delete
            if (n.left.priority < n.right.priority) {
                n = rotateRight(n);
                n.right = delete(n.right, key);
            } else {
                n = rotateLeft(n);
                n.left = delete(n.left, key);
            }
        }
        return n;
    }

    public void delete(int key) {
        root = delete(root, key);
    }

    // ============================ SEARCH =============================
    // Standard BST search: returns true if key exists
    public boolean search(int key) {
        Node cur = root;
        while (cur != null) {
            if (key < cur.key) cur = cur.left;      // go left
            else if (key > cur.key) cur = cur.right; // go right
            else return true;                        // key found
        }
        return false; // not found
    }

    // ============================ SPLIT =============================
    // Recursively split treap into (< key) and (>= key)
    private Split split(Node n, int key) {
        if (n == null) return new Split(null, null); // base case

        if (key <= n.key) {
            Split s = split(n.left, key);  // recurse left
            n.left = s.right;              // reattach right to current node
            return new Split(s.left, n);
        } else {
            Split s = split(n.right, key); // recurse right
            n.right = s.left;              // reattach left to current node
            return new Split(n, s.right);
        }
    }

    public Treap[] split(int key) {
        Split s = split(root, key);        // split root treap
        Treap left = new Treap();
        Treap right = new Treap();
        left.root = s.left;                // assign split results
        right.root = s.right;
        return new Treap[] { left, right };
    }

    // ============================ MERGE =============================
    // Combine two treaps assuming all keys in L < all keys in R
    private Node merge(Node L, Node R) {
        if (L == null || R == null)
            return (L != null) ? L : R; // base case

        if (L.priority < R.priority) {
            L.right = merge(L.right, R);  // recurse right on L
            return L;
        } else {
            R.left = merge(L, R.left);    // recurse left on R
            return R;
        }
    }

    public static Treap merge(Treap left, Treap right) {
        Treap t = new Treap();
        t.root = t.merge(left.root, right.root); // call internal merge
        return t;
    }

    // ============================ INORDER =============================
    // Iterative inorder traversal: returns sorted list of keys
    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        Deque<Node> stack = new ArrayDeque<>();
        Node cur = root;

        while (cur != null || !stack.isEmpty()) {
            while (cur != null) {
                stack.push(cur);       // go as far left as possible
                cur = cur.left;
            }
            cur = stack.pop();         // visit node
            result.add(cur.key);       // add key to result
            cur = cur.right;           // process right child
        }

        return result;
    }



    public static void main(String[] args) throws Exception {
        Treap t = new Treap();
        List<String> lines = java.nio.file.Files.readAllLines(java.nio.file.Paths.get(args[0]));

        String mode = lines.get(0).trim();
        String argsLine = lines.get(1).trim();

        if (mode.equals("Merge")) {
            String[] parts = argsLine.split(" ");
            int n1 = Integer.parseInt(parts[0]);
            int n2 = Integer.parseInt(parts[1]);
            List<String> ops1 = lines.subList(2, 2 + n1);
            List<String> ops2 = lines.subList(2 + n1, 2 + n1 + n2);
            Treap t1 = runTreapOps(ops1);
            Treap t2 = runTreapOps(ops2);
            Treap merged = Treap.merge(t1, t2);
            System.out.println("Merged inorder: " + merged.inorder());

        } else if (mode.equals("Split")) {
            int n = Integer.parseInt(argsLine);
            List<String> ops = lines.subList(2, 2 + n);
            int splitKey = Integer.parseInt(lines.get(2 + n).trim());
            Treap tSplit = runTreapOps(ops);
            Treap[] parts = tSplit.split(splitKey);
            System.out.println("Left treap inorder: " + parts[0].inorder());
            System.out.println("Right treap inorder: " + parts[1].inorder());

        } else if (mode.equals("Basic")) {
            int n = Integer.parseInt(argsLine);
            List<String> ops = lines.subList(2, 2 + n);
            runTreapOps(ops);
        }
    }

    // Execute a list of operations like Insert/Delete/Search/Inorder
    private static Treap runTreapOps(List<String> lines) {
        Treap t = new Treap();
        for (String line : lines) {
            String[] parts = line.trim().split("\\s+");
            if (parts.length == 0) continue;
            String cmd = parts[0];
            if (cmd.equals("Insert")) {
                t.insert(Integer.parseInt(parts[1]));
            } else if (cmd.equals("Delete")) {
                t.delete(Integer.parseInt(parts[1]));
            } else if (cmd.equals("Search")) {
                boolean found = t.search(Integer.parseInt(parts[1]));
                System.out.println("Search " + parts[1] + ": " + (found ? "Found" : "Not Found"));
            } else if (cmd.equals("Inorder")) {
                System.out.println("Inorder: " + t.inorder());
            }
        }
        return t;
    }
}
