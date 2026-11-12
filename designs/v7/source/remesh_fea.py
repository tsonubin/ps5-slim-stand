from pathlib import Path
import sys,json,time
import numpy as np,trimesh,pyvista as pv,pyacvd
p=Path(sys.argv[1]);n=int(sys.argv[2]);out=Path(sys.argv[3]);orig=trimesh.load(p)
surf=pv.PolyData(orig.vertices,np.c_[np.full(len(orig.faces),3),orig.faces].ravel())
print('Subdivide',p,flush=True);surf=surf.subdivide_adaptive(max_edge_len=1.6,max_n_passes=4,max_n_tris=1600000)
print('Cluster',surf.n_points,'to',n,flush=True);c=pyacvd.Clustering(surf);c.cluster(n,maxiter=50);s=c.create_mesh();m=trimesh.Trimesh(s.points,s.faces.reshape(-1,4)[:,1:],process=True);m.fix_normals()
if not m.is_watertight or m.body_count!=1:
 import pymeshfix
 print('Repair remesh topology',m.is_watertight,m.body_count,flush=True)
 vv,ff=pymeshfix.clean_from_arrays(np.float64(m.vertices),np.int32(m.faces),remove_smallest_components=False)
 m=trimesh.Trimesh(vv,ff,process=True)
assert m.is_watertight and m.body_count==1
# Deterministic bidirectional sampled surface error, not a rigorous Hausdorff bound.
points=np.vstack([m.vertices[::max(1,len(m.vertices)//4000)],m.triangles_center[::max(1,len(m.faces)//4000)]])
_,d,_=trimesh.proximity.closest_point(orig,points)
points2=np.vstack([orig.vertices[::max(1,len(orig.vertices)//4000)],orig.triangles_center[::max(1,len(orig.faces)//4000)]])
_,d2,_=trimesh.proximity.closest_point(m,points2)
error={'original_volume_mm3':orig.volume,'remesh_volume_mm3':m.volume,'relative_volume_change':m.volume/orig.volume-1,'bidirectional_sample_max_distance_mm':max(float(d.max()),float(d2.max())),'bidirectional_sample_p95_distance_mm':float(np.percentile(np.r_[d,d2],95)),'vertices':len(m.vertices),'faces':len(m.faces)}
print(error,flush=True);assert abs(error['relative_volume_change'])<.04,'Too much geometric change'
m.export(out);out.with_suffix('.json').write_text(json.dumps(error,indent=2))
