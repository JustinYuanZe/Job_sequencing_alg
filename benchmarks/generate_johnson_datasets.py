"""
Johnson's Rule — Dataset Generator (2-Machine Flow Shop)
==========================================================
Generates test cases of various sizes for benchmarking Johnson's Rule
on the 2-machine flow shop scheduling problem.

Each job has:
  - p1: processing time on Machine 1
  - p2: processing time on Machine 2

Dataset types for each size:
  1. Balanced   — p1 and p2 drawn from similar ranges
  2. M1-heavy   — p1 >> p2  (Machine 1 is the bottleneck)
  3. M2-heavy   — p1 << p2  (Machine 2 is the bottleneck)
  4. Mixed      — high variance, diverse distribution

File format:
  Line 1      : N (number of jobs)
  Lines 2..N+1: p1_i  p2_i

Usage:
  python benchmarks/generate_johnson_datasets.py
"""

import os
import random


def generate_balanced(n, seed=42):
    """Both machines have similar processing times."""
    random.seed(seed)
    jobs = [(random.randint(1, 100), random.randint(1, 100)) for _ in range(n)]
    return jobs


def generate_m1_heavy(n, seed=42):
    """Machine 1 processing times are much larger than Machine 2."""
    random.seed(seed)
    jobs = [(random.randint(50, 200), random.randint(1, 50)) for _ in range(n)]
    return jobs


def generate_m2_heavy(n, seed=42):
    """Machine 2 processing times are much larger than Machine 1."""
    random.seed(seed)
    jobs = [(random.randint(1, 50), random.randint(50, 200)) for _ in range(n)]
    return jobs


def generate_mixed(n, seed=42):
    """High variance — some jobs are M1-heavy, some M2-heavy, some balanced."""
    random.seed(seed)
    jobs = []
    for _ in range(n):
        flavor = random.choice(["balanced", "m1_heavy", "m2_heavy", "extreme"])
        if flavor == "balanced":
            jobs.append((random.randint(10, 90), random.randint(10, 90)))
        elif flavor == "m1_heavy":
            jobs.append((random.randint(100, 500), random.randint(1, 20)))
        elif flavor == "m2_heavy":
            jobs.append((random.randint(1, 20), random.randint(100, 500)))
        else:  # extreme
            jobs.append((random.randint(1, 1000), random.randint(1, 1000)))
    return jobs


def save_dataset(filepath, jobs):
    """Save a dataset to file."""
    with open(filepath, "w") as f:
        f.write(f"{len(jobs)}\n")
        for p1, p2 in jobs:
            f.write(f"{p1} {p2}\n")


def human_readable(n):
    if n >= 1_000_000:
        return f"{n/1e6:.1f}M"
    elif n >= 1_000:
        return f"{n/1e3:.0f}K"
    return str(n)


GENERATORS = {
    "balanced": generate_balanced,
    "m1_heavy": generate_m1_heavy,
    "m2_heavy": generate_m2_heavy,
    "mixed":    generate_mixed,
}


def main():
    os.makedirs("tests/johnson", exist_ok=True)

    # -----------------------------------------------------------------------
    # Dataset configurations: (label, N)
    # Each size will be generated with ALL distribution types.
    # -----------------------------------------------------------------------
    sizes = [
        ("tiny",      10),
        ("small",     100),
        ("medium",    500),
        ("large",     2000),
        ("xlarge",    5000),
        ("huge",      10000),
        ("massive",   20000),
        ("giant",     50000),
        ("colossal",  100000),
        ("extreme",   200000),
        ("ultra",     500000),
    ]

    dist_types = ["balanced", "m1_heavy", "m2_heavy", "mixed"]

    # Header
    print("=" * 80)
    print("  JOHNSON'S RULE — 2-MACHINE FLOW SHOP DATASET GENERATOR")
    print("=" * 80)
    print()
    print(f"  {'Label':<12} {'N':>10} {'Type':<12} {'File'}")
    print(f"  {'-'*12} {'-'*10} {'-'*12} {'-'*40}")

    generated = []

    for label, n in sizes:
        for dist_type in dist_types:
            seed = n * 100 + hash(dist_type) % 1000
            gen_func = GENERATORS[dist_type]
            jobs = gen_func(n, seed=seed)

            filename = f"tests/johnson/{label}_n{n}_{dist_type}.txt"
            save_dataset(filename, jobs)

            print(f"  {label:<12} {n:>10,} {dist_type:<12} {filename}")
            generated.append((filename, n, dist_type))

    # Also generate small correctness-check cases with known answers
    print()
    print("  Generating correctness samples ...")

    # Classic textbook example (CLRS / Operations Research)
    # 4 jobs: (p1, p2) = (5,2), (1,6), (9,7), (3,8)
    # Johnson's rule:
    #   Set A (p1<=p2): J2(1,6), J4(3,8), J3(9,7) → sorted by p1: J2, J4, J3
    #   Set B (p1>p2):  J1(5,2) → sorted by p2 desc: J1
    #   Sequence: J2 → J4 → J3 → J1
    #   Makespan: M1: 1,4,13,18  M2: 7,15,22,24  → 24
    sample1 = [(5, 2), (1, 6), (9, 7), (3, 8)]
    save_dataset("tests/johnson/sample_4jobs.txt", sample1)
    print(f"    sample_4jobs.txt -> 4 jobs, expected makespan = 24")

    # Another example: 5 jobs
    sample2 = [(2, 5), (6, 3), (7, 4), (3, 6), (4, 1)]
    save_dataset("tests/johnson/sample_5jobs.txt", sample2)
    print(f"    sample_5jobs.txt -> 5 jobs")

    # Summary
    print()
    print("=" * 80)
    print(f"  GENERATED {len(generated)} DATASETS + 2 SAMPLES")
    print("=" * 80)

    # Write manifest for the benchmark runner
    manifest_path = "tests/johnson/manifest.txt"
    with open(manifest_path, "w") as f:
        for filepath, n, dist_type in generated:
            f.write(f"{filepath} {n} {dist_type}\n")
    print(f"  Manifest: {manifest_path}")
    print(f"  Sizes: {', '.join(human_readable(n) for _, n in sizes)}")
    print(f"  Types: {', '.join(dist_types)}")
    print(f"  Total datasets: {len(generated)}")
    print()
    print("  All datasets generated successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
