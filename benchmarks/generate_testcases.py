"""
Generates 6 test cases with exponentially growing input sizes
to visualize the divergence between O(N²) and O(N log N) algorithms.
"""

import os
import random

import numpy as np


def generate_test_case(num_jobs: int, deadline_multiplier: float = 2.0):
    """
    Generate a single random test case for the Job Sequencing problem.

    Parameters
    ----------
    num_jobs : int
        Number of jobs to generate.
    deadline_multiplier : float
        Maximum deadline is computed as max(1, num_jobs * deadline_multiplier).
        This ensures a feasible schedule exists without over-constraining.

    Returns
    -------
    deadlines : list[int]
        List of deadlines for each job.
    profits : list[int]
        List of profits for each job.
    """
    max_deadline = max(1, int(num_jobs * deadline_multiplier))
    deadlines = [random.randint(1, max_deadline) for _ in range(num_jobs)]
    profits = [random.randint(1, 10000) for _ in range(num_jobs)]
    return deadlines, profits


def save_test_case(filepath: str, deadlines: list, profits: list) -> None:
    """
    Save a test case to a text file.

    Format
    ------
    Line 1        : N (number of jobs)
    Lines 2..N+1  : deadline_i profit_i
    """
    num_jobs = len(deadlines)
    with open(filepath, "w") as output_file:
        output_file.write(f"{num_jobs}\n")
        for deadline, profit in zip(deadlines, profits):
            output_file.write(f"{deadline} {profit}\n")


def estimate_complexity(num_jobs: int):
    """
    Estimate the number of elementary operations for complexity comparison.

    Parameters
    ----------
    num_jobs : int
        Number of jobs.

    Returns
    -------
    est_n_squared : str
        Human-readable estimate for O(N²).
    est_n_log_n : str
        Human-readable estimate for O(N log N).
    """
    if num_jobs <= 0:
        return "0 ops", "0 ops"

    n_sq = num_jobs * num_jobs
    n_log_n = num_jobs * np.log2(num_jobs) if num_jobs > 1 else 1

    if n_sq >= 1e9:
        est_n_squared = f"{n_sq / 1e9:.2f}B ops"
    elif n_sq >= 1e6:
        est_n_squared = f"{n_sq / 1e6:.2f}M ops"
    elif n_sq >= 1e3:
        est_n_squared = f"{n_sq / 1e3:.2f}K ops"
    else:
        est_n_squared = f"{n_sq:.0f} ops"

    if n_log_n >= 1e9:
        est_n_log_n = f"{n_log_n / 1e9:.2f}B ops"
    elif n_log_n >= 1e6:
        est_n_log_n = f"{n_log_n / 1e6:.2f}M ops"
    elif n_log_n >= 1e3:
        est_n_log_n = f"{n_log_n / 1e3:.2f}K ops"
    else:
        est_n_log_n = f"{n_log_n:.0f} ops"

    return est_n_squared, est_n_log_n


def main():
    """Main entry point: generate all test cases and sample inputs."""

    # Ensure output directory exists
    os.makedirs("tests", exist_ok=True)

    # TEST CASE CONFIGURATIONS
    # Exponential growth to clearly show O(N²) vs O(N log N) divergence
    test_configs = [
        # (name,      num_jobs,   deadline_multiplier)
        ("tiny", 10, 2.0),  # negligible runtime
        ("small", 100, 2.0),  # O(N²) begins to show
        ("medium", 500, 2.0),  # noticeable gap emerges
        ("large", 2000, 3.0),  # clear divergence
        ("huge", 10000, 3.0),  # O(N²) becomes impractical
        ("massive", 50000, 5.0),  # O(N²) unusable in practice
    ]

    # HEADER
    print("=" * 75)
    print("  JOB SEQUENCING - RANDOM TEST CASE GENERATOR")
    print("=" * 75)
    print()
    print(
        f"  {'Name':<10} {'N':<10} {'Max D':<12} {'O(N²) Est.':<16} {'O(N log N) Est.'}"
    )
    print(f"  {'-' * 10} {'-' * 10} {'-' * 12} {'-' * 16} {'-' * 18}")

    # GENERATE & REPORT
    for name, num_jobs, multiplier in test_configs:
        deadlines, profits = generate_test_case(
            num_jobs, deadline_multiplier=multiplier
        )
        filename = f"tests/test_{name}_n{num_jobs}.txt"
        save_test_case(filename, deadlines, profits)

        max_deadline = max(deadlines)
        est_n2, est_nlogn = estimate_complexity(num_jobs)

        print(
            f"  {name:<10} {num_jobs:<10} {max_deadline:<12} {est_n2:<16} {est_nlogn}"
        )

    # SAMPLE CASES (from problem statement, for correctness verification)
    print()
    print("  Generating sample test cases ...")
    print()

    save_test_case(
        "tests/sample_1.txt", deadlines=[4, 1, 1, 1], profits=[20, 10, 40, 30]
    )
    print("    sample_1.txt  →  deadlines = [4, 1, 1, 1]")
    print("                      profits   = [20, 10, 40, 30]")
    print("                      expected  →  2 jobs, 60 total profit")

    save_test_case(
        "tests/sample_2.txt", deadlines=[2, 1, 2, 1, 1], profits=[100, 19, 27, 25, 15]
    )
    print()
    print("    sample_2.txt  →  deadlines = [2, 1, 2, 1, 1]")
    print("                      profits   = [100, 19, 27, 25, 15]")
    print("                      expected  →  2 jobs, 127 total profit")

    # SUMMARY
    print()
    print("=" * 75)
    print("  OUTPUT FILES (written to tests/)")
    print("=" * 75)
    for name, num_jobs, _ in test_configs:
        print(f"    test_{name}_n{num_jobs}.txt")
    print("    sample_1.txt")
    print("    sample_2.txt")
    print()
    print("  All test cases generated successfully.")
    print("=" * 75)


if __name__ == "__main__":
    main()
