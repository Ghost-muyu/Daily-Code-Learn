#include <iostream>
using namespace std;
struct ListNode{
    int val;
    ListNode* next;
    ListNode(int x):val(x),next(NULL){}
};
ListNode* createList(){
    ListNode* head=NULL;
    ListNode* tail=NULL;
    int num;
    while(cin>>num){
        ListNode* node=new ListNode(num);
        if(head==NULL){
            head=node;
            tail=node;
        }else{
            tail->next=node;
            tail=node;
        }
    }
    return head;
}
void printList(ListNode* head){
    ListNode* p=head;
    while(p!=NULL){
        cout<<p->val<<"  ";
        p=p->next;
    }
    cout<<endl;
}
int main(){
    ListNode* head=createList();
    printList(head);
    return 0;
}

