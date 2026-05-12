"""
Job Sequencing - Benchmark Runner
==================================
Compiles and executes three C++ scheduling algorithms on
pre-generated test cases, then plots performance curves.

Three approaches:
  1. Naive Greedy with linear slot scan   O(N^2)
  2. Min-Heap / Priority Queue            O(N log N)
  3. Disjoint Set Union (DSU)             O(N log D)

Usage:
  python benchmarks/run_benchmark.py
"""

import os
import subprocess
import sys
import time

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "Naive O(N^2)": {
        "source": "src/greedy_baseline.cpp",
        "binary": "bin/baseline",
        "color": "#E63946",
        "marker": "o",
    },
    "Min-Heap O(N log N)": {
        "source": "src/greedy_heap.cpp",
        "binary": "bin/heap",
        "color": "#457B9D",
        "marker": "s",
    },
    "DSU O(N log D)": {
        "source": "src/greedy_dsu.cpp",
        "binary": "bin/dsu",
        "color": "#2A9D8F",
        "marker": "^",
    },
}

TEST_CASES = [
    ("tests/test_tiny_n10.txt", 10),
    ("tests/test_small_n100.txt", 100),
    ("tests/test_medium_n500.txt", 500),
    ("tests/test_large_n2000.txt", 2000),
    ("tests/test_huge_n10000.txt", 10000),
    ("tests/test_massive_n50000.txt", 50000),
]

TIMEOUT_SECONDS = 300


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------


def compile_all():
    print("=" * 60)
    print("  COMPILING")
    print("=" * 60)

    os.makedirs("bin", exist_ok=True)
    ok = True

    for name, cfg in ALGORITHMS.items():
        src = cfg["source"]
        out = cfg["binary"]
        cmd = f"g++ -std=c++17 -O2 {src} -o {out}"
        print(f"  {name}")
        print(f"    {cmd}")
        if os.system(cmd) != 0:
            print(f"    [FAILED]")
            ok = False
        else:
            print(f"    [OK]")
        print()
    return ok


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def run_one(binary, testfile):
    try:
        r = subprocess.run(
            [binary, testfile], capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
        if r.returncode != 0:
            return None
        parts = r.stdout.strip().split()
        if len(parts) < 3:
            return None
        return float(parts[2])
    except:
        return None


def run_all():
    print("=" * 60)
    print("  RUNNING BENCHMARKS")
    print("=" * 60)

    data = {name: {} for name in ALGORITHMS}

    for testfile, n in TEST_CASES:
        if not os.path.exists(testfile):
            print(f"  [SKIP] {testfile} not found")
            continue

        print(f"\n  N = {n:,}")
        for name, cfg in ALGORITHMS.items():
            binary = cfg["binary"]
            if not os.path.exists(binary):
                print(f"    {name:<22} binary missing")
                continue

            t = run_one(binary, testfile)
            if t is not None:
                print(f"    {name:<22} {t:>10.4f} ms")
                data[name][n] = t
            else:
                print(f"    {name:<22} {'FAILED':>10}")

    return data


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_results(data):
    os.makedirs("results", exist_ok=True)

    plt.figure(figsize=(11, 6))

    for name, cfg in ALGORITHMS.items():
        xs, ys = [], []
        for n, t in sorted(data[name].items()):
            xs.append(n)
            ys.append(t)
        if xs:
            plt.plot(
                xs,
                ys,
                label=name,
                color=cfg["color"],
                marker=cfg["marker"],
                linewidth=2,
                markersize=7,
            )

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of Jobs (N)", fontsize=11)
    plt.ylabel("Execution Time (ms)", fontsize=11)
    plt.title(
        "Job Sequencing — Algorithm Performance Comparison",
        fontweight="bold",
        fontsize=13,
    )
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.35, which="both")
    plt.tight_layout()

    path = "results/benchmark_comparison.png"
    plt.savefig(path, dpi=150)
    print(f"\n  Plot saved: {path}")
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if not compile_all():
        print("Compilation failed. Exiting.")
        return

    data = run_all()
    plot_results(data)
    print("\nDone.")


if __name__ == "__main__":
    main()
