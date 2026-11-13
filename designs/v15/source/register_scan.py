"""Register a phone scan of the console (standing base-up) to the reference model's frame.
usage: register_scan.py <scan.glb, z up, metres> <xmin> <xmax> <ymin> <ymax> <out.json> <scale> [check.png]
Trimmed point-to-point rigid ICP at a FIXED scale (a free scale shrinks the scan to hide its noise), lower 70 mm of the
console only, several starting yaws. The scale comes from the published 216 mm depth of the console.
Design frame: mm, z up from the console's underside, +x disc-drive side, +y rear."""
import sys,json
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
src=sys.argv[1];x0,x1,y0,y1=map(float,sys.argv[2:6]);root=Path(__file__).resolve().parents[3]
sc=trimesh.load(root/'references/console-model/PS5_Slim.glb');ref=[]
for k,g in sc.geometry.items():
 if k=='unnamed_7':continue                       # the original stand ring
 p,_=trimesh.sample.sample_surface(g,int(max(2000,g.area/4)),seed=1);ref.append(p)
ref=np.vstack(ref);ref=ref[ref[:,2]<75];print('model bounds',sc.bounds.round(1).tolist());tree=cKDTree(ref)
m=trimesh.load(src,force='mesh',process=False);cen=m.triangles_center;fm=(cen[:,0]>x0)&(cen[:,0]<x1)&(cen[:,1]>y0)&(cen[:,1]<y1)
ztop=np.percentile(cen[fm,2],99.5);fm&=cen[:,2]>ztop-.068
P,_=trimesh.sample.sample_surface(m.submesh([np.flatnonzero(fm)],append=True),60000,seed=2);P=P*1e3
top=P[P[:,2]>P[:,2].max()-12];c=np.r_[top[:,:2].mean(0),P[:,2].max()];_,V=np.linalg.eigh(np.cov((top[:,:2]-c[:2]).T));ey=V[:,1];best=None
S0=float(sys.argv[7])
def fit(A,B):   # rigid transform A -> B (Kabsch)
 ma,mb=A.mean(0),B.mean(0);H=(B-mb).T@(A-ma)/len(A);U,S,Vt=np.linalg.svd(H);D=np.diag([1,1,np.sign(np.linalg.det(U@Vt))]);R=U@D@Vt;s=1.;return s,R,mb-s*R@ma
for flip in (1,-1):
 for yaw in np.radians(np.arange(-16,16.1,4)):
  e2=flip*np.array([ey[0]*np.cos(yaw)-ey[1]*np.sin(yaw),ey[0]*np.sin(yaw)+ey[1]*np.cos(yaw)]);e1=np.array([e2[1],-e2[0]])
  # base-up to base-down: 180 degree turn about the long axis
  R0=np.array([[-e1[0],-e1[1],0],[e2[0],e2[1],0],[0,0,-1]]);s,R,t=S0,R0,-S0*R0@c+np.array([8.,0,0])
  for it in range(60):
   Q=s*P@R.T+t;d,i=tree.query(Q);keep=d<np.percentile(d,80);ds,dR,dt=fit(Q[keep],ref[i[keep]]);s,R,t=ds*s,dR@R,ds*dR@t+dt
  Q=s*P@R.T+t;d,_=tree.query(Q);cost=float(np.sqrt(np.mean(np.sort(d)[:int(.8*len(d))]**2)));print('flip',flip,'yaw0 %.0f'%np.degrees(yaw),'scale %.4f'%s,'rms80 %.2f mm'%cost)
  if best is None or cost<best[0]:best=(cost,s,R,t)
cost,s,R,t=best;T=np.eye(4);T[:3,:3]=s*R*1e3;T[:3,3]=t
json.dump({'scan_m_to_design_mm':T.tolist(),'scale':s,'trimmed_rms_mm':cost,'published_size_mm':[358,96,216],'model_bounds_mm':sc.bounds.tolist()},open(sys.argv[6],'w'),indent=1);print('best',cost,s)
if len(sys.argv)>8:
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 Q=s*P@R.T+t;fig,ax=plt.subplots(1,3,figsize=(18,10))
 for a_,(z0,z1) in zip(ax,[(3,8),(15,25),(40,55)]):
  q=ref[(ref[:,2]>z0)&(ref[:,2]<z1)];a_.plot(q[:,0],q[:,1],'.',ms=1,color='#bbb');q=Q[(Q[:,2]>z0)&(Q[:,2]<z1)];a_.plot(q[:,0],q[:,1],'r.',ms=1);a_.set_aspect('equal');a_.grid(lw=.3);a_.set_title(f'z {z0}-{z1} mm: grey model, red scan')
 fig.savefig(sys.argv[8],dpi=70,bbox_inches='tight')
