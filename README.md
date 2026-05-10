# Job Sequencing with Deadlines — Optimization & Benchmarking

**Course:** IN208 Algorithms  
**Group 12:** Justin (Math & Analysis), Musa (Implementation), Ha(Statement, Application, Conclusion)  
**Instructor:** Dr. Muhammad Asad Saleem

---

## 📌 Problem Statement

Given a set of `N` jobs, each with a deadline and a profit (earned only if completed by the deadline), determine the optimal sequence that maximizes total profit using a single machine (one job per time slot).

---

## 🧠 Algorithms Implemented

| Version | Approach | Time Complexity | File |
|---------|----------|-----------------|------|
| **Baseline** | Greedy + Linear Scan for available slot | O(N²) | `src/greedy_baseline.cpp` |
| **Advanced** | Greedy + Disjoint Set Union (DSU) for slot finding | O(N log N) | `src/greedy_dsu.cpp` |
