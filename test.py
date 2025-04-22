# test.py

import subprocess
import random
import time
import sys

# Path to your treap implementation
TREAP_SCRIPT = 'pc.py'

# --- Brute‐Force Reference ---
class BruteForce:
    def __init__(self):
        self.events = {}  # date -> priority

    def add(self, date, p):
        self.events[date] = p

    def remove(self, date):
        self.events.pop(date, None)

    def update(self, date, p):
        self.events[date] = p

    def query(self, thr, sd, ed):
        res = [(d, p) for d,p in self.events.items() if sd <= d <= ed and p > thr]
        res.sort(key=lambda x: x[0])
        return res

def generate_test(N=10000, Q=10000):
    valid_dates = []
    for year in range(0, 2025):
        for month in range(1, 13):
            if month in (1,3,5,7,8,10,12):
                days = 31
            elif month in (4,6,9,11):
                days = 30
            else:  # Feb
                if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
                    days = 29
                else:
                    days = 28
            for day in range(1, days+1):
                valid_dates.append(year*10000 + month*100 + day)

    dates = random.sample(valid_dates, N+Q)
    lines = [f"{N} {Q}"]
    current = set()

    # initial events
    for i in range(N):
        d = dates[i]
        p = random.getrandbits(32)
        lines.append(f"{d} {p}")
        current.add(d)

    idx = 0
    # operations
    for _ in range(Q):
        op = random.choices(['ADD','REMOVE','UPDATE','QUERY'], [0.3,0.2,0.2,0.3])[0]
        if op == 'ADD' and len(current) < N+Q:
            d = dates[N + idx]; idx+=1
            if d not in current:
                p = random.getrandbits(32)
                lines.append(f"ADD {d} {p}")
                current.add(d)
        elif op == 'REMOVE' and current:
            d = random.choice(list(current))
            lines.append(f"REMOVE {d}")
            current.remove(d)
        elif op == 'UPDATE' and current:
            d = random.choice(list(current))
            p = random.getrandbits(32)
            lines.append(f"UPDATE {d} {p}")
        elif op == 'QUERY' and current:
            sd, ed = random.sample(list(current), 2)
            if sd > ed:
                sd, ed = ed, sd
            thr = random.getrandbits(32)
            lines.append(f"QUERY {thr} {sd} {ed}")

    return "\n".join(lines) + "\n"

# --- Brute‐Force Runner (line‐based) ---
def run_brute(input_str):
    lines = input_str.strip().splitlines()
    N, Q = map(int, lines[0].split())
    bf = BruteForce()
    idx = 1

    # load initial
    for _ in range(N):
        d, p = map(int, lines[idx].split())
        bf.add(d, p)
        idx += 1

    out = []
    # execute ops
    for _ in range(Q):
        parts = lines[idx].split()
        idx += 1
        op = parts[0]
        if op == 'ADD':
            d, p = map(int, parts[1:3])
            bf.add(d, p)
        elif op == 'REMOVE':
            d = int(parts[1])
            bf.remove(d)
        elif op == 'UPDATE':
            d, p = map(int, parts[1:3])
            bf.update(d, p)
        else:  # QUERY
            thr, sd, ed = map(int, parts[1:4])
            res = bf.query(thr, sd, ed)
            out.append(str(len(res)))
            for d,p in res:
                out.append(f"{d} {p}")

    return "\n".join(out)

# --- Main Test Driver ---
def main():
    random.seed(0)
    test_input = generate_test()

    # Run treap via subprocess with timeout
    try:
        t0 = time.time()
        proc = subprocess.run(
            ["python3", TREAP_SCRIPT],
            input=test_input,
            text=True,
            capture_output=True,
            timeout=10
        )
        t1 = time.time()
        treap_out = proc.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Treap implementation timed out", file=sys.stderr)
        sys.exit(1)

    # Run brute
    t2 = time.time()
    brute_out = run_brute(test_input).strip()
    t3 = time.time()

    # Report
    print(f"Treap time: {t1-t0:.3f}s")
    print(f"Brute time: {t3-t2:.3f}s")
    print("Outputs match:", treap_out == brute_out)

if __name__ == '__main__':
    main()
