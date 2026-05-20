"""
Johnson's Rule -- Benchmark Pipeline (2-Machine Flow Shop)
============================================================
Compiles Johnson's Rule C++ implementation via WSL, runs it on all generated
datasets, collects timing data, and saves raw results as CSV.

Usage:
  python benchmarks/run_johnson_benchmark.py

Workflow:
  1. Compile  src/johnson.cpp  ->  bin/johnson  (via WSL g++)
  2. Run correctness samples with --verify
  3. Read manifest from tests/johnson/manifest.txt
  4. For each dataset: run binary, record N, dist_type, makespan, time (ms)
  5. Repeat each run REPEATS times, take median
  6. Save results to results/johnson/benchmark_data.csv
"""

import csv
import os
import platform
import statistics
import subprocess
import sys
import shutil

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOURCE = "src/johnson.cpp"
BINARY = "bin/johnson"
MANIFEST = "tests/johnson/manifest.txt"
OUTPUT_DIR = "results/johnson"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "benchmark_data.csv")

TIMEOUT_SECONDS = 300   # 5 minutes max per run
REPEATS = 5             # number of repetitions per dataset

# Project root (Windows path)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Convert Windows path to WSL path
def to_wsl_path(win_path):
    """Convert a Windows absolute path to WSL /mnt/ path."""
    abs_path = os.path.abspath(win_path)
    # C:\foo\bar -> /mnt/c/foo/bar
    drive = abs_path[0].lower()
    rest = abs_path[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"

# Detect whether to use WSL or native g++
USE_WSL = False

def detect_compiler():
    """Detect g++ -- prefer native, fall back to WSL."""
    global USE_WSL

    # Try native g++ first
    gpp = shutil.which("g++")
    if gpp:
        USE_WSL = False
        return gpp

    # Try WSL
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
    """Run a command, using WSL wrapper if needed."""
    if USE_WSL:
        wsl_project = to_wsl_path(PROJECT_ROOT)
        cmd_str = " ".join(args)
        full_cmd = ["wsl", "bash", "-c",
                    f"cd '{wsl_project}' && {cmd_str}"]
    else:
        full_cmd = args
    return subprocess.run(
        full_cmd, capture_output=True, text=True, timeout=timeout
    )


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------

def compile_johnson():
    print("=" * 70)
    print("  COMPILING JOHNSON'S RULE")
    print("=" * 70)

    os.makedirs("bin", exist_ok=True)

    gpp_path = detect_compiler()
    if gpp_path is None:
        print("  [ERROR] g++ compiler not found!")
        print("  Install MinGW-w64, add g++ to PATH, or install g++ in WSL.")
        return False

    mode = "WSL" if USE_WSL else "native"
    print(f"  Compiler: {gpp_path} ({mode})")

    compile_args = ["g++", "-std=c++17", "-O2", SOURCE, "-o", BINARY]
    print(f"  Command:  {' '.join(compile_args)}")

    try:
        r = run_cmd(compile_args, timeout=30)
        if r.returncode != 0:
            print(f"  [FAILED] {r.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  [FAILED] {e}")
        return False

    print("  [OK] Compilation successful.")
    print()
    return True


# ---------------------------------------------------------------------------
# Run correctness tests
# ---------------------------------------------------------------------------

def run_correctness():
    print("=" * 70)
    print("  CORRECTNESS VERIFICATION")
    print("=" * 70)

    sample_files = [
        ("tests/johnson/sample_4jobs.txt", "4 jobs (expected makespan=24)"),
        ("tests/johnson/sample_5jobs.txt", "5 jobs"),
    ]

    for sample_file, desc in sample_files:
        if os.path.exists(sample_file):
            try:
                r = run_cmd(
                    [f"./{BINARY}", sample_file, "--verify", "--print-seq"],
                    timeout=10
                )
                print(f"  {desc}:")
                print(f"    stdout: {r.stdout.strip()}")
                if r.stderr:
                    for line in r.stderr.strip().split("\n"):
                        print(f"    {line}")
            except Exception as e:
                print(f"  [ERROR] {e}")
        else:
            print(f"  [SKIP] {sample_file} not found")

    print()


# ---------------------------------------------------------------------------
# Run single test
# ---------------------------------------------------------------------------

def run_single(testfile):
    """Run the binary on a test file. Returns (makespan, N, time_ms) or None."""
    try:
        r = run_cmd([f"./{BINARY}", testfile], timeout=TIMEOUT_SECONDS)
        if r.returncode != 0:
            return None
        parts = r.stdout.strip().split()
        if len(parts) < 3:
            return None
        makespan = int(parts[0])
        N = int(parts[1])
        time_ms = float(parts[2])
        return makespan, N, time_ms
    except subprocess.TimeoutExpired:
        print(f"      [TIMEOUT after {TIMEOUT_SECONDS}s]")
        return None
    except Exception as e:
        print(f"      [ERROR: {e}]")
        return None


# ---------------------------------------------------------------------------
# Run all benchmarks
# ---------------------------------------------------------------------------

def run_all():
    print("=" * 70)
    print("  RUNNING JOHNSON'S RULE BENCHMARKS")
    print("=" * 70)

    if not os.path.exists(MANIFEST):
        print(f"  Manifest not found: {MANIFEST}")
        print("  Run generate_johnson_datasets.py first.")
        return []

    # Parse manifest
    datasets = []
    with open(MANIFEST) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                filepath, N, dist_type = parts[0], int(parts[1]), parts[2]
                datasets.append((filepath, N, dist_type))

    results = []
    prev_n = None

    for filepath, N, dist_type in datasets:
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filepath} -- file not found")
            continue

        if N != prev_n:
            print(f"\n  {'='*60}")
            print(f"  N = {N:>10,}")
            print(f"  {'='*60}")
            prev_n = N

        times = []
        makespans = []
        for rep in range(REPEATS):
            result = run_single(filepath)
            if result is not None:
                makespan, _, t = result
                times.append(t)
                makespans.append(makespan)

        if times:
            median_time = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            makespan_val = makespans[0]  # same for all runs (deterministic)
            print(f"    {dist_type:<12}  makespan={makespan_val:>10,}  "
                  f"time={median_time:>10.3f} ms  "
                  f"(min={min_time:.3f}, max={max_time:.3f})")
            results.append({
                "N": N,
                "dist_type": dist_type,
                "makespan": makespan_val,
                "median_ms": median_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "runs": len(times),
            })
        else:
            print(f"    {dist_type:<12}  ALL RUNS FAILED")

    return results


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["N", "dist_type", "makespan", "median_ms", "min_ms", "max_ms", "runs"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\n  Results saved to: {OUTPUT_CSV}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.chdir(PROJECT_ROOT)

    if not compile_johnson():
        print("\nCompilation failed. Aborting.")
        sys.exit(1)

    run_correctness()

    results = run_all()

    if results:
        save_results(results)
        print("\n" + "=" * 70)
        print("  BENCHMARK COMPLETE")
        print("=" * 70)
        print(f"  Total datasets run: {len(results)}")
        print(f"  Results CSV: {OUTPUT_CSV}")
        print(f"\n  Next step: python benchmarks/plot_johnson_results.py")
        print("=" * 70)
    else:
        print("\nNo results collected.")


if __name__ == "__main__":
    main()
