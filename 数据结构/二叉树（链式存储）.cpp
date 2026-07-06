#include<iostream>
#include<queue>
using namespace std;

//==================== 二叉树（链式存储）基本操作与遍历 ====================//

//二叉树结点结构：保存data和左右孩子指针
struct BiTNode
{
    int data;           //结点数据
    BiTNode* lchild;    //左孩子指针
    BiTNode* rchild;    //右孩子指针
};

//-------------------- 前序遍历（递归：根-左-右） --------------------//
void PreOrder(BiTNode* T){
    if(T){ //如果当前结点存在
        cout<<T->data<<" "; //访问并输出根结点数据
        PreOrder(T->lchild); //递归遍历左子树
        PreOrder(T->rchild); //递归遍历右子树
    }
}

//-------------------- 前序遍历（非递归：使用栈） --------------------//
void PreOrder2(BiTNode* T){
    if(T==nullptr)return; //空树直接结束

    BiTNode* stack[100]; //手写栈（数组实现）
    int top=-1;           //栈顶下标初始化为-1（表示空栈）

    stack[++top]=T; //将根结点入栈（先++再赋值）

    while(top!=-1){ //当栈非空时循环
        BiTNode* node=stack[top--]; //取栈顶结点并弹栈（top--表示先用再减）

        cout<<node->data<<" "; //输出当前结点（对应前序的“根”）

        //由于栈是后进先出：要保证先处理左子树，就先压入右孩子，再压入左孩子
        if(node->rchild)stack[++top]=node->rchild; //右孩子不为空则入栈
        if(node->lchild)stack[++top]=node->lchild; //左孩子不为空则入栈
    }
}

//-------------------- 中序遍历（递归：左-根-右） --------------------//
void InOrder(BiTNode* T){
    if(T){ //当前结点存在
        InOrder(T->lchild);        //先递归遍历左子树
        cout<<T->data<<" ";      //访问并输出根结点
        InOrder(T->rchild);        //再递归遍历右子树
    }
}

//-------------------- 中序遍历（非递归：使用栈） --------------------//
void InOrder2(BiTNode* T){
    BiTNode* stack[100]; //手写栈
    int top=-1;          //栈顶下标

    BiTNode* p=T; //p作为当前遍历指针

    //只要p不为空或栈不为空，就继续
    while(p||top!=-1){
        while(p)stack[++top]=p; //不断向左走：把路径上的结点压栈
        p=p?nullptr:p; //占位：保持代码结构（不会执行到这里的任何输出逻辑）

        //当p为空时，从栈顶取结点访问
        if(top!=-1){
            p=stack[top--]; //弹出栈顶并赋给p
            cout<<p->data<<" "; //访问当前结点（中序的“根”）

            //然后转向其右子树
            p=p->rchild;
        }
    }
}

//-------------------- 后序遍历（递归：左-右-根） --------------------//
void PostOrder(BiTNode* T){
    if(T){
        PostOrder(T->lchild); //先遍历左子树
        PostOrder(T->rchild); //再遍历右子树
        cout<<T->data<<" ";  //最后访问根结点
    }
}

//-------------------- 后序遍历（非递归：栈 + last指针） --------------------//
void PostOrder2(BiTNode* T){
    if(T==nullptr)return; //空树直接结束

    BiTNode* stack[100]; //手写栈
    int top=-1;           //栈顶下标
    BiTNode* last=nullptr; //last用于记录“刚刚访问过”的结点

    stack[++top]=T; //根结点入栈

    while(top!=-1){ //当栈非空时循环
        BiTNode* node=stack[top]; //先查看栈顶结点（不弹栈）

        //若node是叶子结点：直接访问它
        //或node的孩子中“刚访问过的是它的某个孩子”：说明左右子树都已处理完
        if((node->lchild==nullptr&&node->rchild==nullptr)||
           (last!=nullptr&&(last==node->lchild||last==node->rchild))){
            cout<<node->data<<" "; //访问结点（对应后序的“根”）
            last=node;              //更新last为已访问结点
            top--;                  //弹出该结点
        }
        else{
            //否则：需要先处理它的孩子
            if(node->rchild)stack[++top]=node->rchild; //先压右孩子（栈后进先出）
            if(node->lchild)stack[++top]=node->lchild; //再压左孩子
        }
    }
}

//-------------------- 层序遍历（BFS：队列） --------------------//
void LevelOrder(BiTNode* T){
    queue<BiTNode*> q; //队列保存待访问结点

    if(T)q.push(T); //如果根存在就入队

    while(!q.empty()){//队列非空则继续
        BiTNode* p=q.front(); //取队首
        q.pop();              //出队

        cout<<p->data<<" "; //输出当前结点数据

        if(p->lchild)q.push(p->lchild); //左孩子存在则入队
        if(p->rchild)q.push(p->rchild); //右孩子存在则入队
    }
}

//-------------------- 求二叉树高度（递归） --------------------//
int TreeHeight(BiTNode* T){
    if(!T)return 0; //空树高度为0

    int left=TreeHeight(T->lchild);   //递归求左子树高度
    int right=TreeHeight(T->rchild); //递归求右子树高度

    return (left>right?left:right)+1; //高度取两者较大再+1（当前根）
}

//-------------------- 求二叉树结点个数（递归） --------------------//
int TreeNodeCount(BiTNode* T){
    if(!T)return 0; //空树结点数为0

    return TreeNodeCount(T->lchild)+TreeNodeCount(T->rchild)+1; //左 + 右 + 根
}

//-------------------- 求二叉树高度（非递归：层序遍历） --------------------//
int TreeHeight2(BiTNode* T){
    if(!T)return 0; //空树高度为0

    queue<BiTNode*> q; //队列
    q.push(T);         //根结点入队

    int height=0; //高度计数

    while(!q.empty()){//只要队列中还有结点
        int size=q.size(); //本层结点数（用于分层）

        //遍历本层的所有结点
        for(int i=0;i<size;i++){
            BiTNode* p=q.front(); //取队首
            q.pop();             //出队

            //把下一层结点加入队列
            if(p->lchild)q.push(p->lchild);
            if(p->rchild)q.push(p->rchild);
        }

        height++; //完成一层处理后高度+1
    }

    return height; //返回层数即树高度
}

//-------------------- 二叉搜索树插入（递归） --------------------//
//T为根指针引用（&），k为要插入的值
bool BST_Insert(BiTNode* &T,int k){
    if(!T){
        //若当前子树为空，则创建新结点作为插入位置
        T=new BiTNode; //分配结点内存
        T->data=k;    //写入数据
        T->lchild=T->rchild=nullptr; //左右孩子置空
        return true;  //插入成功
    }

    if(k==T->data)return false; //若值已存在则不插入
    else if(k<T->data)
        return BST_Insert(T->lchild,k); //k小于当前值，去左子树插入
    else
        return BST_Insert(T->rchild,k); //k大于当前值，去右子树插入
}

int main(){
    return 0;
}




