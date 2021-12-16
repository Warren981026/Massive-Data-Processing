#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <string>
#include <cstring>
#include <map>
#include <fstream>
#include "BOBHash32.h"
#include "params.h"
#include "ssummary.h"
#include "heavykeeper.h"

using namespace std;
map <string ,int> B,C;
struct node {string x;int y;} p[10000005];
ifstream fin("formatted00.dat",ios::in|ios::binary);
char a[65];
string Read()
{
    fin.read(a,8);
    a[8]='\0';
    string tmp=a;
    return tmp;
}
int cmp(node i,node j) {return i.y>j.y;}
int main()
{
    int k,width,depth;
    double decay;
    cin>>k>>width>>depth>>decay;
    cout<<"K="<<k<<endl<<"Width="<<width<<endl<<"Depth="<<depth<<endl<<"Decay="<<decay<<endl;
    cout<<"preparing algorithm"<<endl;
    int m=10000000;  // the number of flows
    // preparing heavykeeper
    heavykeeper *hk=new heavykeeper(k,width,depth,decay);

    // Inserting
    for (int i=1; i<=m; i++)
	{
	    if (i%(m/10)==0) cout<<"Insert "<<i<<endl;
		string s=Read();
		B[s]++;
		hk->Insert(s);
	}
	hk->work();

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
    int hk_sum=0,hk_AAE=0; double hk_ARE=0;
    string hk_string; int hk_num;
    for (int i=0; i<k; i++)
    {
        hk_string=(hk->Query(i)).first; hk_num=(hk->Query(i)).second;
        hk_AAE+=abs(B[hk_string]-hk_num); hk_ARE+=abs(B[hk_string]-hk_num)/(B[hk_string]+0.0);
        if (C[hk_string]) hk_sum++;
    }

    printf("heavkeeper:\nAccepted: %d/%d  %.10f\nARE: %.10f\nAAE: %.10f\n\n",hk_sum,k,(hk_sum/(k+0.0)),hk_ARE/k,hk_AAE/(k+0.0));
   
    return 0;
}
