import sys, random
sys.setrecursionlimit(1_000_000)
rnd = random.Random(42) # fixed seed for per‑crop balancing

# --------- Per‑crop Treap for(COUNT) ----------
class PNode:
    __slots__ = ('key','prio','l','r','sz')
    def __init__(self, key):
        self.key = key
        self.prio = rnd.randint(0, 2**31-1)
        self.l = self.r = None
        self.sz = 1

def psz(t): return 0 if t is None else t.sz
def ppull(t): 
    if t: t.sz = 1 + psz(t.l) + psz(t.r)

def psplit(t, key): # ≤key | >key
    if t is None: return (None, None)
    if key < t.key:
        a,b = psplit(t.l, key)
        t.l = b; ppull(t)
        return (a, t)
    a,b = psplit(t.r, key)
    t.r = a; ppull(t)
    return (t, b)

def pmerge(a, b):
    if a is None: return b
    if b is None: return a
    if a.prio > b.prio:
        a.r = pmerge(a.r, b); ppull(a); return a
    b.l = pmerge(a, b.l); ppull(b); return b

def pinsert(root, key):
    node = PNode(key)
    l,r = psplit(root, key)
    return pmerge(pmerge(l, node), r)

def perase(root, key):
    if root is None: return None
    if root.key == key:
        return pmerge(root.l, root.r)
    if key < root.key:
        root.l = perase(root.l, key)
    else:
        root.r = perase(root.r, key)
    ppull(root); return root

def pcount_less(t, key):
    if t is None: return 0
    if key <= t.key: return pcount_less(t.l, key)
    return psz(t.l) + 1 + pcount_less(t.r, key)


# --------- Global Treap (STRONGEST) --------
class GNode:
    __slots__ = ('key','crop','time','l','r','sz','maxTime','maxIdx','maxCrop')
    def __init__(self, key, crop, time):
        self.key, self.crop, self.time = key, crop, time
        self.l = self.r = None
        self.sz = 1
        self.maxTime, self.maxIdx, self.maxCrop = time, key, crop

def gsz(t): return 0 if t is None else t.sz
def gpull(t):
    if not t: return
    t.sz = 1 + gsz(t.l) + gsz(t.r)
    t.maxTime, t.maxIdx, t.maxCrop = t.time, t.key, t.crop
    for ch in (t.l, t.r):
        if ch and (ch.maxTime > t.maxTime or (ch.maxTime==t.maxTime and ch.maxIdx < t.maxIdx)):
            t.maxTime, t.maxIdx, t.maxCrop = ch.maxTime, ch.maxIdx, ch.maxCrop

def gsplit(t, key): # ≤key | >key
    if t is None: return (None, None)
    if key < t.key:
        a,b = gsplit(t.l, key)
        t.l = b; gpull(t); return (a, t)
    a,b = gsplit(t.r, key)
    t.r = a; gpull(t); return (t, b)

def gmerge(a, b): # heap by (time, -idx)
    if a is None: return b
    if b is None: return a
    if (a.time, -a.key) > (b.time, -b.key):
        a.r = gmerge(a.r, b); gpull(a); return a
    b.l = gmerge(a, b.l); gpull(b); return b

def ginsert(root, idx, crop, time):
    node = GNode(idx, crop, time)
    l,r = gsplit(root, idx)
    return gmerge(gmerge(l, node), r)

def gerase(root, idx):
    if root is None: return None
    if root.key == idx:
        return gmerge(root.l, root.r)
    if idx < root.key:
        root.l = gerase(root.l, idx)
    else:
        root.r = gerase(root.r, idx)
    gpull(root); return root


# --------- Game -------------
N, Q = map(int, sys.stdin.readline().split())
cropType = list(map(int, sys.stdin.readline().split()))
cropTime = [0]*N
globalTime = 0
perCrop = {}
globalRoot = None
for i,v in enumerate(cropType):
    perCrop[v] = pinsert(perCrop.get(v), i)
    globalRoot = ginsert(globalRoot, i, v, 0)

undo = [] # stack of (idx, crop, time), for the undo operation
out = [] # output buffer

def apply_replace(idx, newCrop):
    global globalTime, globalRoot
    undo.append((idx, cropType[idx], cropTime[idx]))
    oldCrop = cropType[idx]
    perCrop[oldCrop] = perase(perCrop[oldCrop], idx)
    perCrop[newCrop] = pinsert(perCrop.get(newCrop), idx)
    globalRoot = gerase(globalRoot, idx)
    globalTime += 1
    globalRoot = ginsert(globalRoot, idx, newCrop, globalTime)
    cropType[idx] = newCrop; cropTime[idx] = globalTime

def undo_replace(idx, oldCrop, oldTime):
    global globalRoot
    perCrop[cropType[idx]] = perase(perCrop[cropType[idx]], idx)
    globalRoot = gerase(globalRoot, idx)
    perCrop[oldCrop] = pinsert(perCrop.get(oldCrop), idx)
    globalRoot = ginsert(globalRoot, idx, oldCrop, oldTime)
    cropType[idx] = oldCrop; cropTime[idx] = oldTime

for _ in range(Q):
    parts = sys.stdin.readline().split()
    op = parts[0]
    if op == 'C':
        i,v = map(int, parts[1:])
        ans = pcount_less(perCrop.get(v), i) if v in perCrop else 0
        out.append(str(ans))
    elif op == 'R':
        i,v = map(int, parts[1:])
        apply_replace(i, v)
    elif op == 'U':
        k = int(parts[1])
        for _ in range(k):
            idx, oc, ot = undo.pop()
            undo_replace(idx, oc, ot)
    else:                               # S l r
        l,r = map(int, parts[1:])
        a,b = gsplit(globalRoot, l-1)
        mid,c = gsplit(b, r)
        out.append(str(mid.maxCrop))
        globalRoot = gmerge(a, gmerge(mid, c))

sys.stdout.write("\n".join(out))
