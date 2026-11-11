"""Deterministic point-splat rendering of solved FE surface stress (no browser)."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from skfem import MeshTet
from splat import look_at
root=Path(__file__).resolve().parents[1];tag=sys.argv[1] if len(sys.argv)>1 else 'full_star_refined_result';a=np.load(root/'analysis'/f'{tag}.npz');r=json.loads((root/'analysis'/f'{tag}.json').read_text());m=MeshTet(a['nodes'].T,a['elements'].T);bf=m.boundary_facets();F=m.facets[:,bf].T;V=a['nodes'];case='rim_side_10N' if 'rim_side_10N_vm' in a else 'vertical_1g';vm=a[case+'_vm'][m.f2t[0,bf]];limit=.6 if case=='rim_side_10N' else .06
stops=np.array([[.16,.33,.79],[.13,.78,.83],[.94,.88,.34],[.93,.30,.24]])
def colors(value):
 t=np.clip(value/limit,0,.999999)*3;i=t.astype(int);f=t-i;return stops[i]*(1-f[:,None])+stops[i+1]*f[:,None]
def view(eye,target,W=1100,H=760):
 eye=np.array(eye,float);R=look_at(eye,target);foc=.5*H/np.tan(np.radians(25)/2);buf=np.full((H,W,3),[14,22,36],float)/255;depth=np.full((H,W),np.inf);rng=np.random.default_rng(4)
 for start in range(0,len(F),6000):
  tri=V[F[start:start+6000]];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(n,axis=1)/2;n/=2*area[:,None]+1e-15
  count=np.maximum(1,np.ceil(area/.16**2).astype(int));idx=np.repeat(np.arange(len(tri)),count)
  x,y=rng.random(len(idx)),rng.random(len(idx));flip=x+y>1;x[flip]=1-x[flip];y[flip]=1-y[flip]
  P=tri[idx,0]+x[:,None]*(tri[idx,1]-tri[idx,0])+y[:,None]*(tri[idx,2]-tri[idx,0]);N=n[idx];Q=(P-eye)@R.T;z=-Q[:,2]
  px=(W/2+foc*Q[:,0]/z).astype(int);py=(H/2-foc*Q[:,1]/z).astype(int);ok=(px>=0)&(px<W)&(py>=0)&(py<H)&(z>0)
  c=colors(vm[start:start+len(tri)][idx]);shade=.65+.35*np.abs(N@np.array([.35,-.5,.79]));c*=shade[:,None]
  px,py,z,c=px[ok],py[ok],z[ok],c[ok];order=np.argsort(-z);px,py,z,c=px[order],py[order],z[order],c[order]
  vis=z<depth[py,px];buf[py[vis],px[vis]]=c[vis];depth[py[vis],px[vis]]=z[vis]
 return Image.fromarray(np.uint8(np.clip(buf,0,1)*255))
im=Image.new('RGB',(1500,1000),(14,22,36));im.paste(view((380,-440,270),(8,0,25)),(50,100));d=ImageDraw.Draw(im)
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',24);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
except OSError:font=ImageFont.load_default(size=24);small=ImageFont.load_default(size=19)
d.text((40,24),'VEIL / 3D STRESS HEATMAP',font=font,fill='white');d.text((40,62),tag+' / '+case,font=small,fill=(185,202,225))
for i in range(400):
 c=tuple(np.uint8(colors(np.array([(1-i/399)*limit]))[0]*255));d.line((1230,220+i,1280,220+i),fill=c,width=1)
d.text((1205,175),'Von Mises / MPa',font=small,fill='white')
for j in range(5):d.text((1295,210+j*100),f'{limit*(1-j/4):.2f}',font=small,fill='white')
metrics=r['results'][case]
for y,line in [(840,f'{r["tets"]:,} tetrahedra | peak {metrics["peak_von_mises_MPa"]:.3f} MPa | max displacement {metrics["max_displacement_mm"]:.4f} mm'),(880,f'Colors above {limit:g} MPa saturate red. Shape is undeformed. Material E=1200 MPa, nu=0.35; feet constrained.'),(920,'Screening only. Approximate geometry; printed material, contact, creep and impacts are not validated.'),(955,'Peak stress is mesh-sensitive. Consult the convergence report and the interactive 3D data.')]:d.text((40,y),line,font=small,fill=(205,217,235))
im.save(root/'output'/f'{tag}_stress.png');print('Saved',tag,flush=True)
