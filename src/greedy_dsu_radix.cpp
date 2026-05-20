/**
 * Job Sequencing with Deadlines - Radix Sort + DSU Optimization
 * =============================================================
 * An ultra-optimized approach that uses a linear-time Radix Sort
 * to sort jobs by profit, followed by Disjoint Set Union (DSU) for slot matching.
 * Time Complexity: O(N * (W/8) + N alpha(D)) where W = 32 bits, D = max deadline.
 *                  This is practically O(N) since W/8 = 4 passes.
 * Space Complexity: O(N + D)
 *
 * This outperforms all standard GeeksforGeeks baselines (O(N^2), O(N log N)).
 * Reads input from file specified as command-line argument.
 * Output format: jobCount totalProfit executionTimeMs
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <climits>

using namespace std;
using namespace std::chrono;

class DisjointSet {
public:
    vector<int> parent;

    DisjointSet(int n) {
        parent.resize(n + 1);
        for (int i = 0; i <= n; i++)
            parent[i] = i;
    }

    int find(int s) {
        if (s == parent[s])
            return s;
        return parent[s] = find(parent[s]);
    }

    void merge(int u, int v) {
        parent[v] = u;
    }
};

// Stable Radix Sort (LSD) in descending order of profit
void radixSortJobsDescending(vector<pair<int, int>>& jobs) {
    int n = jobs.size();
    if (n <= 1) return;

    int maxProfit = 0;
    for (int i = 0; i < n; i++) {
        if (jobs[i].first > maxProfit) {
            maxProfit = jobs[i].first;
        }
    }

    vector<pair<int, int>> temp(n);

    // 4 passes for 32-bit integers (8 bits per pass)
    for (int shift = 0; (maxProfit >> shift) > 0; shift += 8) {
        int count[256] = {0};

        for (int i = 0; i < n; i++) {
            int byteVal = (jobs[i].first >> shift) & 0xFF;
            count[byteVal]++;
        }

        for (int i = 1; i < 256; i++) {
            count[i] += count[i - 1];
        }

        // Build temporary array from right to left to maintain stability
        for (int i = n - 1; i >= 0; i--) {
            int byteVal = (jobs[i].first >> shift) & 0xFF;
            temp[count[byteVal] - 1] = jobs[i];
            count[byteVal]--;
        }

        jobs = temp;
    }

    // Radix sort sorts in ascending order, reverse to get descending order
    reverse(jobs.begin(), jobs.end());
}

vector<int> jobSequencing(vector<int> &deadline, vector<int> &profit) {
    int n = deadline.size();
    int jobCount = 0;
    int totalProfit = 0;

    // pair the profit and deadline of all the jobs together
    vector<pair<int, int>> jobs;
    jobs.reserve(n);
    for (int i = 0; i < n; i++) {
        jobs.push_back({profit[i], deadline[i]});
    }

    // Sort jobs based on profit in descending order using O(N) Radix Sort
    radixSortJobsDescending(jobs);

    // Find maximum deadline
    int maxDeadline = INT_MIN;
    for (int i = 0; i < n; i++) {
        maxDeadline = max(maxDeadline, deadline[i]);
    }

    // create a disjoint set of maxDeadline nodes
    DisjointSet ds(maxDeadline);

    // Traverse through all the jobs
    for (int i = 0; i < n; i++) {
        int availableSlot = ds.find(jobs[i].second);
        if (availableSlot > 0) {
            ds.merge(ds.find(availableSlot - 1), availableSlot);
            totalProfit += jobs[i].first;
            jobCount++;
        }
    }

    return {jobCount, totalProfit};
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        freopen(argv[1], "r", stdin);
    }

    int n;
    if (!(cin >> n)) return 0;

    vector<int> deadline(n), profit(n);
    for (int i = 0; i < n; i++) {
        cin >> deadline[i] >> profit[i];
    }

    auto start = high_resolution_clock::now();
    vector<int> ans = jobSequencing(deadline, profit);
    auto stop = high_resolution_clock::now();

    auto duration = duration_cast<microseconds>(stop - start);
    double timeMs = duration.count() / 1000.0;

    cout << ans[0] << " " << ans[1] << " " << timeMs << endl;

    return 0;
}
