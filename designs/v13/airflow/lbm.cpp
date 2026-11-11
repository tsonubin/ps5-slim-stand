// D3Q19 BGK, halfway link bounceback; pressure via non-equilibrium extrapolation.
#include <vector>
#include <cmath>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <iomanip>
using namespace std;
int main(int argc,char**argv){ifstream in(argv[1],ios::binary);int nx,ny,nz;in.read((char*)&nx,4);in.read((char*)&ny,4);in.read((char*)&nz,4);int n=nx*ny*nz;vector<unsigned char> t(n);in.read((char*)t.data(),n);vector<int> ref(n);in.read((char*)ref.data(),n*4);int c[19][3]={{0,0,0},{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1},{1,1,0},{-1,-1,0},{1,-1,0},{-1,1,0},{1,0,1},{-1,0,-1},{1,0,-1},{-1,0,1},{0,1,1},{0,-1,-1},{0,1,-1},{0,-1,1}};int op[19]={0,2,1,4,3,6,5,8,7,10,9,12,11,14,13,16,15,18,17};double w[19];for(int q=0;q<19;q++)w[q]=q==0?1./3:q<7?1./18:1./36;vector<int> nb(n*19,-1),active,bounds;for(int z=0;z<nz;z++)for(int y=0;y<ny;y++)for(int x=0;x<nx;x++){int i=(z*ny+y)*nx+x;if(!t[i])continue;(t[i]==1?active:bounds).push_back(i);for(int q=0;q<19;q++){int a=x-c[q][0],b=y-c[q][1],d=z-c[q][2];if(a>=0&&a<nx&&b>=0&&b<ny&&d>=0&&d<nz){int j=(d*ny+b)*nx+a;if(t[j])nb[i*19+q]=j;}}}
vector<double> f(n*19),g(n*19),vel(n*3),last(n*3);for(int i=0;i<n;i++)for(int q=0;q<19;q++)f[i*19+q]=w[q];double tau=.8,delta=argc>4?atof(argv[4]):1e-5;int maxit=argc>3?atoi(argv[3]):10000;double rel=1;int it=0;auto macro=[&](int i,double&rho,double*u){rho=0;u[0]=u[1]=u[2]=0;for(int q=0;q<19;q++){double a=f[i*19+q];rho+=a;for(int k=0;k<3;k++)u[k]+=a*c[q][k];}for(int k=0;k<3;k++)u[k]/=rho;};auto eq=[&](int q,double rho,double*u){double cu=c[q][0]*u[0]+c[q][1]*u[1]+c[q][2]*u[2];return w[q]*rho*(1+3*cu+4.5*cu*cu-1.5*(u[0]*u[0]+u[1]*u[1]+u[2]*u[2]));};
for(it=1;it<=maxit;it++){
for(int i:active){double rho,u[3];macro(i,rho,u);for(int k=0;k<3;k++)vel[i*3+k]=u[k];for(int q=0;q<19;q++)f[i*19+q]-=(f[i*19+q]-eq(q,rho,u))/tau;}
for(int i:bounds){int j=ref[i];double rho,u[3];macro(j,rho,u);double rb=t[i]==2?1.:1.-delta;for(int q=0;q<19;q++)f[i*19+q]=eq(q,rb,u)+f[j*19+q]-eq(q,rho,u);}
for(int i:active)for(int q=0;q<19;q++){int j=nb[i*19+q];g[i*19+q]=j<0?f[i*19+op[q]]:f[j*19+q];}
for(int i:bounds)for(int q=0;q<19;q++)g[i*19+q]=f[i*19+q];f.swap(g);
if(it%250==0){double a=0,b=0;for(int i:active)for(int k=0;k<3;k++){double d=vel[i*3+k]-last[i*3+k];a+=d*d;b+=vel[i*3+k]*vel[i*3+k];}rel=sqrt(a/max(b,1e-50));last=vel;cerr<<it<<" relative_change "<<rel<<endl;if(!isfinite(rel))return 2;if(rel<1e-6&&it>=1000)break;}}
ofstream out(argv[2],ios::binary);for(int i=0;i<n;i++){double rho,u[3];macro(i,rho,u);float v[4]={(float)rho,(float)u[0],(float)u[1],(float)u[2]};out.write((char*)v,16);}double flux[4]={};for(int i:active){double rho,u[3];macro(i,rho,u);for(int q=1;q<19;q++){int j=nb[i*19+q];if(j>=0&&t[j]>=2){double fo=f[i*19+op[q]]-(f[i*19+op[q]]-eq(op[q],rho,u))/tau;flux[t[j]]+=f[j*19+q]-fo;}}}cout<<setprecision(14)<<"{\"iterations\":"<<it<<",\"relative_change\":"<<rel<<",\"link_flux_in\":"<<flux[2]<<",\"link_flux_out\":"<<-flux[3]<<"}"<<endl;
}
