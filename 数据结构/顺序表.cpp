#define InitSize 10
#include <iostream>
struct SeqList{
    int* data;
    int length;
    int maxSize;
};
//初始化
void InitList(SeqList &L){
    L.data=new int[InitSize];
    L.length=0;
    L.maxSize=InitSize;
}
//扩容
void IncreaseSize(SeqList &L,int len){
    int* p=L.data;
    L.data=new int[L.maxSize+len];
    for(int i=0;i<L.length+1;i++){
        L.data[i]=p[i];
        L.maxSize+=len;
        delete[] p;
    }
}
//插入
bool ListInsert(SeqList &L,int i,int e){
    if(i<1||i>L.length+1)return false;
    if(L.length>=L.maxSize)IncreaseSize(L,5);
    for(int j=L.length;j>=i;j--)
    L.data[j]=L.data[j-1];
    L.data[i-1]=e;
    L.length++;
    return true;
}
//删除
bool ListDelete(SeqList &L,int i,int &e){
    if(i<1||i>L.length+1)return false;
    e=L.data[i-1];//记录删除元素
    for(int j=i;j<L.length;j++)
    L.data[j-1]=L.data[j];
    L.length--;
    return true;
}
//按值查找
int LocateElem(SeqList L,int e){
    for (int i = 0; i < L.length; i++)
    if(L.data[i]==e)return i+1;
    return 0;
}