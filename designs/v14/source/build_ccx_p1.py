"""Solver cross-check deck: the SAME first-order TetGen mesh and the SAME loads as solve_fea.py, for CalculiX (C3D4).
usage: build_ccx_p1.py <mesh.npz> <out_dir>   Material PA 2200 (E 1650 MPa, nu 0.40)."""
import sys,json
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely import contains_xy
a=np.load(sys.argv[1]);xyz=a['nodes'];conn=a['elements'].astype(np.int64);dest=Path(sys.argv[2]);dest.mkdir(parents=True,exist_ok=True);nn=len(xyz);W=3.2*9.81
p=xyz[conn];neg=np.linalg.det(p[:,1:]-p[:,:1])<0;conn[neg]=conn[neg][:,[0,2,1,3]]
FC=np.array([[0,1,2],[0,3,1],[1,3,2],[2,3,0]]);allf=conn[:,FC].reshape(-1,3);key=np.sort(allf,1);_,inv,cnt=np.unique(key,axis=0,return_inverse=True,return_counts=True);bnd=np.where(cnt[inv]==1)[0]
bel,bfa=bnd//4,bnd%4;tri=xyz[allf[bnd]];cent=tri.mean(1);nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(nrm,axis=1)/2;nz=np.abs(nrm[:,2])/(2*area)
root=Path(__file__).resolve().parents[3];sec=trimesh.load(root/'references/console-model/PS5_Slim.glb').geometry['unnamed_6'].section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
core=max((Polygon(c[:,:2]) for c in sec.discrete if np.linalg.norm(c[0]-c[-1])<.01),key=lambda q:q.area)
seat=(np.abs(tri[:,:,2]-30).max(1)<.3)&(nz>.9)&contains_xy(core,cent[:,0],cent[:,1]);rim=(cent[:,0]>40)&(cent[:,1]>15)&(cent[:,1]<100)&(cent[:,2]>36);base=np.where(xyz[:,2]<xyz[:,2].min()+.2)[0]
def nodal(mask,total):
 f=np.zeros(nn);np.add.at(f,allf[bnd][mask].ravel(),np.repeat(area[mask]/3,3));return f*total/f.sum()
head=['*NODE, NSET=NALL']+[f'{i+1}, {q[0]:.7f}, {q[1]:.7f}, {q[2]:.7f}' for i,q in enumerate(xyz)]+['*ELEMENT, TYPE=C3D4, ELSET=STAND']+[f'{i+1}, '+', '.join(str(n+1) for n in c) for i,c in enumerate(conn)]
ids=[str(i+1) for i in base];head+=['*NSET, NSET=BASE']+[', '.join(ids[i:i+12]) for i in range(0,len(ids),12)]+['*MATERIAL, NAME=PA2200','*ELASTIC','1650., 0.40','*SOLID SECTION, ELSET=STAND, MATERIAL=PA2200','*BOUNDARY','BASE, 1, 3']
for case in ['vertical_1g','rim_side_10N']:
 fz=nodal(seat,-W);d=head+['*STEP','*STATIC','*CLOAD']+[f'{i+1}, 3, {v:.9e}' for i,v in enumerate(fz) if v]   # same nodal weights as solve_fea.py
 if case=='rim_side_10N':d+=[f'{i+1}, 1, {v:.9e}' for i,v in enumerate(nodal(rim,10.)) if v]
 (dest/f'{case}.inp').write_text('\n'.join(d)+'\n*NODE FILE\nU\n*EL FILE\nS\n*NODE PRINT, NSET=BASE, TOTALS=ONLY\nRF\n*END STEP\n')
info={'mesh':sys.argv[1],'mode':'pressure','nodes':int(nn),'tets':int(len(conn)),'element':'C3D4','E_MPa':1650.,'nu':.4,'seat_pressure_area_mm2':float(area[seat].sum())}
np.savez_compressed(dest/'model.npz',xyz=xyz,conn=conn,bfaces=allf[bnd],bmid=allf[bnd],base=base,seat=seat,padtop=seat,rim=rim);(dest/'model.json').write_text(json.dumps(info,indent=2));print(info)
