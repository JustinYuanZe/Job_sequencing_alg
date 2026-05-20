"""
Johnson's Rule — Scientific Visualization (2-Machine Flow Shop)
================================================================
Reads benchmark CSV data and produces publication-quality plots:

  1. Execution Time vs. N (log-log, grouped by distribution type)
  2. Makespan vs. N (showing scheduling quality across distributions)
  3. Theoretical Complexity Overlay — measured vs. O(N log N)
  4. Time per Job (efficiency / overhead analysis)
  5. Multi-panel Dashboard — comprehensive summary figure
  6. Distribution Comparison — bar chart comparing makespans

Usage:
  python benchmarks/plot_johnson_results.py
"""

import csv
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.gridspec import GridSpec

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INPUT_CSV = "results/johnson/benchmark_data.csv"
OUTPUT_DIR = "results/johnson"

# Curated color palette
COLORS = {
    "balanced":  "#2196F3",   # blue
    "m1_heavy":  "#FF5722",   # deep orange
    "m2_heavy":  "#4CAF50",   # green
    "mixed":     "#9C27B0",   # purple
}

MARKERS = {
    "balanced":  "o",
    "m1_heavy":  "s",
    "m2_heavy":  "^",
    "mixed":     "D",
}

LABELS = {
    "balanced":  "Balanced (p1 ~ p2)",
    "m1_heavy":  "M1-Heavy (p1 >> p2)",
    "m2_heavy":  "M2-Heavy (p1 << p2)",
    "mixed":     "Mixed (high variance)",
}

# Shared style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 11,
    "axes.linewidth": 1.2,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "grid.alpha": 0.3,
    "grid.linewidth": 0.8,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(csv_path):
    data = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "N":         int(row["N"]),
                "dist_type": row["dist_type"],
                "makespan":  int(row["makespan"]),
                "median_ms": float(row["median_ms"]),
                "min_ms":    float(row["min_ms"]),
                "max_ms":    float(row["max_ms"]),
            })
    return data


def split_by_type(data):
    groups = {}
    for row in data:
        d = row["dist_type"]
        if d not in groups:
            groups[d] = []
        groups[d].append(row)
    for d in groups:
        groups[d].sort(key=lambda r: r["N"])
    return groups


# ---------------------------------------------------------------------------
# Plot 1: Execution Time vs. N (log-log with error bars)
# ---------------------------------------------------------------------------

def plot_time_vs_n(data, groups):
    fig, ax = plt.subplots(figsize=(11, 7))

    for dtype in ["balanced", "m1_heavy", "m2_heavy", "mixed"]:
        if dtype not in groups:
            continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        t = [r["median_ms"] for r in rows]
        lo = [r["median_ms"] - r["min_ms"] for r in rows]
        hi = [r["max_ms"] - r["median_ms"] for r in rows]

        ax.errorbar(
            N, t,
            yerr=[lo, hi],
            label=LABELS.get(dtype, dtype),
            color=COLORS.get(dtype, "#999"),
            marker=MARKERS.get(dtype, "o"),
            markersize=8,
            linewidth=2.2,
            capsize=4,
            capthick=1.5,
            elinewidth=1.2,
            alpha=0.9,
            zorder=3,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of Jobs (N)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Execution Time (ms)", fontsize=13, fontweight="bold")
    ax.set_title(
        "Johnson's Rule — Execution Time vs. Problem Size",
        fontsize=15, fontweight="bold", pad=14
    )
    ax.legend(fontsize=10, framealpha=0.92, edgecolor="#cccccc", loc="upper left")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{int(x):,}" if x >= 1 else f"{x}"
    ))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "time_vs_n.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Plot 2: Makespan vs. N (scheduling quality)
# ---------------------------------------------------------------------------

def plot_makespan_vs_n(data, groups):
    fig, ax = plt.subplots(figsize=(11, 7))

    for dtype in ["balanced", "m1_heavy", "m2_heavy", "mixed"]:
        if dtype not in groups:
            continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        m = [r["makespan"] for r in rows]

        ax.plot(
            N, m,
            label=LABELS.get(dtype, dtype),
            color=COLORS.get(dtype, "#999"),
            marker=MARKERS.get(dtype, "o"),
            markersize=7,
            linewidth=2.2,
            alpha=0.9,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of Jobs (N)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Makespan (total completion time)", fontsize=13, fontweight="bold")
    ax.set_title(
        "Johnson's Rule — Optimal Makespan by Distribution Type",
        fontsize=15, fontweight="bold", pad=14
    )
    ax.legend(fontsize=10, framealpha=0.92, edgecolor="#cccccc", loc="upper left")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{int(x):,}" if x >= 1 else f"{x}"
    ))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "makespan_vs_n.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Plot 3: Theoretical Complexity Overlay
# ---------------------------------------------------------------------------

def plot_complexity_overlay(data, groups):
    fig, ax = plt.subplots(figsize=(11, 7))

    all_NlogN, all_T = [], []

    for dtype in ["balanced", "m1_heavy", "m2_heavy", "mixed"]:
        if dtype not in groups:
            continue
        rows = groups[dtype]

        for r in rows:
            n = r["N"]
            nlogn = n * math.log2(max(n, 2))
            all_NlogN.append(nlogn)
            all_T.append(r["median_ms"])
            ax.scatter(
                nlogn, r["median_ms"],
                color=COLORS.get(dtype, "#999"),
                marker=MARKERS.get(dtype, "o"),
                s=70, edgecolors="white", linewidths=0.6,
                alpha=0.85, zorder=3,
            )

    # Fit: T ≈ c * N log N
    if all_NlogN and all_T:
        c = np.median([t / x for t, x in zip(all_T, all_NlogN) if x > 0])
        x_range = np.logspace(
            math.log10(min(all_NlogN) * 0.5),
            math.log10(max(all_NlogN) * 2),
            100
        )
        ax.plot(
            x_range, c * x_range,
            "--", color="#666", linewidth=2.2, alpha=0.7,
            label=f"Fitted O(N log N)",
            zorder=2,
        )

    # Add legend entries for distribution types
    for dtype in ["balanced", "m1_heavy", "m2_heavy", "mixed"]:
        if dtype in groups:
            ax.scatter([], [], color=COLORS[dtype], marker=MARKERS[dtype],
                      s=70, label=LABELS[dtype])

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("N × log2(N)  (theoretical operations)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Execution Time (ms)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Johnson's Rule — Empirical vs. Theoretical O(N log N) Complexity",
        fontsize=14, fontweight="bold", pad=14
    )
    ax.legend(fontsize=10, framealpha=0.92, edgecolor="#cccccc")
    ax.grid(True, which="both", linestyle="--", alpha=0.3)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "complexity_overlay.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Plot 4: Time per Job (efficiency analysis)
# ---------------------------------------------------------------------------

def plot_time_per_job(data, groups):
    fig, ax = plt.subplots(figsize=(11, 7))

    for dtype in ["balanced", "m1_heavy", "m2_heavy", "mixed"]:
        if dtype not in groups:
            continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        t = [r["median_ms"] for r in rows]

        # Time per job in microseconds
        tpj = [ti / ni * 1000 for ti, ni in zip(t, N)]  # μs per job

        ax.plot(
            N, tpj,
            label=LABELS.get(dtype, dtype),
            color=COLORS.get(dtype, "#999"),
            marker=MARKERS.get(dtype, "o"),
            markersize=7,
            linewidth=2,
            alpha=0.85,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Number of Jobs (N)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Time per Job (μs)", fontsize=13, fontweight="bold")
    ax.set_title(
        "Johnson's Rule — Per-Job Processing Overhead",
        fontsize=15, fontweight="bold", pad=14
    )
    ax.legend(fontsize=10, framealpha=0.92, edgecolor="#cccccc")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{int(x):,}" if x >= 1 else f"{x}"
    ))

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "time_per_job.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Plot 5: Distribution Comparison Bars (for selected sizes)
# ---------------------------------------------------------------------------

def plot_distribution_bars(data, groups):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Pick representative sizes
    all_N = sorted(set(r["N"] for r in data))
    if len(all_N) > 6:
        # Pick 6 evenly spaced
        indices = np.linspace(0, len(all_N) - 1, 6, dtype=int)
        selected_N = [all_N[i] for i in indices]
    else:
        selected_N = all_N

    dtypes = [d for d in ["balanced", "m1_heavy", "m2_heavy", "mixed"] if d in groups]
    x = np.arange(len(selected_N))
    bar_w = 0.8 / len(dtypes)

    # Left panel: execution time
    for i, dtype in enumerate(dtypes):
        times = []
        for n in selected_N:
            matching = [r for r in groups[dtype] if r["N"] == n]
            times.append(matching[0]["median_ms"] if matching else 0)
        offset = (i - len(dtypes)/2 + 0.5) * bar_w
        ax1.bar(x + offset, times, bar_w,
                label=LABELS.get(dtype, dtype),
                color=COLORS.get(dtype, "#999"),
                alpha=0.85, edgecolor="white", linewidth=0.5)

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{n:,}" for n in selected_N], rotation=40, ha="right", fontsize=9)
    ax1.set_xlabel("Number of Jobs (N)", fontsize=11)
    ax1.set_ylabel("Execution Time (ms)", fontsize=11)
    ax1.set_title("(a) Execution Time by Distribution", fontweight="bold", fontsize=13)
    ax1.legend(fontsize=9, framealpha=0.9)
    ax1.grid(True, axis="y", alpha=0.3, linestyle="--")

    # Right panel: makespan
    for i, dtype in enumerate(dtypes):
        makespans = []
        for n in selected_N:
            matching = [r for r in groups[dtype] if r["N"] == n]
            makespans.append(matching[0]["makespan"] if matching else 0)
        offset = (i - len(dtypes)/2 + 0.5) * bar_w
        ax2.bar(x + offset, makespans, bar_w,
                label=LABELS.get(dtype, dtype),
                color=COLORS.get(dtype, "#999"),
                alpha=0.85, edgecolor="white", linewidth=0.5)

    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{n:,}" for n in selected_N], rotation=40, ha="right", fontsize=9)
    ax2.set_xlabel("Number of Jobs (N)", fontsize=11)
    ax2.set_ylabel("Optimal Makespan", fontsize=11)
    ax2.set_title("(b) Optimal Makespan by Distribution", fontweight="bold", fontsize=13)
    ax2.legend(fontsize=9, framealpha=0.9)
    ax2.grid(True, axis="y", alpha=0.3, linestyle="--")

    fig.suptitle(
        "Johnson's Rule — Distribution Type Impact Analysis",
        fontsize=15, fontweight="bold", y=1.02
    )
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "distribution_comparison.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Plot 6: Multi-panel Dashboard
# ---------------------------------------------------------------------------

def plot_dashboard(data, groups):
    fig = plt.figure(figsize=(20, 14))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    dtypes = ["balanced", "m1_heavy", "m2_heavy", "mixed"]

    # Panel (a): Time vs N (log-log)
    ax1 = fig.add_subplot(gs[0, 0])
    for dtype in dtypes:
        if dtype not in groups: continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        t = [r["median_ms"] for r in rows]
        lo = [r["median_ms"] - r["min_ms"] for r in rows]
        hi = [r["max_ms"] - r["median_ms"] for r in rows]
        ax1.errorbar(N, t, yerr=[lo, hi], label=dtype.replace("_", " ").title(),
                     color=COLORS.get(dtype), marker=MARKERS.get(dtype),
                     markersize=5, linewidth=1.6, capsize=2.5, alpha=0.85)
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel("Jobs (N)", fontsize=10); ax1.set_ylabel("Time (ms)", fontsize=10)
    ax1.set_title("(a) Execution Time vs. N", fontweight="bold", fontsize=11)
    ax1.legend(fontsize=7.5, loc="upper left"); ax1.grid(True, alpha=0.25, which="both", ls="--")

    # Panel (b): Makespan vs N
    ax2 = fig.add_subplot(gs[0, 1])
    for dtype in dtypes:
        if dtype not in groups: continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        m = [r["makespan"] for r in rows]
        ax2.plot(N, m, label=dtype.replace("_", " ").title(),
                 color=COLORS.get(dtype), marker=MARKERS.get(dtype),
                 markersize=5, linewidth=1.6, alpha=0.85)
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("Jobs (N)", fontsize=10); ax2.set_ylabel("Makespan", fontsize=10)
    ax2.set_title("(b) Optimal Makespan", fontweight="bold", fontsize=11)
    ax2.legend(fontsize=7.5, loc="upper left"); ax2.grid(True, alpha=0.25, which="both", ls="--")

    # Panel (c): Complexity overlay
    ax3 = fig.add_subplot(gs[0, 2])
    all_x, all_t = [], []
    for dtype in dtypes:
        if dtype not in groups: continue
        for r in groups[dtype]:
            x = r["N"] * math.log2(max(r["N"], 2))
            all_x.append(x); all_t.append(r["median_ms"])
            ax3.scatter(x, r["median_ms"], color=COLORS.get(dtype),
                       marker=MARKERS.get(dtype), s=35, edgecolors="white",
                       linewidths=0.4, alpha=0.8)
    if all_x:
        c = np.median([t/x for t,x in zip(all_t, all_x) if x > 0])
        xr = np.logspace(math.log10(min(all_x)*0.5), math.log10(max(all_x)*2), 80)
        ax3.plot(xr, c*xr, "--", color="#888", linewidth=1.5, label="O(N log N)")
    ax3.set_xscale("log"); ax3.set_yscale("log")
    ax3.set_xlabel("N × log2(N)", fontsize=10); ax3.set_ylabel("Time (ms)", fontsize=10)
    ax3.set_title("(c) Empirical vs. O(N log N)", fontweight="bold", fontsize=11)
    ax3.legend(fontsize=8); ax3.grid(True, alpha=0.25, which="both", ls="--")

    # Panel (d): Time per job
    ax4 = fig.add_subplot(gs[1, 0])
    for dtype in dtypes:
        if dtype not in groups: continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        tpj = [r["median_ms"] / r["N"] * 1000 for r in rows]
        ax4.plot(N, tpj, label=dtype.replace("_", " ").title(),
                 color=COLORS.get(dtype), marker=MARKERS.get(dtype),
                 markersize=5, linewidth=1.6, alpha=0.85)
    ax4.set_xscale("log")
    ax4.set_xlabel("Jobs (N)", fontsize=10); ax4.set_ylabel("μs / job", fontsize=10)
    ax4.set_title("(d) Per-Job Overhead", fontweight="bold", fontsize=11)
    ax4.legend(fontsize=7.5); ax4.grid(True, alpha=0.25, which="both", ls="--")

    # Panel (e): Makespan / N (average completion per job)
    ax5 = fig.add_subplot(gs[1, 1])
    for dtype in dtypes:
        if dtype not in groups: continue
        rows = groups[dtype]
        N = [r["N"] for r in rows]
        mpj = [r["makespan"] / r["N"] for r in rows]
        ax5.plot(N, mpj, label=dtype.replace("_", " ").title(),
                 color=COLORS.get(dtype), marker=MARKERS.get(dtype),
                 markersize=5, linewidth=1.6, alpha=0.85)
    ax5.set_xscale("log")
    ax5.set_xlabel("Jobs (N)", fontsize=10); ax5.set_ylabel("Makespan / N", fontsize=10)
    ax5.set_title("(e) Average Makespan per Job", fontweight="bold", fontsize=11)
    ax5.legend(fontsize=7.5); ax5.grid(True, alpha=0.25, which="both", ls="--")

    # Panel (f): Stacked performance summary (top 6 sizes)
    ax6 = fig.add_subplot(gs[1, 2])
    all_N = sorted(set(r["N"] for r in data))
    selected = all_N[-6:] if len(all_N) > 6 else all_N
    present_dtypes = [d for d in dtypes if d in groups]
    x_pos = np.arange(len(selected))
    bw = 0.8 / max(len(present_dtypes), 1)
    for i, dtype in enumerate(present_dtypes):
        vals = []
        for n in selected:
            matching = [r for r in groups[dtype] if r["N"] == n]
            vals.append(matching[0]["median_ms"] if matching else 0)
        offset = (i - len(present_dtypes)/2 + 0.5) * bw
        ax6.bar(x_pos + offset, vals, bw,
                label=dtype.replace("_"," ").title(),
                color=COLORS.get(dtype), alpha=0.85,
                edgecolor="white", linewidth=0.4)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels([f"{n:,}" for n in selected], rotation=35, ha="right", fontsize=8)
    ax6.set_xlabel("Jobs (N)", fontsize=10); ax6.set_ylabel("Time (ms)", fontsize=10)
    ax6.set_title("(f) Largest Datasets Performance", fontweight="bold", fontsize=11)
    ax6.legend(fontsize=7.5); ax6.grid(True, axis="y", alpha=0.25, ls="--")

    fig.suptitle(
        "Johnson's Rule (2-Machine Flow Shop) — Comprehensive Performance Analysis",
        fontsize=17, fontweight="bold", y=1.01
    )

    path = os.path.join(OUTPUT_DIR, "johnson_dashboard.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  JOHNSON'S RULE — SCIENTIFIC VISUALIZATION")
    print("=" * 70)
    print()

    if not os.path.exists(INPUT_CSV):
        print(f"  Data file not found: {INPUT_CSV}")
        print("  Run run_johnson_benchmark.py first.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_data(INPUT_CSV)
    groups = split_by_type(data)

    print(f"  Loaded {len(data)} data points across "
          f"{len(groups)} distribution types.")
    print(f"  Types: {', '.join(groups.keys())}")
    print(f"  Size range: {min(r['N'] for r in data):,} — {max(r['N'] for r in data):,}")
    print()

    # Generate all plots
    plot_time_vs_n(data, groups)
    plot_makespan_vs_n(data, groups)
    plot_complexity_overlay(data, groups)
    plot_time_per_job(data, groups)
    plot_distribution_bars(data, groups)
    plot_dashboard(data, groups)

    print()
    print("=" * 70)
    print("  ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"  Output directory: {OUTPUT_DIR}/")
    print()
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".png"):
            fpath = os.path.join(OUTPUT_DIR, f)
            size_kb = os.path.getsize(fpath) / 1024
            print(f"    * {f:<35} ({size_kb:.0f} KB)")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
