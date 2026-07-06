#include<iostream>
#include<queue>
#include<stack>
using namespace std;

//==================== 图的邻接表存储结构（有向图）====================//

//弧结点：表示一条从顶点v出发的边，终点是agjvex
struct ArcNode{
    int agjvex;      //邻接点（边的终点）下标
    ArcNode* next;   //指向下一条弧结点
};

//顶点结点：保存顶点数据data，以及该顶点的出边链表头first
struct VNode{
    int data;        //顶点数据（本程序直接用编号）
    ArcNode* first;  //出边链表头
};

//邻接表图：vertices数组保存每个顶点的VNode；vexnum顶点数；arcnum边数
struct ALGraph{
    VNode* vertices[100]; //最多100个顶点
    int vexnum,arcnum;
};

//添加有向边 v -> w
void AddArc(ALGraph &G,int v,int w){
    ArcNode* arc=new ArcNode;            //创建一个新的弧结点
    arc->agjvex=w;                       //设置该弧的终点为w
    arc->next=G.vertices[v]->first;     //将新弧的next指向v当前的出边链表头
    G.vertices[v]->first=arc;           //更新v的出边链表头为新弧
}

//全局访问数组（递归版DFS使用）
bool visited[100]={false};


//-------------------- 深度优先遍历（递归） --------------------//
void DFS(ALGraph G,int v){
    visited[v]=true; //先标记v为已访问
    cout<<G.vertices[v]->data<<" "; //输出当前顶点数据

    //沿着v的出边链表逐个访问邻接点
    for(ArcNode* arc=G.vertices[v]->first;arc;arc=arc->next){
        //若终点未访问，则对终点递归DFS
        if(!visited[arc->agjvex])DFS(G,arc->agjvex);
    }
}

//-------------------- 深度优先遍历（非递归，使用栈） --------------------//
void DFS2(ALGraph G,int v){
    bool visited[100]={false}; //局部visited：记录哪些顶点已访问

    stack<int> s;   //栈用于模拟递归过程
    s.push(v);      //起点入栈

    while(!s.empty()){
        int u=s.top(); //取栈顶元素
        s.pop();       //弹出栈顶

        //如果u还未访问，则进行访问并扩展其邻接点
        if(!visited[u]){
            visited[u]=true; //标记u已访问
            cout<<G.vertices[u]->data<<" "; //输出u

            //遍历u的出边链表
            for(ArcNode* arc=G.vertices[u]->first;arc;arc=arc->next){
                //若u的邻接点未访问，则压栈
                if(!visited[arc->agjvex])s.push(arc->agjvex);
            }
        }
    }
}

//-------------------- 广度优先遍历（队列） --------------------//
void BFS(ALGraph G,int v){
    queue<int> q; //队列用于层序遍历

    visited[v]=true; //起点入队前标记已访问
    q.push(v);       //起点入队

    while(!q.empty()){
        int u=q.front(); //取队首
        q.pop();         //弹出队首

        cout<<G.vertices[u]->data<<" "; //访问u（输出）

        //遍历u的所有出边
        for(ArcNode* arc=G.vertices[u]->first;arc;arc=arc->next){
            //若该出边的终点未访问
            if(!visited[arc->agjvex]){
                visited[arc->agjvex]=true; //标记终点已访问（避免重复入队）
                q.push(arc->agjvex);       //终点入队
            }
        }
    }
}

//-------------------- 广度优先遍历（非递归，这里也是用队列实现） --------------------//
void BFS2(ALGraph G,int v){
    bool visited[100]={false}; //局部visited数组

    queue<int> q;    //队列
    visited[v]=true; //起点标记访问
    q.push(v);       //起点入队

    while(!q.empty()){
        int u=q.front(); //取队首元素
        q.pop();         //出队

        cout<<G.vertices[u]->data<<" "; //访问u（输出）

        //遍历u的出边链表
        for(ArcNode* arc=G.vertices[u]->first;arc;arc=arc->next){
            //若邻接点未访问
            if(!visited[arc->agjvex]){
                visited[arc->agjvex]=true; //标记
                q.push(arc->agjvex);       //入队
            }
        }
    }
}

//-------------------- 主函数：创建图并进行遍历 --------------------//
int main(){
    ALGraph G; //定义邻接表图

    //初始化图规模
    G.vexnum=5; //顶点数
    G.arcnum=6; //边数（本程序不在AddArc中使用）

    //为每个顶点分配VNode，并初始化data与first
    for(int i=0;i<G.vexnum;i++){
        G.vertices[i]=new VNode; //申请顶点结点内存
        G.vertices[i]->data=i;  //设置顶点数据
        G.vertices[i]->first=nullptr; //初始化出边链表为空
    }

    //添加有向边：0->1, 0->2, 1->3, 1->4, 2->4, 3->4
    AddArc(G,0,1);
    AddArc(G,0,2);
    AddArc(G,1,3);
    AddArc(G,1,4);
    AddArc(G,2,4);
    AddArc(G,3,4);

    //执行并输出不同遍历
    cout<<"DFS: "; //输出DFS标题
    //注意：递归DFS使用全局visited，若之前调用过需要清零；本题按原代码结构保留
    DFS(G,0); //从顶点0开始深度优先遍历

    cout<<"\nBFS: "; //换行并输出BFS标题
    BFS(G,0); //从顶点0开始广度优先遍历

    cout<<"\nDFS2: "; //换行并输出DFS2标题
    DFS2(G,0); //从顶点0开始非递归深度优先遍历

    cout<<"\nBFS2: "; //换行并输出BFS2标题
    BFS2(G,0); //从顶点0开始广度优先遍历（BFS2）
}


//==================== 图的邻接矩阵存储结构 ====================//

struct MGraph{
    int vertices[100][100]; //邻接矩阵：vertices[i][j]表示i->j是否存在边
    int vexnum,arcnum;       //顶点数/边数
};

//-------------------- 拓扑排序（Kahn算法） --------------------//
bool TopologicalSort(MGraph G){
    int inDegree[100]={0}; //inDegree[i]：顶点i的入度

    //遍历矩阵计算每个顶点入度
    for(int i=0;i<G.vexnum;i++){
        for(int j=0;j<G.vexnum;j++){
            //若存在边 i -> j，则j的入度+1
            if(G.vertices[i][j])inDegree[j]++;
        }
    }

    queue<int> q; //队列：存放入度为0的顶点

    //将所有入度为0的顶点入队
    for(int i=0;i<G.vexnum;i++){
        if(inDegree[i]==0)q.push(i);
    }

    int count=0; //记录输出（删除）的顶点个数

    //反复取出入度为0的顶点，并删除它的出边
    while(!q.empty()){
        int u=q.front(); //取队首顶点u
        q.pop();         //出队

        cout<<u<<" ";    //输出u（拓扑序列）
        count++;          //计数加1

        //遍历u到所有v的边：若存在u->v，则v入度减1
        for(int v=0;v<G.vexnum;v++){
            if(G.vertices[u][v]){
                inDegree[v]--; //删除u->v后，v的入度减1
                //若v入度变为0，则可入队
                if(inDegree[v]==0)q.push(v);
            }
        }
    }

    //若删除的顶点数等于总顶点数，则无环；否则存在环
    return count==G.vexnum;
}

