"""Regularized simulation surface from exact horizontal CAD sections.
This is a measured approximation, not the manufacturing mesh."""
from pathlib import Path
import sys,json,time
import numpy as np,trimesh,manifold3d as m3,pyvista as pv
from skimage.draw import polygon
from skimage.measure import marching_cubes
from scipy.ndimage import gaussian_filter,binary_fill_holes,label
p=Path(sys.argv[1]);pitch=float(sys.argv[2]);out=Path(sys.argv[3]);orig=trimesh.load(p);body=m3.Manifold(m3.Mesh(np.float32(orig.vertices),np.uint32(orig.faces)));assert body.status()==m3.Error.NoError
lo=np.floor(orig.bounds[0]/pitch)*pitch-3*pitch+pitch/2;hi=np.ceil(orig.bounds[1]/pitch)*pitch+3*pitch
xs=np.arange(lo[0],hi[0]+pitch/2,pitch);ys=np.arange(lo[1],hi[1]+pitch/2,pitch);zs=np.arange(lo[2],hi[2]+pitch/2,pitch)
field=np.zeros((len(zs),len(ys),len(xs)),np.float32);print('Grid',field.shape,'pitch',pitch,flush=True)
for i,z in enumerate(zs):
 polys=body.slice(float(round(z,8))).to_polygons();signed=lambda q:np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))/2
 for q in sorted(polys,key=lambda q:abs(signed(q)),reverse=True):
  rr,cc=polygon((q[:,1]-lo[1])/pitch,(q[:,0]-lo[0])/pitch,shape=field.shape[1:]);field[i,rr,cc]=1 if signed(q)>0 else 0
field=binary_fill_holes(field>.5)
labels,nlabels=label(field)
counts=np.bincount(labels.ravel());counts[0]=0
field=gaussian_filter((labels==counts.argmax()).astype(np.float32),.55)
v,f,_,_=marching_cubes(field,level=.500173,spacing=(pitch,pitch,pitch),allow_degenerate=False)
v=v[:,[2,1,0]]+lo;v[:,2]-=v[:,2].min() # plane at the physical desk datum
m=trimesh.Trimesh(v,f,process=True);m.fix_normals();print('Isosurface',len(m.vertices),len(m.faces),m.is_watertight,flush=True)
surf=pv.PolyData(m.vertices,np.c_[np.full(len(m.faces),3),m.faces].ravel())
# Topology-preserving edge collapse removes voxel sampling redundancy.
surf=surf.smooth_taubin(n_iter=20,pass_band=.15,normalize_coordinates=True)
s=surf.decimate_pro(.65,preserve_topology=True,splitting=False,boundary_vertex_deletion=False)
s=s.smooth_taubin(n_iter=5,pass_band=.2,normalize_coordinates=True)
m=trimesh.Trimesh(s.points,s.faces.reshape(-1,4)[:,1:],process=True);m.update_faces(~np.any(np.diff(np.sort(m.faces,axis=1),axis=1)==0,axis=1));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices();m.fix_normals();print('Decimated',len(m.vertices),len(m.faces),m.is_watertight,m.body_count,flush=True)
if not m.is_watertight or m.body_count!=1:
 import pymeshfix
 before=m.volume;vv,ff=pymeshfix.clean_from_arrays(np.float64(m.vertices),np.int32(m.faces),remove_smallest_components=False)
 m=trimesh.Trimesh(vv,ff,process=True);print('Repair delta',m.volume/before-1,flush=True)
 assert abs(m.volume/before-1)<.002
assert m.is_watertight and m.body_count==1
points=np.vstack([m.vertices[::max(1,len(m.vertices)//2500)],m.triangles_center[::max(1,len(m.faces)//2500)]])
_,d,_=trimesh.proximity.closest_point(orig,points)
points2=np.vstack([orig.vertices[::max(1,len(orig.vertices)//2500)],orig.triangles_center[::max(1,len(orig.faces)//2500)]])
_,d2,_=trimesh.proximity.closest_point(m,points2)
err={'method':'Section raster + Gaussian sigma0.55 voxels + isosurface + topology-preserving decimation','pitch_mm':pitch,'original_volume_mm3':float(orig.volume),'simulation_volume_mm3':float(m.volume),'relative_volume_change':float(m.volume/orig.volume-1),'sample_max_distance_mm':max(float(d.max()),float(d2.max())),'sample_p95_distance_mm':float(np.percentile(np.r_[d,d2],95)),'faces':len(m.faces)}
print(err,flush=True);assert abs(err['relative_volume_change'])<.08 and err['sample_max_distance_mm']<2
m.export(out);out.with_suffix('.json').write_text(json.dumps(err,indent=2))
