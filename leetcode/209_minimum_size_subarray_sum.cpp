#include <vector>
#include <iostream>
#include <climits>
using namespace std;

// 209. 长度最小的子数组
// 滑动窗口：right 扩张到 sum >= target，再 left 收缩求最短，O(n)
class Solution {
public:
    int minSubArrayLen(int target, vector<int>& nums) {
        int n = nums.size();
        int left = 0, sum = 0;
        int ans = INT_MAX;

        for (int right = 0; right < n; right++) {
            sum += nums[right];            // 窗口扩张
            while (sum >= target) {        // 窗口收缩
                ans = min(ans, right - left + 1);
                sum -= nums[left];
                left++;
            }
        }
        return ans == INT_MAX ? 0 : ans;   // 没找到返回 0
    }
};

int main() {
    Solution s;
    vector<int> nums = {2, 3, 1, 2, 4, 3};
    cout << s.minSubArrayLen(7, nums) << endl;   // 期望 2
    return 0;
}
