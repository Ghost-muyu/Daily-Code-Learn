#include <vector>
#include <iostream>
using namespace std;

// 59. 螺旋矩阵 II
// 模拟 + 循环不变量：一圈一圈填，四条边统一「左闭右开」（每条边填 [start, n-1-start)），
// 圈数 n/2；n 为奇数时中心单独填 n*n。O(n^2)
class Solution {
public:
    vector<vector<int>> generateMatrix(int n) {
        vector<vector<int>> matrix(n, vector<int>(n, 0));
        int count = 1;

        for (int start = 0; start < n / 2; start++) {
            for (int j = start; j < n - 1 - start; j++)   matrix[start][j] = count++;         // 上
            for (int i = start; i < n - 1 - start; i++)   matrix[i][n - 1 - start] = count++; // 右
            for (int j = n - 1 - start; j > start; j--)   matrix[n - 1 - start][j] = count++; // 下
            for (int i = n - 1 - start; i > start; i--)   matrix[i][start] = count++;         // 左
        }

        if (n % 2 == 1) matrix[n / 2][n / 2] = n * n;   // 奇数：中心单独填
        return matrix;
    }
};

int main() {
    Solution s;
    vector<vector<int>> m = s.generateMatrix(4);
    for (auto& row : m) {
        for (int x : row) cout << x << " ";
        cout << endl;
    }
    // 期望：
    // 1 2 3 4
    // 12 13 14 5
    // 11 16 15 6
    // 10 9 8 7
    return 0;
}
