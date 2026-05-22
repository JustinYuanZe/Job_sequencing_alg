# Job Sequencing with Deadlines & Flow Shop Optimization

**Course:** IN208 Introduction to Algorithms (114-2)  
**Group 12:** Justin (Math & Analysis), Musa (Implementation), Ha (Statement, Application, Conclusion)  
**Instructor:** Dr. Muhammad Asad Saleem  
**University:** Yuan Ze University

---

## 📌 Project Overview
This repository contains the complete implementation, benchmarking, and mathematical analysis of **Job Sequencing with Deadlines** (Single-Machine Scheduling) and its industrial extensions, including **Johnson's Rule** (2-Machine Flow Shop Scheduling) and the integration of **Explainable AI (xAI)** for industrial applications.

We implement three standard baselines (Naive, Min-Heap, DSU) and propose an ultra-optimized algorithm (**Radix Sort + DSU**) that reduces sorting overhead to achieve practically linear $O(N \alpha(D))$ time complexity.

---

## 🧠 Algorithms Implemented

### 1. Single-Machine Job Sequencing (Max Profit)
| Algorithm | Key Technique | Time Complexity | Space Complexity | File |
| :--- | :--- | :--- | :--- | :--- |
| **Naive Greedy** | Sorting + linear search backward for free slot | $O(N^2)$ | $O(N)$ | [`src/greedy_baseline.cpp`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/src/greedy_baseline.cpp) |
| **Min-Heap (Expected)** | Sorting by deadline + Min-Heap tracking | $O(N \log N)$ | $O(N)$ | [`src/greedy_heap.cpp`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/src/greedy_heap.cpp) |
| **Disjoint Set (DSU)** | Sorting by profit + DSU for available slot finding | $O(N \log N + N \alpha(D))$ | $O(D)$ | [`src/greedy_dsu.cpp`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/src/greedy_dsu.cpp) |
| **Optimized Radix-DSU** | **Radix Sort** (base 256) + DSU slot finding (Proposed) | **$O(N \alpha(D))$** (Linear) | $O(N + D)$ | [`src/greedy_dsu_radix.cpp`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/src/greedy_dsu_radix.cpp) |

### 2. Two-Machine Flow Shop Scheduling (Makespan Minimization)
- **Johnson's Algorithm:** Implements Johnson's Rule ($O(N \log N)$) to find the optimal order minimizing the total makespan on two serial machines.
- **Location:** [`src/johnson.cpp`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/src/johnson.cpp)

---

## 📊 Experimental Results & Benchmarks

Our benchmarks run on 6 datasets of exponentially growing sizes ($N=10$ to $N=50,000$).

### Execution Time Table (ms)
| Jobs ($N$) | Naive $O(N^2)$ | Min-Heap $O(N \log N)$ | DSU $O(N \log D)$ | **Proposed Radix-DSU $O(N)$** |
| :--- | :--- | :--- | :--- | :--- |
| **10** | 0.0020 ms | 0.0030 ms | 0.0020 ms | **0.0030 ms** |
| **100** | 0.0140 ms | 0.0110 ms | 0.0130 ms | **0.0040 ms** |
| **500** | 0.0530 ms | 0.0630 ms | 0.0390 ms | **0.0220 ms** |
| **2,000** | 0.5710 ms | 0.2830 ms | 0.1980 ms | **0.0660 ms** |
| **10,000** | 13.8600 ms | 1.7930 ms | 1.1100 ms | **0.4380 ms** |
| **50,000** | *Skipped (>10s)* | 8.7770 ms | 5.7520 ms | **2.3410 ms** |

*Note: At $N=50,000$, our proposed Radix-DSU solver is **2.5x faster than DSU** and **4x faster than Min-Heap** due to the $O(N)$ linear-time sorting.*

The generated comparative performance curve is saved at [`results/job_sequencing_comparison.png`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/results/job_sequencing_comparison.png).

---

## 🚀 How to Run Benchmarks

### 1. Job Sequencing (Single Machine)
To generate the datasets, run the benchmarks, and output the comparison plot, execute:
```bash
python benchmarks/generate_testcases.py
python benchmarks/run_benchmark.py
```
*(The benchmark automatically handles C++ compilation via native `g++` or `wsl g++` if running on Windows).*

### 2. Johnson's Algorithm (2-Machine Flow Shop)
To generate the 2-machine datasets, run the makespan benchmarks, and produce the 6 diagnostic visualization graphs, execute:
```bash
python benchmarks/generate_johnson_datasets.py
python benchmarks/run_johnson_benchmark.py
```
Outputs will be written to `results/johnson/`.

---

## 📄 Academic Slides & Report
We have completed academic-grade LaTeX source files ready to compile:
- **Presentation Slides:** [`slides/presentation.tex`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/slides/presentation.tex) (contains matroid foundations, algorithms, benchmark plots, Johnson's Rule, and xAI industrial explanations).
- **Written Report:** [`report/report.tex`](file:///c:/Users/MSI/Desktop/1142/IN208_Algorithms/Job_sequencing_alg/report/report.tex) (comprehensive academic report including abstract, matroid mathematical proofs, detailed algorithms, empirical benchmark tables, and future-work integration details).

---

## 💡 Key Contributions & Real-World Extensions
1. **Mathematical Matroid Proof:** Proved that Job Sequencing forms a matroid, guaranteeing greedy optimality.
2. **Linear-Time Algorithm:** Designed and evaluated a custom Radix Sort + DSU implementation that operates in $O(N \alpha(D))$ time, breaking the comparison-based sorting bottleneck.
3. **Johnson's Flow Shop Extension:** Described the transition to two-machine scheduling and the NP-hardness of the problem under machine unavailability.
4. **xAI (Explainable AI) Integration:** Detailed how feature attribution (SHAP/LIME) and counterfactual explanations make automated schedule prioritizations transparent and trustworthy for floor operators.
