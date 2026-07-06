#include<iostream>
using namespace std;

//==================== 快速排序（QuickSort）====================//

//Partition：对区间[low, high]进行划分
//使用基准pivot = A[low]，将比pivot小的放左边，比pivot大的放右边
int Partition(int A[],int low,int high){
    int pivot=A[low]; //选择第一个元素作为基准（pivot）

    while(low<high){ //只要左右指针未交错，就继续找
        //从右往左找第一个“小于pivot”的元素
        while(low<high && A[high]>=pivot) high--; //high向左移动：跳过所有>=pivot的元素
        A[low]=A[high]; //把找到的“小于pivot”的元素放到low位置（形成左侧更小区域）

        //从左往右找第一个“大于pivot”的元素
        while(low<high && A[low]<=pivot) low++; //low向右移动：跳过所有<=pivot的元素
        A[high]=A[low]; //把找到的“大于pivot”的元素放到high位置（形成右侧更大区域）
    }

    //当low==high时，左右都指向同一位置，该位置就是pivot最终落点
    A[low]=pivot;      //把pivot写回最终位置
    return low;        //返回pivot最终下标，便于递归继续处理左右两段
}

//QuickSort：递归快速排序
void QuickSort(int A[],int low, int high){
    if(low<high){ //区间至少包含两个元素时才需要继续划分
        int pivotpos=Partition(A,low,high); //对当前区间完成一次划分，得到pivot最终位置
        QuickSort(A,low,pivotpos-1);         //对pivot左侧（<=pivot）继续快速排序
        QuickSort(A,pivotpos+1,high);        //对pivot右侧（>=pivot）继续快速排序
    }
}

//==================== 归并排序（MergeSort）====================//

//Merge：合并两个有序段 A[low..mid] 和 A[mid+1..high]
void Merge(int A[],int low,int mid,int high){
    int i=low, j=mid+1, k=0; //i遍历左段，j遍历右段；k是temp数组写入下标
    int* temp=new int[high-low+1]; //临时数组temp大小=当前区间长度

    //逐个比较左右段当前元素，把更小的元素先放入temp
    while(i<=mid && j<=high){
        //如果左段元素小于等于右段元素，先放左段
        if(A[i]<=A[j]) temp[k++]=A[i++]; //把A[i]写入temp[k]后，k++且i++
        else            temp[k++]=A[j++]; //否则写入右段A[j]后，同样k++且j++
    }

    //若右段已经耗尽，则左段剩余元素直接拷贝到temp
    while(i<=mid) temp[k++]=A[i++]; //持续把左段剩余元素写入temp

    //若左段已经耗尽，则右段剩余元素直接拷贝到temp
    while(j<=high) temp[k++]=A[j++]; //持续把右段剩余元素写入temp

    //把temp中合并好的结果拷回原数组A的[low..high]区间
    for(int i=0;i<k;i++) A[low+i]=temp[i];

    //释放临时数组，避免内存泄漏
    delete[] temp;
}

//MergeSort：递归归并排序
void MergeSort(int A[],int low,int high){
    if(low<high){ //区间长度>1才继续分裂
        int mid=(low+high)/2; //计算中点：把区间分成[low..mid]和[mid+1..high]
        MergeSort(A,low,mid);      //递归排序左半段
        MergeSort(A,mid+1,high); //递归排序右半段
        Merge(A,low,mid,high);    //把两个已排好序的半段合并
    }
}

//==================== 测试主函数 ====================//
int main(){
    //待排序数组
    int A[]={38,27,43,3,9,82,10};
    int n=sizeof(A)/sizeof(A[0]); //计算数组元素个数n

    //快速排序
    QuickSort(A,0,n-1); //对整个区间[0..n-1]进行快排

    //输出快速排序结果
    for(int i=0;i<n;i++) cout<<A[i]<<" "; //逐个输出排好序的元素
    cout<<endl; //输出换行

    //归并排序（使用另一个数组B，保证初始数据与A相同）
    int B[]={38,27,43,3,9,82,10};
    MergeSort(B,0,n-1); //对B进行归并排序

    //输出归并排序结果
    for(int i=0;i<n;i++) cout<<B[i]<<" "; //逐个输出排好序的元素
    cout<<endl; //输出换行
}


