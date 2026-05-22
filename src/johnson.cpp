/**
 * Johnson's Rule — 2-Machine Flow Shop Scheduling
 * ==================================================
 * Finds the optimal job sequence to minimize makespan (total completion time)
 * when every job must be processed first on Machine 1, then on Machine 2.
 *
 * Algorithm (Johnson's Rule, 1954):
 *   1. Partition jobs into two sets:
 *        Set A: jobs where p1[i] <= p2[i]  (Machine 1 time <= Machine 2 time)
 *        Set B: jobs where p1[i] >  p2[i]  (Machine 1 time >  Machine 2 time)
 *   2. Sort Set A by p1[i] in ascending order  (shortest M1 first)
 *   3. Sort Set B by p2[i] in descending order (longest M2 first)
 *   4. Optimal sequence = Set A ++ Set B
 *   5. Compute makespan by simulating the schedule.
 *
 * Time Complexity : O(N log N)  [dominated by sorting]
 * Space Complexity: O(N)
 *
 * Input format (from file, first argument):
 *   Line 1      : N (number of jobs)
 *   Lines 2..N+1: p1_i  p2_i   (processing times on Machine 1 and 2)
 *
 * Output format:
 *   makespan  N  executionTimeMs
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <chrono>

using namespace std;
using namespace std::chrono;

struct Job {
    int id;   // original 1-based job index
    int p1;   // processing time on Machine 1
    int p2;   // processing time on Machine 2
};

// ---------------------------------------------------------------------------
// Johnson's Rule
// ---------------------------------------------------------------------------
// Returns: (optimal sequence of job indices, makespan)
pair<vector<int>, long long> johnsonRule(const vector<Job>& jobs) {
    int n = (int)jobs.size();

    // Step 1: Partition into Set A and Set B
    vector<Job> setA, setB;
    for (const auto& j : jobs) {
        if (j.p1 <= j.p2) {
            setA.push_back(j);
        } else {
            setB.push_back(j);
        }
    }

    // Step 2: Sort Set A by p1 ascending (shortest Machine 1 time first)
    sort(setA.begin(), setA.end(), [](const Job& a, const Job& b) {
        return a.p1 < b.p1;
    });

    // Step 3: Sort Set B by p2 descending (longest Machine 2 time first)
    sort(setB.begin(), setB.end(), [](const Job& a, const Job& b) {
        return a.p2 > b.p2;
    });

    // Step 4: Concatenate: Set A followed by Set B
    vector<int> sequence;
    sequence.reserve(n);
    for (const auto& j : setA) sequence.push_back(j.id);
    for (const auto& j : setB) sequence.push_back(j.id);

    // Step 5: Compute makespan by simulating the schedule
    long long m1_end = 0;  // completion time on Machine 1
    long long m2_end = 0;  // completion time on Machine 2

    // Build a lookup by id for fast access
    vector<Job> ordered;
    ordered.reserve(n);
    for (const auto& j : setA) ordered.push_back(j);
    for (const auto& j : setB) ordered.push_back(j);

    for (const auto& j : ordered) {
        m1_end += j.p1;
        // Machine 2 can start only after Machine 1 finishes this job
        // AND after Machine 2 finishes its previous job
        m2_end = max(m1_end, m2_end) + j.p2;
    }

    return {sequence, m2_end};
}

// ---------------------------------------------------------------------------
// Brute-Force (for small N, used for correctness verification)
// ---------------------------------------------------------------------------
long long computeMakespan(const vector<Job>& jobs, const vector<int>& perm) {
    long long m1_end = 0, m2_end = 0;
    for (int idx : perm) {
        const Job& j = jobs[idx];
        m1_end += j.p1;
        m2_end = max(m1_end, m2_end) + j.p2;
    }
    return m2_end;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <input_file> [--verify] [--print-seq]" << endl;
        return 1;
    }

    bool verify = false;
    bool printSeq = false;
    for (int i = 2; i < argc; i++) {
        if (string(argv[i]) == "--verify") verify = true;
        if (string(argv[i]) == "--print-seq") printSeq = true;
    }

    // Read input
    ifstream fin(argv[1]);
    if (!fin.is_open()) {
        cerr << "Cannot open file: " << argv[1] << endl;
        return 1;
    }

    int n;
    fin >> n;

    vector<Job> jobs(n);
    for (int i = 0; i < n; i++) {
        jobs[i].id = i;
        fin >> jobs[i].p1 >> jobs[i].p2;
    }
    fin.close();

    // Run Johnson's Rule with timing
    auto start = high_resolution_clock::now();
    auto [sequence, makespan] = johnsonRule(jobs);
    auto stop = high_resolution_clock::now();

    auto duration = duration_cast<microseconds>(stop - start);
    double timeMs = duration.count() / 1000.0;

    // Output: makespan N timeMs
    cout << makespan << " " << n << " " << timeMs << endl;

    // Optional: print optimal sequence
    if (printSeq && n <= 200) {
        cerr << "Optimal sequence: ";
        for (int i = 0; i < n; i++) {
            if (i > 0) cerr << " -> ";
            cerr << "J" << (sequence[i] + 1);
        }
        cerr << endl;
        cerr << "Makespan: " << makespan << endl;
    }

    // Optional: verify against brute-force (only for small N)
    if (verify && n <= 10) {
        vector<int> perm(n);
        for (int i = 0; i < n; i++) perm[i] = i;
        long long bestBF = computeMakespan(jobs, perm);
        while (next_permutation(perm.begin(), perm.end())) {
            bestBF = min(bestBF, computeMakespan(jobs, perm));
        }
        if (bestBF == makespan) {
            cerr << "[VERIFY OK] Johnson = BruteForce = " << makespan << endl;
        } else {
            cerr << "[VERIFY FAIL] Johnson=" << makespan
                 << " BruteForce=" << bestBF << endl;
        }
    }

    return 0;
}
