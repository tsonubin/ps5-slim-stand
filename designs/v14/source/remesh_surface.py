"""Isotropic, locally refined surface remesh of the regularized simulation surface with MMG (mmgs).
usage: remesh_surface.py <in.stl> <base_edge_mm> <out.stl> [hausdorff_mm]
Target edge is base size, 0.45x around the pads / rib crossings and 0.55x on the +x wall struts; MMG keeps
the new surface within the given Hausdorff tolerance (default 0.2 mm) of the input and stays manifold."""
import sys,json
from pathlib import Path
import numpy as np,trimesh,mmgpy
src,h,out=sys.argv[1],float(sys.argv[2]),Path(sys.argv[3]);m=trimesh.load(src);p=np.asarray(m.vertices,float)
size=np.full(len(p),h)
for sy in (1,-1):size[(abs(p[:,0])<24)&(abs(p[:,1]-sy*44)<13)&(p[:,2]>8)]=.45*h
k=(p[:,0]>38)&(p[:,1]>-5)&(p[:,1]<112);size[k]=np.minimum(size[k],.55*h)
mesh=mmgpy.MmgMeshS(p,np.asarray(m.faces,np.int32));mesh.set_field('metric',size[:,None])
HAUSD=float(sys.argv[4]) if len(sys.argv)>4 else .2
mesh.remesh(hausd=HAUSD,hgrad=1.3,hmin=.3*h,hmax=h,angle=0,verbose=-1)
t=trimesh.Trimesh(mesh.get_vertices(),mesh.get_triangles(),process=True);t.fix_normals()
assert t.is_watertight and t.body_count==1 and t.volume>0
_,d,_=trimesh.proximity.closest_point(m,t.vertices[::max(1,len(t.vertices)//4000)]);_,d2,_=trimesh.proximity.closest_point(t,p[::max(1,len(p)//4000)])
e=t.edges_unique_length;a=np.sort(t.triangles[:,[0,1,2,0]],0);tri=t.triangles;l=np.linalg.norm(tri-np.roll(tri,1,1),axis=2);q=4*np.sqrt(3)*t.area_faces/(l**2).sum(1)
info={'input':src,'tool':'MMG '+str(mmgpy.MMG_VERSION),'base_edge_mm':h,'hausdorff_tolerance_mm':HAUSD,'faces':len(t.faces),'edge_mm_p5_p50_p95':np.percentile(e,[5,50,95]).round(3).tolist(),'triangle_quality_min_p1':[float(q.min()),float(np.percentile(q,1))],'volume_change_vs_input':float(t.volume/m.volume-1),'max_sampled_deviation_mm':float(max(d.max(),d2.max())),'p95_sampled_deviation_mm':float(np.percentile(np.r_[d,d2],95))}
t.export(out);out.with_suffix('.json').write_text(json.dumps(info,indent=2));print(info)
