import subprocess
import time
import random
import tempfile
import os

TREAP_SCRIPT = "treap.py"  # Change if your file has a different name

def generate_basic_test_case(num_ops=100000):
    ops = ["Basic", str(num_ops)]
    inserted = set()
    for _ in range(num_ops):
        op = random.choices(["Insert", "Delete", "Search", "Inorder"], weights=[4, 3, 2, 1])[0]
        if op == "Insert":
            x = random.randint(1, 1000)
            inserted.add(x)
            ops.append(f"Insert {x}")
        elif op == "Delete":
            if inserted:
                x = random.choice(list(inserted))
                inserted.discard(x)
                ops.append(f"Delete {x}")
            else:
                ops.append(f"Delete {random.randint(1, 1000)}")
        elif op == "Search":
            x = random.randint(1, 1000)
            ops.append(f"Search {x}")
        else:
            ops.append("Inorder")
    return "\n".join(ops)

def run_basic_test():
    input_str = generate_basic_test_case(100000)
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(input_str)
        f.flush()
        f_path = f.name

    try:
        start = time.time()
        result = subprocess.run(
            ["python3", TREAP_SCRIPT, f_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        end = time.time()
        print(f"Execution Time: {end - start:.4f} seconds\n")
    finally:
        os.remove(f_path)

if __name__ == "__main__":
    run_basic_test()
