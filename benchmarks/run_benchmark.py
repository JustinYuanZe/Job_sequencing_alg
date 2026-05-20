"""
Job Sequencing - Benchmark Pipeline (Single Machine)
===================================================
Compiles and executes four C++ job sequencing algorithms on test cases,
saves benchmark results to CSV, and generates high-quality visualizations.

Four approaches:
  1. Naive Greedy with linear slot scan       O(N^2)
  2. Min-Heap / Priority Queue                O(N log N)
  3. Disjoint Set Union (DSU)                 O(N log D)
  4. Radix Sort + DSU (Proposed Optimization)  O(N alpha(D)) - Linear Time

Usage:
  python benchmarks/run_benchmark.py
"""

import csv
import os
import platform
import statistics
import subprocess
import sys
import shutil
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
    "Optimized DSU (Radix) O(N)": {
        "source": "src/greedy_dsu_radix.cpp",
        "binary": "bin/dsu_radix",
        "color": "#9B5DE5",
        "marker": "D",
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
REPEATS = 5
OUTPUT_DIR = "results"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "job_sequencing_benchmark.csv")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Convert Windows path to WSL path
def to_wsl_path(win_path):
    abs_path = os.path.abspath(win_path)
    drive = abs_path[0].lower()
    rest = abs_path[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"

USE_WSL = False

def detect_compiler():
    global USE_WSL
    gpp = shutil.which("g++")
    if gpp:
        USE_WSL = False
        return gpp

    try:
        r = subprocess.run(
            ["wsl", "which", "g++"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0 and r.stdout.strip():
            USE_WSL = True
            return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None

def run_cmd(args, timeout=TIMEOUT_SECONDS):
    if USE_WSL:
        wsl_project = to_wsl_path(PROJECT_ROOT)
        cmd_str = " ".join(args)
        full_cmd = ["wsl", "bash", "-c", f"cd '{wsl_project}' && {cmd_str}"]
    else:
        full_cmd = args
    return subprocess.run(
        full_cmd, capture_output=True, text=True, timeout=timeout
    )

# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------

def compile_all():
    print("=" * 70)
    print("  COMPILING ALGORITHMS")
    print("=" * 70)

    os.makedirs("bin", exist_ok=True)
    gpp_path = detect_compiler()
    if gpp_path is None:
        print("  [ERROR] g++ compiler not found!")
        return False

    mode = "WSL" if USE_WSL else "native"
    print(f"  Compiler: {gpp_path} ({mode})")

    for name, cfg in ALGORITHMS.items():
        src = cfg["source"]
        out = cfg["binary"]
        compile_args = ["g++", "-std=c++17", "-O2", src, "-o", out]
        print(f"  Compiling {name} ...")
        try:
            r = run_cmd(compile_args, timeout=30)
            if r.returncode != 0:
                print(f"    [FAILED] {r.stderr.strip()}")
                return False
            print("    [OK]")
        except Exception as e:
            print(f"    [FAILED] {e}")
            return False
    print()
    return True

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_one(binary, testfile):
    try:
        r = run_cmd([f"./{binary}", testfile], timeout=TIMEOUT_SECONDS)
        if r.returncode != 0:
            return None
        parts = r.stdout.strip().split()
        if len(parts) < 3:
            return None
        jobs_scheduled = int(parts[0])
        profit = int(parts[1])
        time_ms = float(parts[2])
        return jobs_scheduled, profit, time_ms
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "TIMEOUT", None
    except Exception as e:
        return "ERROR", "ERROR", None

def run_benchmarks():
    print("=" * 70)
    print("  RUNNING BENCHMARKS")
    print("=" * 70)

    results = []
    
    for testfile, n in TEST_CASES:
        if not os.path.exists(testfile):
            print(f"  [SKIP] {testfile} not found")
            continue

        print(f"\n  N = {n:,}")
        for name, cfg in ALGORITHMS.items():
            binary = cfg["binary"]
            if not os.path.exists(binary):
                print(f"    {name:<28} binary missing")
                continue

            # Check for Naive Greedy timeout on large datasets to avoid wasting time
            if name == "Naive O(N^2)" and n >= 50000:
                print(f"    {name:<28} [SKIPPED (O(N^2) too slow for N >= 50K)]")
                results.append({
                    "N": n,
                    "algorithm": name,
                    "scheduled": "N/A",
                    "profit": "N/A",
                    "median_ms": None,
                    "min_ms": None,
                    "max_ms": None
                })
                continue

            times = []
            scheduled = None
            profit = None
            
            for rep in range(REPEATS):
                res = run_one(binary, testfile)
                if res is not None:
                    sch, prof, t = res
                    if t is not None:
                        times.append(t)
                        scheduled = sch
                        profit = prof
            
            if times:
                med = statistics.median(times)
                mn = min(times)
                mx = max(times)
                print(f"    {name:<28} profit={profit:<10} time={med:>10.4f} ms")
                results.append({
                    "N": n,
                    "algorithm": name,
                    "scheduled": scheduled,
                    "profit": profit,
                    "median_ms": med,
                    "min_ms": mn,
                    "max_ms": mx
                })
            else:
                print(f"    {name:<28} FAILED or TIMED OUT")
                results.append({
                    "N": n,
                    "algorithm": name,
                    "scheduled": "FAIL",
                    "profit": "FAIL",
                    "median_ms": None,
                    "min_ms": None,
                    "max_ms": None
                })
    return results

def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fieldnames = ["N", "algorithm", "scheduled", "profit", "median_ms", "min_ms", "max_ms"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"\n  Results saved to: {OUTPUT_CSV}")

# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_results():
    if not os.path.exists(OUTPUT_CSV):
        print(f"CSV results file {OUTPUT_CSV} does not exist. Cannot plot.")
        return

    # Load data
    data = {}
    with open(OUTPUT_CSV) as f:
        reader = csv.DictReader(f)
        for r in reader:
            alg = r["algorithm"]
            n = int(r["N"])
            med = r["median_ms"]
            if med and med != "":
                med = float(med)
            else:
                med = None
            if alg not in data:
                data[alg] = {"x": [], "y": []}
            if med is not None:
                data[alg]["x"].append(n)
                data[alg]["y"].append(med)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    for name, cfg in ALGORITHMS.items():
        if name in data and data[name]["x"]:
            ax.plot(
                data[name]["x"],
                data[name]["y"],
                label=name,
                color=cfg["color"],
                marker=cfg["marker"],
                linewidth=2.5,
                markersize=8,
                markeredgecolor="white",
                markeredgewidth=1.5
            )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of Jobs (N)", fontsize=12, fontweight="bold", labelpad=8)
    ax.set_ylabel("Execution Time (ms)", fontsize=12, fontweight="bold", labelpad=8)
    ax.set_title("Job Sequencing with Deadlines -- Empirical Performance Curve", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=10, loc="upper left", frameon=True, facecolor="white", edgecolor="none")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    
    # Customizing spines and ticks
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "job_sequencing_comparison.png")
    fig.savefig(path, dpi=200)
    print(f"  [OK] Plot saved: {path}")
    plt.close(fig)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.chdir(PROJECT_ROOT)

    if not compile_all():
        print("Compilation failed. Exiting.")
        sys.exit(1)

    results = run_benchmarks()
    save_results(results)
    plot_results()
    print("\nBenchmark completed successfully.")

if __name__ == "__main__":
    main()
