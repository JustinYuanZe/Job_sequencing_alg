/**
 * Job Sequencing with Deadlines - Naive Approach
 * ===============================================
 * Greedy algorithm with linear scan for available slot.
 * Time Complexity: O(N^2)
 * Space Complexity: O(N)
 *
 * Source: GeeksforGeeks
 *   "Job Sequencing Problem - Naive Approach Using Sorting"
 *
 * Reads input from file specified as command-line argument.
 * Output format: jobCount totalProfit executionTimeMs
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>

using namespace std;
using namespace std::chrono;

vector<int> jobSequencing(vector<int> &deadline, vector<int> &profit) {
    int n = deadline.size();
    int cnt = 0;
    int totProfit = 0;

    // pair the profit and deadline of all the jobs together
    vector<pair<int, int>> jobs;
    for (int i = 0; i < n; i++) {
        jobs.push_back({profit[i], deadline[i]});
    }

    // sort the jobs based on profit in decreasing order
    sort(jobs.begin(), jobs.end(), greater<pair<int, int>>());

    vector<int> slot(n, 0);
    for (int i = 0; i < n; i++) {
        int start = min(n, jobs[i].second) - 1;
        for (int j = start; j >= 0; j--) {
            // if slot is empty
            if (slot[j] == 0) {
                slot[j] = 1;
                cnt++;
                totProfit += jobs[i].first;
                break;
            }
        }
    }

    return {cnt, totProfit};
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
