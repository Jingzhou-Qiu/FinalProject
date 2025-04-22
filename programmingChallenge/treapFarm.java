import java.io.*;
import java.util.*;

public class treapFarm {
    // ----------------- Per‑crop Treap (for COUNT) --------------------
    static final Random RNG = new Random(42); // fixed seed for per‑crop balancing
    static class PNode {
        int key, prio = RNG.nextInt(); // key and priority value for the Treap
        PNode left, right;
        int size = 1;
    }
    static int getSize(PNode t){ return t == null ? 0 : t.size; }
    static void pull(PNode t){ if(t!=null) t.size = 1 + getSize(t.left) + getSize(t.right); }
    static PNode[] pSplit(PNode t, int key){
        if(t==null) return new PNode[]{null,null};
        if(key < t.key){
            PNode[] sp = pSplit(t.left, key);
            t.left = sp[1]; pull(t);
            return new PNode[]{sp[0], t};
        } else {
            PNode[] sp = pSplit(t.right, key);
            t.right = sp[0]; pull(t);
            return new PNode[]{t, sp[1]};
        }
    }
    static PNode pMerge(PNode a, PNode b){
        if(a==null) return b;
        if(b==null) return a;
        if(a.prio > b.prio){
            a.right = pMerge(a.right, b); pull(a); return a;
        } else {
            b.left = pMerge(a, b.left); pull(b); return b;
        }
    }
    static PNode pInsert(PNode root, int key){
        PNode node = new PNode(); node.key = key;
        PNode[] sp = pSplit(root, key);
        return pMerge(pMerge(sp[0], node), sp[1]);
    }
    static PNode pErase(PNode root, int key){
        if(root==null) return null;
        if(root.key == key){
            return pMerge(root.left, root.right);
        } else if(key < root.key){
            root.left = pErase(root.left, key);
        } else {
            root.right = pErase(root.right, key);
        }
        pull(root);
        return root;
    }
    static int pCountLess(PNode t, int key){
        if(t==null) return 0;
        if(key <= t.key) return pCountLess(t.left, key);
        return getSize(t.left) + 1 + pCountLess(t.right, key);
    }

    // ------------------ Global Treap (for STRONGEST) ------------
    static class GNode {
        int key; // plot index
        int crop; // crop type
        int time; // last update timestamp
        GNode left, right;
        int size = 1;
        int maxTime;
        int maxIdx; // leftmost index with maxTime
        int maxCrop; // crop at maxIdx
    }
    static int getSize(GNode t){ return t==null ? 0 : t.size; }
    static void pull(GNode t){
        if(t==null) return;
        t.size = 1 + getSize(t.left) + getSize(t.right);

        // start with self
        t.maxTime = t.time;
        t.maxIdx  = t.key;
        t.maxCrop = t.crop;

        // left subtree
        if(t.left != null){
            if(t.left.maxTime > t.maxTime ||
                    (t.left.maxTime == t.maxTime && t.left.maxIdx < t.maxIdx)){
                t.maxTime = t.left.maxTime;
                t.maxIdx  = t.left.maxIdx;
                t.maxCrop = t.left.maxCrop;
            }
        }
        // right subtree
        if(t.right != null){
            if(t.right.maxTime > t.maxTime ||
                    (t.right.maxTime == t.maxTime && t.right.maxIdx < t.maxIdx)){
                t.maxTime = t.right.maxTime;
                t.maxIdx  = t.right.maxIdx;
                t.maxCrop = t.right.maxCrop;
            }
        }
    }
    static GNode[] gSplit(GNode t, int key){
        if(t==null) return new GNode[]{null,null};
        if(key < t.key){
            GNode[] sp = gSplit(t.left, key);
            t.left = sp[1]; pull(t);
            return new GNode[]{sp[0], t};
        } else {
            GNode[] sp = gSplit(t.right, key);
            t.right = sp[0]; pull(t);
            return new GNode[]{t, sp[1]};
        }
    }
    static GNode gMerge(GNode a, GNode b){
        if(a==null) return b;
        if(b==null) return a;
        if(a.time > b.time){
            a.right = gMerge(a.right, b); pull(a); return a;
        } else if(b.time > a.time){
            b.left = gMerge(a, b.left); pull(b); return b;
        } else {
            // if tie by timestamp, then break by index (smaller index as root to keep leftmost)
            if(a.key < b.key){
                a.right = gMerge(a.right, b); pull(a); return a;
            } else {
                b.left = gMerge(a, b.left); pull(b); return b;
            }
        }
    }
    static GNode gInsert(GNode root, int idx, int crop, int time){
        GNode node = new GNode();
        node.key = idx; node.crop = crop; node.time = time;
        node.maxTime = time; node.maxIdx = idx; node.maxCrop = crop;
        GNode[] sp = gSplit(root, idx);
        return gMerge(gMerge(sp[0], node), sp[1]);
    }
    static GNode gErase(GNode root, int idx){
        if(root==null) return null;
        if(root.key == idx){
            return gMerge(root.left, root.right);
        } else if(idx < root.key){
            root.left = gErase(root.left, idx);
        } else {
            root.right = gErase(root.right, idx);
        }
        pull(root);
        return root;
    }

    // -------------------- Game vars -------------------------
    static int N, Q;
    static int[] cropType; // current crop at each plot
    static int[] cropTime; // current timestamp at each plot
    static int globalTime = 0;

    // map crop → its per‑crop Treap root
    static HashMap<Integer,PNode> perCrop = new HashMap<>();
    static GNode globalRoot = null;

    // undo stack
    static class Action {
        int idx, oldCrop, oldTime;
        Action(int i, int c, int t){ idx=i; oldCrop=c; oldTime=t; }
    }
    static Deque<Action> undoStack = new ArrayDeque<>();

    public static void main(String[] args) throws IOException {
        Scanner fs = new Scanner(System.in);
        N = fs.nextInt(); Q = fs.nextInt();
        cropType = new int[N];
        cropTime = new int[N];

        // read initial crops (timestamp = 0)
        for(int i=0; i<N; i++){
            int v = fs.nextInt();
            cropType[i] = v;
            cropTime[i] = 0;
            // per‑crop insertion
            perCrop.putIfAbsent(v, null);
            perCrop.put(v, pInsert(perCrop.get(v), i));
            // global insertion
            globalRoot = gInsert(globalRoot, i, v, 0);
        }

        StringBuilder out = new StringBuilder();
        while(Q-- > 0){
            String op = fs.next();
            if(op.equals("C")){
                int i = fs.nextInt(), v = fs.nextInt();
                PNode t = perCrop.get(v);
                int ans = (t==null ? 0 : pCountLess(t, i));
                out.append(ans).append('\n');

            } else if(op.equals("R")){
                int i = fs.nextInt(), v = fs.nextInt();
                applyReplace(i, v);

            } else if(op.equals("U")){
                int k = fs.nextInt();
                while(k-- > 0){
                    Action a = undoStack.pop();
                    // revert to a.oldCrop, a.oldTime
                    undoReplace(a.idx, a.oldCrop, a.oldTime);
                }

            } else if(op.equals("S")){
                int l = fs.nextInt(), r = fs.nextInt();
                // split into [0..l-1], [l..r], [r+1..N-1]
                GNode[] sp1 = gSplit(globalRoot, l-1);
                GNode[] sp2 = gSplit(sp1[1], r);
                int strongestCrop = sp2[0].maxCrop;
                out.append(strongestCrop).append('\n');
                globalRoot = gMerge(sp1[0], gMerge(sp2[0], sp2[1]));
            }
        }
        System.out.print(out);
    }

    // perform replace with timestamp++ and record undo
    static void applyReplace(int idx, int newCrop){
        // record old state
        undoStack.push(new Action(idx, cropType[idx], cropTime[idx]));
        // remove old from per‑crop
        int oldCrop = cropType[idx];
        perCrop.put(oldCrop, pErase(perCrop.get(oldCrop), idx));
        // insert new into per‑crop
        perCrop.putIfAbsent(newCrop, null);
        perCrop.put(newCrop, pInsert(perCrop.get(newCrop), idx));
        // update global
        globalRoot = gErase(globalRoot, idx);
        int t = ++globalTime;
        globalRoot = gInsert(globalRoot, idx, newCrop, t);
        // update arrays
        cropType[idx] = newCrop;
        cropTime[idx] = t;
    }

    // undo a replacement to oldCrop and oldTime
    static void undoReplace(int idx, int oldCrop, int oldTime){
        // remove current
        perCrop.put(cropType[idx], pErase(perCrop.get(cropType[idx]), idx));
        globalRoot = gErase(globalRoot, idx);
        // restore per‑crop
        perCrop.putIfAbsent(oldCrop, null);
        perCrop.put(oldCrop, pInsert(perCrop.get(oldCrop), idx));
        // restore global
        globalRoot = gInsert(globalRoot, idx, oldCrop, oldTime);
        // update arrays
        cropType[idx] = oldCrop;
        cropTime[idx] = oldTime;
    }
}
