#include <vector>
#include <iostream>
using namespace std;

// 977. 有序数组的平方
// 双指针：平方后数组呈「中间小、两端大」，从结果末尾往前填，每次取两端平方较大者，O(n)
class Solution {
public:
    vector<int> sortedSquares(vector<int>& nums) {
        int n = nums.size();
        vector<int> result(n);
        int left = 0, right = n - 1, pos = n - 1;

        while (left <= right) {
            int sqL = nums[left] * nums[left];
            int sqR = nums[right] * nums[right];
            if (sqL > sqR) {
                result[pos] = sqL;
                left++;
            } else {
                result[pos] = sqR;
                right--;
            }
            pos--;
        }
        return result;
    }
};

int main() {
    Solution s;
    vector<int> nums = {-4, -1, 0, 3, 10};
    vector<int> ans = s.sortedSquares(nums);
    for (int x : ans) cout << x << " ";   // 期望 0 1 9 16 100
    cout << endl;
    return 0;
}
