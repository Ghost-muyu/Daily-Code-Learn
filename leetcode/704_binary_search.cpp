#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    int search(vector<int>& nums, int target) {
        // 搜索区间是闭区间 [left, right]
        int left = 0, right = nums.size() - 1;
        while (left <= right) {
            // 防溢出写法，等价于 (left + right) / 2
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;   // target 在右半边
            } else {
                right = mid - 1;  // target 在左半边
            }
        }
        return -1;  // 没找到
    }
};

// 本地测试
int main() {
    Solution s;
    vector<int> nums = {-1, 0, 3, 5, 9, 12};

    cout << "target=9  -> " << s.search(nums, 9)  << "  (期望 4)" << endl;
    cout << "target=2  -> " << s.search(nums, 2)  << "  (期望 -1)" << endl;
    cout << "target=-1 -> " << s.search(nums, -1) << "  (期望 0)" << endl;
    cout << "target=12 -> " << s.search(nums, 12) << "  (期望 5)" << endl;
    return 0;
}
