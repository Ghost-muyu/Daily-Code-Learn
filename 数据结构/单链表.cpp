#include<iostream>
using namespace std;
struct Node{
    int data;
    Node* next;
};
//初始化
void InitList(Node* &L){
    L=new Node;
    L->next=nullptr;
}
//头插法
void HeadInsert(Node* &L){
    InitList(L);
    int x;
    cin>>x;
    while(cin>>x&&x!=9999){
        Node* s=new Node;
        s->data=x;
        s->next=L->next;
        L->next=s;

    }
}
//尾插法
void TailInsert(Node* &L){
    L=new Node;
    L->next=nullptr;
    Node* tail=L;
    Node* s=new Node;
    int x;
    while(cin>>x){
    s->data=x;
    tail->next=s;
    tail=s;
    tail->next=nullptr;
}
}
//按序号查找
Node* GetElem(Node* L,int i){
    if(i<0) return nullptr;
    Node* p=L;
    int j=0;
    while(p&&j<i){
        p=p->next;
        j++;
    }
    return p;
}
//按值查找
Node* LocateElem(Node* L,int e){
    Node* p=L;
    while(p&&p->data!=e)p=p->next;
    return p;

}
//在第i个位置插入e
void ListInsert(Node* &L,int e){
    Node* p=L;
    int i,j=0;cin>>i;
    while(p&&j<i-1){
        p=p->next;
        j++;
    }
    Node* s=new Node;
    s->data=e;
    s->next=p->next;
    p->next=s;
}
//删除第i个节点，用e返回值
void ListDelete(Node* &L,int i,int &e){
    cin>>i;
    Node* p=GetElem(L,i-1);
    Node* s=p->next;
    e=s->data;
    p->next=s->next;
    delete s;
}
//反转链表
void Reverse(Node* &L){
    Node* pre=nullptr;
    Node* cur=L->next;
    Node* next;
    while(cur){
        next=cur->next;
        cur->next=pre;
        pre=cur;
        cur=next;
    }
    L->next=pre;
}
