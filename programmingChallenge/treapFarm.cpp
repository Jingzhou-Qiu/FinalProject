#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <algorithm>
#include <utility>
#include <random>

using namespace std;

/* ----------------- Per‑crop Treap (COUNT) ----------------- */
static std::mt19937 rng(42); // random number generator

// Treap node for per‑crop tree
struct PNode {         
    int key, prio;
    PNode *l, *r;
    int sz;
    PNode(int k): key(k), prio((int)rng()), l(nullptr), r(nullptr), sz(1){}
};
int psz(PNode* t){ return t? t->sz : 0; }
void ppull(PNode* t){ if(t) t->sz = 1 + psz(t->l) + psz(t->r); }

/* split by key:  keys ≤ key  |  keys > key */
pair<PNode*,PNode*> psplit(PNode* t,int key){
    if(!t) return {nullptr,nullptr};
    if(key < t->key){ auto sp=psplit(t->l,key); t->l=sp.second; ppull(t); return {sp.first,t}; }
    auto sp=psplit(t->r,key); t->r=sp.first; ppull(t); return {t,sp.second};
}
/* merge assumes all keys in a < keys in b */
PNode* pmerge(PNode* a,PNode* b){
    if(!a) return b; if(!b) return a;
    if(a->prio > b->prio){ a->r=pmerge(a->r,b); ppull(a); return a; }
    b->l=pmerge(a,b->l); ppull(b); return b;
}
PNode* pinsert(PNode* root,int key){
    auto node=new PNode(key);
    auto sp=psplit(root,key);
    return pmerge(pmerge(sp.first,node),sp.second);
}
PNode* perase(PNode* root,int key){
    if(!root) return nullptr;
    if(root->key==key){ PNode* res=pmerge(root->l,root->r); delete root; return res; }
    if(key<root->key) root->l=perase(root->l,key); else root->r=perase(root->r,key);
    ppull(root); return root;
}
int pcount_less(PNode* t,int key){
    if(!t) return 0;
    if(key<=t->key) return pcount_less(t->l,key);
    return psz(t->l)+1+pcount_less(t->r,key);
}

/* ----------------- Global Treap (STRONGEST) -------------- */
// Global treap node for strongest crop
struct GNode{
    int key,crop,time; // plot index, crop, timestamp
    GNode *l,*r;
    int sz, maxTime, maxIdx, maxCrop; // augmentation
    GNode(int k,int c,int t):key(k),crop(c),time(t),l(nullptr),r(nullptr),sz(1),
            maxTime(t),maxIdx(k),maxCrop(c){}
};
int gsz(GNode* t){ return t? t->sz:0; }
void gpull(GNode* t){ // update sz + max*
    if(!t) return;
    t->sz = 1 + gsz(t->l) + gsz(t->r);
    t->maxTime=t->time; t->maxIdx=t->key; t->maxCrop=t->crop;
    for(GNode* ch:{t->l,t->r})
        if(ch && (ch->maxTime>t->maxTime || (ch->maxTime==t->maxTime&&ch->maxIdx<t->maxIdx))){
            t->maxTime=ch->maxTime; t->maxIdx=ch->maxIdx; t->maxCrop=ch->maxCrop;
        }
}
/* split by index */
pair<GNode*,GNode*> gsplit(GNode* t,int key){
    if(!t) return {nullptr,nullptr};
    if(key<t->key){ auto sp=gsplit(t->l,key); t->l=sp.second; gpull(t); return {sp.first,t}; }
    auto sp=gsplit(t->r,key); t->r=sp.first; gpull(t); return {t,sp.second};
}
/* merge by (time, key) heap order */
GNode* gmerge(GNode* a,GNode* b){
    if(!a) return b; if(!b) return a;
    if( make_pair(a->time, -a->key) > make_pair(b->time, -b->key) ){
        a->r=gmerge(a->r,b); gpull(a); return a;
    }
    b->l=gmerge(a,b->l); gpull(b); return b;
}
GNode* ginsert(GNode* root,int idx,int crop,int time){
    auto node=new GNode(idx,crop,time);
    auto sp=gsplit(root,idx);
    return gmerge(gmerge(sp.first,node),sp.second);
}
GNode* gerase(GNode* root,int idx){
    if(!root) return nullptr;
    if(root->key==idx){ GNode* res=gmerge(root->l,root->r); delete root; return res; }
    if(idx<root->key) root->l=gerase(root->l,idx); else root->r=gerase(root->r,idx);
    gpull(root); return root;
}

/* ----------------- Game state + logic ------------------- */
int N,Q, globalTime=0;
vector<int> cropType, cropTime;
unordered_map<int,PNode*> perCrop; // crop -> treap root
GNode* globalRoot=nullptr;
struct Act{int idx,crop,time;};
vector<Act> undoStack;

void apply_replace(int idx,int newCrop){
    undoStack.push_back({idx,cropType[idx],cropTime[idx]});
    int oldCrop=cropType[idx];
    perCrop[oldCrop]=perase(perCrop[oldCrop],idx);
    perCrop[newCrop]=pinsert(perCrop.count(newCrop)?perCrop[newCrop]:nullptr, idx);
    globalRoot=gerase(globalRoot,idx);
    int t=++globalTime;
    globalRoot=ginsert(globalRoot,idx,newCrop,t);
    cropType[idx]=newCrop; cropTime[idx]=t;
}
void undo_replace(int idx,int oldCrop,int oldTime){
    perCrop[cropType[idx]]=perase(perCrop[cropType[idx]],idx);
    globalRoot=gerase(globalRoot,idx);
    perCrop[oldCrop]=pinsert(perCrop.count(oldCrop)?perCrop[oldCrop]:nullptr, idx);
    globalRoot=ginsert(globalRoot,idx,oldCrop,oldTime);
    cropType[idx]=oldCrop; cropTime[idx]=oldTime;
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin>>N>>Q;
    cropType.resize(N); cropTime.assign(N,0);
    for(int i=0;i<N;i++){
        cin>>cropType[i];
        perCrop[cropType[i]]=pinsert(perCrop.count(cropType[i])?perCrop[cropType[i]]:nullptr,i);
        globalRoot=ginsert(globalRoot,i,cropType[i],0);
    }

    string op;
    while(Q--){
        cin>>op;
        if(op=="C"){
            int i,v;cin>>i>>v;
            int ans = perCrop.count(v)?pcount_less(perCrop[v],i):0;
            cout<<ans<<"\n";
        }
        else if(op=="R"){
            int i,v;cin>>i>>v;
            apply_replace(i,v);
        }
        else if(op=="U"){
            int k;cin>>k;
            while(k--){
                auto a=undoStack.back(); undoStack.pop_back();
                undo_replace(a.idx,a.crop,a.time);
            }
        }
        else{ // S l r
            int l,r;cin>>l>>r;
            auto sp1=gsplit(globalRoot,l-1);
            auto sp2=gsplit(sp1.second,r);
            cout<<sp2.first->maxCrop<<"\n";
            globalRoot=gmerge(sp1.first, gmerge(sp2.first, sp2.second));
        }
    }
    return 0;
}
