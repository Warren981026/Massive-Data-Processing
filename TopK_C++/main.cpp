#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <string>
#include <cstring>
#include <map>
#include <fstream>
#include "topk.h"
#include "topk.c"
#include "murmurhash2.h"
#include "MurmurHash2.c"
#define packet_len 8

using namespace std;

map <string ,int> B,C;
struct node {string x;int y;} p[10000005];
ifstream fin("formatted00.dat",ios::in|ios::binary);
char a[65];

string Read()
{
    fin.read(a,packet_len);
    a[packet_len]='\0';
    string res=a;
    return res;
}
int cmp(node i,node j) {return i.y>j.y;}

int main()
{
    uint32_t k,width,depth;
    double decay;
    cin>>k>>width>>depth>>decay;
    cout<<"K="<<k<<endl<<"Width="<<width<<endl<<"Depth="<<depth<<endl<<"Decay="<<decay<<endl;
    
    int m=10000000;  // the number of flows
    // preparing Topk
    TopK* topk = TopK_Create(k,width,depth,decay);

    // Inserting
    for (int i=1; i<=m; i++)
	{
	    if (i%(m/10)==0) cout<<"Insert "<<i<<endl;
		string key=Read();
		B[key]++;
		TopK_Add(topk,key.c_str(),sizeof(key.c_str()),1);
		
	}
	
    cout<<"preparing true flow"<<endl;
	// preparing true flow
	int cnt=0;
    for (map <string,int>::iterator sit=B.begin(); sit!=B.end(); sit++)
    {
        p[++cnt].x=sit->first;
        p[cnt].y=sit->second;
    }
    sort(p+1,p+cnt+1,cmp);
    for (int i=1; i<=k; i++) C[p[i].x]=p[i].y;

    // Calculating PRE, ARE, AAE
    cout<<"Calculating"<<endl;
    HeapBucket* list = TopK_List(topk);
    int hk_sum=0,hk_AAE=0; double hk_ARE=0;
    string hk_string; int hk_num;
    for (int i=0; i<k; i++)
    {
        hk_string=(string)((list+i)->item); hk_num=(list+i)->count;
        hk_AAE+=abs(B[hk_string]-hk_num); hk_ARE+=abs(B[hk_string]-hk_num)/(B[hk_string]+0.0);
        if (C[hk_string]) hk_sum++;
    }

    printf("heavkeeper:\nAccepted: %d/%d  %.10f\nARE: %.10f\nAAE: %.10f\n\n",hk_sum,k,(hk_sum/(k+0.0)),hk_ARE/k,hk_AAE/(k+0.0));
    TopK_Destroy(topk);

    return 0;
}
