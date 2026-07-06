#include<iostream>
using namespace std;
#define MaxSize 10
struct SqQueue{
    int data[MaxSize];
    int front,rear;
};
void InitQuene(SqQueue &Q){
    Q.front=Q.rear=0;
}
bool isEmpty(SqQueue Q){
    return Q.front==Q.rear;
}
bool IsFull(SqQueue Q){
    return (Q.rear+1)%MaxSize==Q.front;
}
bool EnQueue(SqQueue &Q,int x){
    if(IsFull(Q))return false;
    Q.data[Q.rear]=x;
    Q.rear=(Q.rear+1)%MaxSize;
    return true;
}
bool DeQueue(SqQueue &Q,int &x){
    if(isEmpty(Q))return false;
    x=Q.data[Q.front];
    Q.front=(Q.front+1)%MaxSize;
    return true;
}
