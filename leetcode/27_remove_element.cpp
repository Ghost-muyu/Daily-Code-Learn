#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    int removeElement(vector<int>& nums, int val) {
        int slow = 0;
        for (int fast = 0; fast < nums.size(); ++fast) {
            if (nums[fast] != val) {
                nums[slow] = nums[fast];
                slow++;
            }
        }
        return slow;
    }
};

int main()
{
    Solution sol;
    vector<int> nums = {0,1,2,2,3,0,4,2};
    int val = 2;

    // 执行移除操作
    int newLen = sol.removeElement(nums, val);

    // 输出结果
    cout << "新数组长度：" << newLen << endl;
    cout << "数组前" << newLen << "个元素：";
    for (int i = 0; i < newLen; ++i)
    {
        cout << nums[i] << " ";
    }
    cout << endl;

    return 0;
}