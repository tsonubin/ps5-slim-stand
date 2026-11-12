"""Write CalculiX decks for the v14 stand from a Gmsh second-order tetrahedral mesh.
usage: build_ccx.py <mesh.msh> <out_dir> <pressure|contact>
Units mm, N, MPa. Material: EOS PA 2200 (E from the EOS data sheet, Poisson ratio from Faes et al. 2015).
pressure: console weight as uniform pressure on the pad tops (same load definition as solve_fea.py).
contact : console as a rigid flat plate resting on the pads through frictionless surface-to-surface contact;
          the weight acts at a reference point, so the pad loads follow from equilibrium.
Cases: vertical_1g, eccentric_1g (pressure: pads at x>8 only; contact: weight point moved 10 mm to +x),
rim_side_10N (weight plus 10 N in +x spread over the wall surface x>40, 15<y<100, z>36)."""
import sys,json
from pathlib import Path
import numpy as np,gmsh,trimesh
from shapely.geometry import Polygon
from shapely import contains_xy
msh,dest,mode=sys.argv[1],Path(sys.argv[2]),sys.argv[3];dest.mkdir(parents=True,exist_ok=True)
E,NU,W=1650.,.40,3.2*9.81
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.open(msh)
tags,xyz,_=gmsh.model.mesh.getNodes();xyz=xyz.reshape(-1,3);et,_,en=gmsh.model.mesh.getElements(3);assert list(et)==[11]
conn=en[0].reshape(-1,10).astype(np.int64);gmsh.finalize()
remap=np.zeros(int(tags.max())+1,np.int64);remap[tags.astype(np.int64)]=np.arange(len(tags));conn=remap[conn][:,[0,1,2,3,4,5,6,7,9,8]]  # Gmsh -> CalculiX C3D10 order
used=np.unique(conn);new=np.full(len(xyz),-1);new[used]=np.arange(len(used));xyz=xyz[used];conn=new[conn];nn,ne=len(xyz),len(conn)
# Boundary faces. CalculiX tetra faces: S1 1-2-3, S2 1-4-2, S3 2-4-3, S4 3-4-1; mid-side nodes follow.
FC=np.array([[0,1,2],[0,3,1],[1,3,2],[2,3,0]]);FM=np.array([[4,5,6],[7,8,4],[8,9,5],[9,7,6]])
allf=conn[:,FC].reshape(-1,3);key=np.sort(allf,1);_,inv,cnt=np.unique(key,axis=0,return_inverse=True,return_counts=True);bnd=np.where(cnt[inv]==1)[0]
bel,bfa=bnd//4,bnd%4;tri=xyz[allf[bnd]];mid=conn[bel[:,None],FM[bfa]];cent=tri.mean(1)
nrm=-np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(nrm,axis=1)/2;nz=nrm[:,2]/(2*area) # face 1-2-3 of a positive tetrahedron winds inward, hence the sign
root=Path(__file__).resolve().parents[3]
sec=trimesh.load(root/'references/console-model/PS5_Slim.glb').geometry['unnamed_6'].section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
core=max((Polygon(c[:,:2]) for c in sec.discrete if np.linalg.norm(c[0]-c[-1])<.01),key=lambda q:q.area)
incore=contains_xy(core,cent[:,0],cent[:,1])
seat=(np.abs(tri[:,:,2]-30).max(1)<.3)&(nz>.9)&incore                 # same rule as solve_fea.py
padtop=(tri[:,:,2].min(1)>29.2)&(nz>.7)&incore                         # whole pad land for contact
rim=(cent[:,0]>40)&(cent[:,1]>15)&(cent[:,1]<100)&(cent[:,2]>36)
base=np.where(xyz[:,2]<xyz[:,2].min()+.2)[0]
PADS=np.array([(-16.5,44.),(16.5,44.),(-11.5,-44.),(11.5,-44.)]);padid=np.linalg.norm(cent[:,None,:2]-PADS[None],axis=2).argmin(1)
def lines(ids,per=12):
 ids=[str(int(i)) for i in ids];return '\n'.join(', '.join(ids[i:i+per]) for i in range(0,len(ids),per))
def side_cload():
 f=np.zeros(nn);np.add.at(f,mid[rim].ravel(),np.repeat(area[rim]/3,3));f*=10/f.sum()  # consistent loads of a quadratic triangle sit on the mid-side nodes
 return ''.join(f'{i+1}, 1, {v:.9e}\n' for i,v in enumerate(f) if v)
head=['*NODE, NSET=NALL']+[f'{i+1}, {p[0]:.7f}, {p[1]:.7f}, {p[2]:.7f}' for i,p in enumerate(xyz)]
head+=['*ELEMENT, TYPE=C3D10, ELSET=STAND']+[f'{i+1}, '+', '.join(str(n+1) for n in c) for i,c in enumerate(conn)]
head+=['*NSET, NSET=BASE',lines(base+1),'*MATERIAL, NAME=PA2200','*ELASTIC',f'{E}, {NU}','*DENSITY','0.93E-9','*SOLID SECTION, ELSET=STAND, MATERIAL=PA2200','*BOUNDARY','BASE, 1, 3']
info={'mesh':msh,'mode':mode,'nodes':int(nn),'tets':int(ne),'E_MPa':E,'nu':NU,'weight_N':W,'fixed_nodes':int(len(base)),'seat_pressure_area_mm2':float(area[seat].sum()),'pad_contact_surface_mm2':float(area[padtop].sum()),'side_patch_area_mm2':float(area[rim].sum()),'cases':{}}
out='*NODE FILE\nU\n*EL FILE\nS\n*NODE PRINT, NSET=BASE, TOTALS=ONLY\nRF\n'
if mode=='pressure':
 for case,mask in [('vertical_1g',seat),('eccentric_1g',seat&(cent[:,0]>8)),('rim_side_10N',seat)]:
  p=W/area[mask].sum();d=head+['*STEP','*STATIC','*DLOAD']+[f'{e+1}, P{f+1}, {p:.9e}' for e,f in zip(bel[mask],bfa[mask])]
  if case=='rim_side_10N':d+=['*CLOAD',side_cload().rstrip()]
  (dest/f'{case}.inp').write_text('\n'.join(d)+'\n'+out+'*END STEP\n');info['cases'][case]={'pressure_MPa':float(p),'loaded_area_mm2':float(area[mask].sum())}
else:
 c0=np.array(core.centroid.coords[0]);gx=np.linspace(-45,45,7)+c0[0]*0;gy=np.linspace(-80,80,11)
 for case,pt in [('vertical_1g',c0),('eccentric_1g',c0+[10,0]),('rim_side_10N',c0)]:
  pn=[];pe=[];idx=lambda i,j,k:nn+1+(k*len(gy)+j)*len(gx)+i
  for k,z in enumerate([30.,34.]):
   for y in gy:
    for x in gx:pn.append(f'{nn+1+len(pn)}, {x:.4f}, {y:.4f}, {z:.4f}')
  for j in range(len(gy)-1):
   for i in range(len(gx)-1):pe.append(f'{ne+1+len(pe)}, '+', '.join(str(idx(a,b,k)) for k in (0,1) for a,b in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]))
  ref,rot=nn+len(pn)+1,nn+len(pn)+2
  d=head+['*NODE, NSET=NPLATE']+pn+['*NODE, NSET=NREF',f'{ref}, {pt[0]:.5f}, {pt[1]:.5f}, 30.0',f'{rot}, {pt[0]:.5f}, {pt[1]:.5f}, 30.0']
  d+=['*ELEMENT, TYPE=C3D8, ELSET=PLATE']+pe+['*MATERIAL, NAME=RIGIDISH','*ELASTIC','200000., 0.3','*SOLID SECTION, ELSET=PLATE, MATERIAL=RIGIDISH',f'*RIGID BODY, NSET=NPLATE, REF NODE={ref}, ROT NODE={rot}']
  # One slave surface and contact pair per pad, so the solver reports each pad's contact force (*CONTACT PRINT, CF).
  for i in range(4):d+=[f'*SURFACE, NAME=PAD{i+1}, TYPE=ELEMENT']+[f'{e+1}, S{f+1}' for e,f in zip(bel[padtop&(padid==i)],bfa[padtop&(padid==i)])]
  d+=['*SURFACE, NAME=MASTER, TYPE=ELEMENT']+[f'{ne+1+i}, S1' for i in range(len(pe))]
  for i in range(4):d+=['*CONTACT PAIR, INTERACTION=SEAT, TYPE=SURFACE TO SURFACE, ADJUST=0.45',f'PAD{i+1}, MASTER']
  d+=['*SURFACE INTERACTION, NAME=SEAT','*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=LINEAR','2.E4']
  d+=['*BOUNDARY',f'{ref}, 1, 2',f'{rot}, 3, 3','*STEP, INC=60','*STATIC','0.5, 1., 1.E-4, 1.','*CLOAD',f'{ref}, 3, {-W:.6f}']
  if case=='rim_side_10N':d+=[side_cload().rstrip()]
  (dest/f'{case}.inp').write_text('\n'.join(d)+'\n'+out+'*CONTACT FILE\nCDIS, CSTR\n'+''.join(f'*CONTACT PRINT, SLAVE=PAD{i+1}, MASTER=MASTER, TOTALS=ONLY\nCF\n' for i in range(4))+'*END STEP\n');info['cases'][case]={'weight_point_xy_mm':[float(pt[0]),float(pt[1])]}
info['core_centroid_xy_mm']=list(map(float,core.centroid.coords[0]))
np.savez_compressed(dest/'model.npz',xyz=xyz,conn=conn,bfaces=allf[bnd],bmid=mid,base=base,seat=seat,padtop=padtop,rim=rim)
(dest/'model.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=1))
