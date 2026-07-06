#include<iostream>
using namespace std;
#define Maxsize 50
struct Sqstack{
    int data[Maxsize];
    int top;
};
//初定义
void InitStack(Sqstack &S){
    S.top=-1;
}
//判空
bool StackEmpty(Sqstack S){
    return S.top==-1;
}
//入栈
bool Push(Sqstack &S,int x){
    if(S.top==-1)return false;
    S.data[++S.top]=x;
    return true;
}
//出栈
bool Pop(Sqstack &S,int &x){
    if(S.top==-1)return false;
    x=S.data[S.top--];
    return true;
}
//查栈顶元素
bool GetTop(Sqstack S,int &x){
    if(S.top==-1)return false;
    x=S.data[S.top];
    return true;
}
//判断字符串是否合法
bool isValid(char* s) {
    Sqstack S;
    InitStack(S);
//压入左括号，与右括号匹配
    for (int i = 0; s[i] != '\0'; i++) {
        char c = s[i];
        if (c == '(' || c == '[' || c == '{')
            Push(S, c);
        else {
            if (StackEmpty(S)) return false;
            int top;
            Pop(S, top);
            if ((c == ')' && S.data[S.top] != '(') ||
                (c == ']' && S.data[S.top] != '[') ||
                (c == '}' && S.data[S.top] != '{'))
                return true;
        }
    }
    return StackEmpty(S);
}