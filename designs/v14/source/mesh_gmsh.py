"""Second-order tetrahedral mesh with Gmsh, refined at pads/rib crossings and the +x wall struts.
usage: mesh_gmsh.py <surface.stl> <base_size_mm> <out.msh> [reparam|direct]
'reparam' rebuilds a parametrised surface from the STL so Gmsh can remesh it; 'direct' keeps the STL facets."""
import sys,time,json
from pathlib import Path
import numpy as np,gmsh
stl,h,out=sys.argv[1],float(sys.argv[2]),Path(sys.argv[3]);mode=sys.argv[4] if len(sys.argv)>4 else 'reparam'
PADS=[(-16.5,44.),(16.5,44.),(-11.5,-44.),(11.5,-44.)]
gmsh.initialize();gmsh.option.setNumber('General.NumThreads',6);gmsh.option.setNumber('General.Terminal',1);gmsh.option.setNumber('General.Verbosity',3)
t=time.time();gmsh.merge(stl)
if mode=='reparam':
 gmsh.model.mesh.classifySurfaces(np.radians(40),True,True,np.pi);gmsh.model.mesh.createGeometry()
gmsh.model.geo.synchronize() if False else None
s=[e[1] for e in gmsh.model.getEntities(2)];loop=gmsh.model.geo.addSurfaceLoop(s);gmsh.model.geo.addVolume([loop]);gmsh.model.geo.synchronize()
f=gmsh.model.mesh.field;ids=[]
def box(x0,x1,y0,y1,z0,z1,vin,thick=4.):
 i=f.add('Box');[f.setNumber(i,k,v) for k,v in dict(VIn=vin,VOut=h,XMin=x0,XMax=x1,YMin=y0,YMax=y1,ZMin=z0,ZMax=z1,Thickness=thick).items()];ids.append(i)
for sy in (1,-1):box(-24,24,sy*44-13,sy*44+13,8,31,h*.45)   # pads, pad roots and the four rib crossings
box(38,90,-5,112,0,45,h*.55)                                   # wall struts under the side-push patch
m=f.add('Min');f.setNumbers(m,'FieldsList',ids);f.setAsBackgroundMesh(m)
for k,v in {'Mesh.MeshSizeExtendFromBoundary':0,'Mesh.MeshSizeFromPoints':0,'Mesh.MeshSizeFromCurvature':0,'Mesh.MeshSizeMax':h,'Mesh.MeshSizeMin':h*.3,'Mesh.Algorithm':6,'Mesh.Algorithm3D':10,'Mesh.Optimize':1,'Mesh.OptimizeNetgen':0}.items():gmsh.option.setNumber(k,v)
gmsh.model.mesh.generate(3)
_,tg,_=gmsh.model.mesh.getElements(3);q=gmsh.model.mesh.getElementQualities(np.concatenate(tg).tolist(),'gamma')
gmsh.model.mesh.setOrder(2)
types,tags,nodes=gmsh.model.mesh.getElements(3);n=sum(len(x) for x in tags)
info={'input':stl,'mode':mode,'base_size_mm':h,'tets':int(n),'nodes':int(len(gmsh.model.mesh.getNodes()[0])),'element_types':[int(x) for x in types],'quality_measure':'gamma (inscribed/circumscribed radius ratio) of the straight-sided tetrahedra before mid-side nodes are added','min_gamma':float(q.min()),'p1_gamma':float(np.percentile(q,1)),'tets_gamma_below_0.05':int((q<.05).sum()),'seconds':time.time()-t}
gmsh.write(str(out));out.with_suffix('.json').write_text(json.dumps(info,indent=2));print(info);gmsh.finalize()
