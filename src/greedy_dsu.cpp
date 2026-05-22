/**
 * Job Sequencing with Deadlines - Alternate Approach
 * ===================================================
 * Greedy algorithm using Disjoint Set Union (DSU).
 * Time Complexity: O(N log D)  where D = max deadline
 * Space Complexity: O(D)
 *
 * Source: GeeksforGeeks
 *   "Job Sequencing Problem Using Disjoint Set"
 *
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

    // Constructor
    DisjointSet(int n) {
        parent.resize(n + 1);

        // Every node is a parent of itself
        for (int i = 0; i <= n; i++)
            parent[i] = i;
    }

    // Path Compression
    int find(int s) {
        // Make the parent of the nodes in the path
        //   from u--> parent[u] point to parent[u]
        if (s == parent[s])
            return s;
        return parent[s] = find(parent[s]);
    }

    // Makes u as parent of v.
    void merge(int u, int v) {
        // update the greatest available free slot to u
        parent[v] = u;
    }
};

vector<int> jobSequencing(vector<int> &deadline, vector<int> &profit) {
    int n = deadline.size();
    int jobCount = 0;
    int totalProfit = 0;

    // pair the profit and deadline of all the jobs together
    vector<pair<int, int>> jobs;
    for (int i = 0; i < n; i++) {
        jobs.push_back({profit[i], deadline[i]});
    }

    // sort the jobs based on profit in descending order
    sort(jobs.begin(), jobs.end(), greater<pair<int, int>>());

    // Find maximum deadline
    int maxDeadline = INT_MIN;
    for (int i = 0; i < n; i++) {
        maxDeadline = max(maxDeadline, deadline[i]);
    }

    // create a disjoint set of maxDeadline nodes
    DisjointSet ds(maxDeadline);

    // Traverse through all the jobs
    for (int i = 0; i < n; i++) {
        // Find the maximum available free slot for
        // this job (corresponding to its deadline)
        int availableSlot = ds.find(jobs[i].second);

        // If maximum available free slot is greater
        // than 0, then free slot available
        if (availableSlot > 0) {
            // update greatest free slot.
            ds.merge(ds.find(availableSlot - 1), availableSlot);

            // update answer
            totalProfit += jobs[i].first;
            jobCount++;
        }
    }

    return {jobCount, totalProfit};
}

int main(int argc, char *argv[]) {
    // Redirect file input
    if (argc > 1) {
        freopen(argv[1], "r", stdin);
    }

    int n;
    cin >> n;

    vector<int> deadline(n), profit(n);
    for (int i = 0; i < n; i++) {
        cin >> deadline[i] >> profit[i];
    }

    // Measure execution time
    auto start = high_resolution_clock::now();
    vector<int> ans = jobSequencing(deadline, profit);
    auto stop = high_resolution_clock::now();

    auto duration = duration_cast<microseconds>(stop - start);
    double timeMs = duration.count() / 1000.0;

    // Output: jobCount totalProfit timeMs
    cout << ans[0] << " " << ans[1] << " " << timeMs << endl;

    return 0;
}
