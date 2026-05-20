/**
 * Job Sequencing with Deadlines - Expected Approach
 * ==================================================
 * Greedy algorithm using Min-Heap (Priority Queue).
 * Time Complexity: O(N log N)
 * Space Complexity: O(N)
 *
 * Source: GeeksforGeeks
 *   "Job Sequencing Problem - Expected Approach Using Sorting and MinHeap"
 *
 * Reads input from file specified as command-line argument.
 * Output format: jobCount totalProfit executionTimeMs
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <chrono>

using namespace std;
using namespace std::chrono;

vector<int> jobSequencing(vector<int> &deadline, vector<int> &profit) {
    int n = deadline.size();
    int jobCount = 0;
    int totalProfit = 0;

    vector<pair<int, int>> jobs;
    for (int i = 0; i < n; i++) {
        jobs.push_back({deadline[i], profit[i]});
    }

    // sort the jobs based on deadline in ascending order
    sort(jobs.begin(), jobs.end());

    priority_queue<int, vector<int>, greater<int>> pq;

    for (int i = 0; i < jobs.size(); i++) {
        // if job can be scheduled within its deadline
        if (jobs[i].first > pq.size())
            pq.push(jobs[i].second);

        // replace the job with the lowest profit
        else if (!pq.empty() && pq.top() < jobs[i].second) {
            pq.pop();
            pq.push(jobs[i].second);
        }
    }

    while (!pq.empty()) {
        totalProfit += pq.top();
        pq.pop();
        jobCount++;
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
