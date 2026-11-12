// Minimal deterministic CPU z-buffer rasterizer. Input/output are private binary streams.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>
struct V {float x,y,iz;};
int main(){
 uint32_t h[4];if(fread(h,4,4,stdin)!=4)return 1;const int W=h[0],H=h[1],nv=h[2],nf=h[3];
 float bg[3];fread(bg,4,3,stdin);std::vector<float> colors(nf*3);fread(colors.data(),4,nf*3,stdin);
 std::vector<V> v(nv);std::vector<uint32_t> f(nf*3);std::vector<float> normal(nf*9);
 if(fread(v.data(),sizeof(V),nv,stdin)!=(size_t)nv)return 2;
 if(fread(f.data(),4,nf*3,stdin)!=(size_t)nf*3)return 3;
 if(fread(normal.data(),4,nf*9,stdin)!=(size_t)nf*9)return 4;
 std::vector<float> depth(W*H,0);std::vector<unsigned char> pix(W*H*3);
 for(int i=0;i<W*H;i++)for(int j=0;j<3;j++)pix[i*3+j]=(unsigned char)(bg[j]*255);
 for(int k=0;k<nf;k++){
  V a=v[f[k*3]],b=v[f[k*3+1]],c=v[f[k*3+2]];
  if(a.iz<=0||b.iz<=0||c.iz<=0)continue;
  float den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);if(std::abs(den)<1e-10)continue;
  int x0=std::max(0,(int)std::floor(std::min({a.x,b.x,c.x}))),x1=std::min(W-1,(int)std::ceil(std::max({a.x,b.x,c.x})));
  int y0=std::max(0,(int)std::floor(std::min({a.y,b.y,c.y}))),y1=std::min(H-1,(int)std::ceil(std::max({a.y,b.y,c.y})));
  const float *n=&normal[k*9];
  for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   float px=x+.5f,py=y+.5f;
   float w0=((b.y-c.y)*(px-c.x)+(c.x-b.x)*(py-c.y))/den;
   float w1=((c.y-a.y)*(px-c.x)+(a.x-c.x)*(py-c.y))/den,w2=1-w0-w1;
   if(w0<-.00001||w1<-.00001||w2<-.00001)continue;
   float iz=w0*a.iz+w1*b.iz+w2*c.iz;int idx=y*W+x;if(iz<=depth[idx])continue;depth[idx]=iz;
   float nx=0,ny=0,nz=0;float ww[3]={w0*a.iz/iz,w1*b.iz/iz,w2*c.iz/iz};
   for(int j=0;j<3;j++){nx+=ww[j]*n[j*3];ny+=ww[j]*n[j*3+1];nz+=ww[j]*n[j*3+2];}
   float ll=std::sqrt(nx*nx+ny*ny+nz*nz)+1e-20f;nx/=ll;ny/=ll;nz/=ll;
   if(nz<0){nx=-nx;ny=-ny;nz=-nz;}
   float key=std::max(0.f,-.38f*nx+.53f*ny+.758f*nz);
   float fill=std::max(0.f,.71f*nx-.15f*ny+.688f*nz);
   float lit=.26f+.64f*key+.10f*fill;
   float spec=.07f*std::pow(std::max(0.f,-.20f*nx+.28f*ny+.939f*nz),35.f);
   for(int j=0;j<3;j++)pix[idx*3+j]=(unsigned char)(255*std::clamp(colors[k*3+j]*lit+spec,0.f,1.f));
  }
 }
 fwrite(pix.data(),1,pix.size(),stdout);return 0;
}
