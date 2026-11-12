"""Preflight actual maximum-bevel aperture polygons mapped to both shell faces.
Checks polygonal segment distances, not finished-CAD wall thickness or print safety.
"""
from pathlib import Path
import json,numpy as np
from scipy.spatial import cKDTree
from shapely.ops import unary_union
import veil_v13 as v
root=Path(__file__).resolve().parents[1];root.joinpath('analysis').mkdir(exist_ok=True)
polys=v.aperture_polygons(.35)
# Independent central differences of the actual common flow map.
u=np.linspace(0,v.PERIMETER,361);y=np.linspace(0,48,121);p=np.stack(np.meshgrid(u,y),axis=-1).reshape(-1,2);eps=1e-4
J=np.stack([(v.flow_warp(p+np.eye(2)[i]*eps)-v.flow_warp(p-np.eye(2)[i]*eps))/(2*eps) for i in range(2)],axis=-1)
det=np.linalg.det(J);sv=np.linalg.svd(J,compute_uv=False);warp={'sample_grid':[len(y),len(u)],'minimum_jacobian_determinant':float(det.min()),'minimum_jacobian_singular_value':float(sv[:,-1].min()),'maximum_jacobian_singular_value':float(sv[:,0].max())}
# Exact finite-segment minima: candidates include every pair potentially closer than4mm.
def segment_min(a,b,c,d):
 U=b-a;V=d-c;W=a-c;aa=np.einsum('ij,ij->i',U,U);bb=np.einsum('ij,ij->i',U,V);cc=np.einsum('ij,ij->i',V,V);dd=np.einsum('ij,ij->i',U,W);ee=np.einsum('ij,ij->i',V,W);den=aa*cc-bb*bb
 def endpoint(x,y,z):
  q=z-y;t=np.clip(np.einsum('ij,ij->i',x-y,q)/np.einsum('ij,ij->i',q,q),0,1);return np.sum((x-y-t[:,None]*q)**2,axis=1)
 best=np.minimum.reduce([endpoint(a,c,d),endpoint(b,c,d),endpoint(c,a,b),endpoint(d,a,b)])
 s=np.divide(bb*ee-cc*dd,den,out=np.zeros_like(den),where=den>1e-18);t=np.divide(aa*ee-bb*dd,den,out=np.zeros_like(den),where=den>1e-18);inside=(den>1e-18)&(s>=0)&(s<=1)&(t>=0)&(t<=1);dist=np.sum((W+s[:,None]*U-t[:,None]*V)**2,axis=1);best=np.where(inside,np.minimum(best,dist),best)
 return np.sqrt(np.maximum(best,0))
records=[]
for depth in [0.,-v.WALL]:
 starts=[];ends=[];labels=[];lowedge=1e9;highedge=1e9
 for i,poly in enumerate(polys):
  raw=np.array(poly.exterior.coords);xy=np.concatenate([np.linspace(a,b,max(1,int(np.ceil(np.linalg.norm(b-a)/.1)))+1)[:-1] for a,b in zip(raw[:-1],raw[1:])]);xy=np.vstack([xy,xy[0]]);th=v.angle(xy[:,0]);z=xy[:,1]/48*v.SH(th);xyz=v.shell_point(th,z,depth)
  starts.append(xyz[:-1]);ends.append(xyz[1:]);labels.extend([i]*(len(xyz)-1));lowedge=min(lowedge,float(z.min()));highedge=min(highedge,float((v.SH(th)-z).min()))
 a=np.concatenate(starts);b=np.concatenate(ends);labels=np.array(labels);length=np.linalg.norm(b-a,axis=1);mid=(a+b)/2
 pairs=cKDTree(mid).query_pairs(4+length.max(),output_type='ndarray');pairs=pairs[labels[pairs[:,0]]!=labels[pairs[:,1]]]
 ds=segment_min(a[pairs[:,0]],b[pairs[:,0]],a[pairs[:,1]],b[pairs[:,1]]);order=np.argsort(ds);uniq=[];seen=set()
 for idx in order:
  i,j=pairs[idx];key=tuple(sorted((int(labels[i]),int(labels[j]))))
  if key in seen:continue
  seen.add(key);uniq.append({'apertures':list(key),'gap_mm':float(ds[idx]),'near_mm':((mid[i]+mid[j])/2).tolist()})
  if len(uniq)==10:break
 records.append({'shell_depth_mm':depth,'minimum_sampled_segment_gap_mm':float(ds.min()),'maximum_mapped_segment_length_mm':float(length.max()),'lowest_opening_z_mm':lowedge,'minimum_top_lip_z_clearance_mm':highedge,'nearest_distinct_pairs':uniq})
report={'scope':'Pre-Boolean maximum-face-bevel polygon boundaries mapped to outer and inner shell; exact distances between sampled straight boundary segments, not analytic surface or finished mesh certification','apertures':len(polys),'warp':warp,'mapped_boundaries':records,'target_minimum_ligament_mm':2.4,'minimum_gap_mm':min(r['minimum_sampled_segment_gap_mm'] for r in records),'round_termini':'Current cell openings are eroded after the common warp, then adaptively rounded toward 3 mm in the chart. This does not establish a minimum physical corner radius after 3D mapping.','limitations':'Polygonal/chord approximation and mesh cutting still require final inspection. A positive sampled Jacobian is not a global proof, though the same shared periodic map is applied to all cells. No FEA or production slicing.'}
(root/'analysis/aperture_spacing_preflight.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert det.min()>0 and report['minimum_gap_mm']>=2.4
