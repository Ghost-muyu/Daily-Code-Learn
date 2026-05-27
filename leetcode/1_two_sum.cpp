#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        int n = nums.size();
        for (int i = 0; i < n; ++i) {
            for (int j = i + 1; j < n; ++j) {
                if (nums[i] + nums[j] == target) {
                    return {i, j};
                }
            }
        }
        return {};
    }
};

// 主函数：本地测试
int main() {
    Solution sol;
    vector<int> nums = {2, 7, 11, 15};
    int target = 9;

    vector<int> ans = sol.twoSum(nums, target);
    
    // 手动打印结果，模拟OJ输出格式
    cout << "[";
    for (int i = 0; i < ans.size(); ++i) {
        if (i > 0) cout << ",";
        cout << ans[i];
    }
    cout << "]" << endl;

    return 0;
}