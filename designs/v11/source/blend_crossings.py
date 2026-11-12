"""Add small local fillets at middle-web crossings to cached ring-root CAD."""
from pathlib import Path
import json,time,sys
import numpy as np,trimesh,manifold3d as m3
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
import veil_v11 as v
from junction_blend import distance
out=Path(__file__).resolve().parents[1]/'output'
a=np.load(out/'guide_curves.npz');curves=list(a['points']);radii=list(a['radius'])
for bi,fraction in enumerate([.36,.69]):
 th=np.linspace(-np.pi,np.pi,1441);t=fraction+.12*np.sin(th+bi*1.7)+.065*np.cos(2*th-.4)
 curves.append(v.surface(th,t));radii.append(np.full(len(th),1.65))
trees=[cKDTree(p) for p in curves];centers=[];pairs=[]
for i in range(len(curves)):
 for j in range(i+1,len(curves)):
  d,ix=trees[j].query(curves[i]);keep=np.where(d<radii[i]+radii[j][ix]+.40)[0]
  if not len(keep):continue
  mid=(curves[i][keep]+curves[j][ix[keep]])/2
  th=np.arctan2(mid[:,1]-v.CENTER[1],mid[:,0]-v.CENTER[0])
  keep=keep[(mid[:,2]>7)&(mid[:,2]<v.interp(v.RIMH,th)-6.5)]
  if not len(keep):continue
  groups=np.split(keep,np.where(np.diff(keep)>3)[0]+1)
  for group in groups:
   k=group[np.argmin(d[group])];c=(curves[i][k]+curves[j][ix[k]])/2
   if any(pair==(i,j) and np.linalg.norm(c-old)<3.0 for old,pair in zip(centers,pairs)):continue
   centers.append(c);pairs.append((i,j))
print('Crossing patches',len(centers),flush=True)
pitch=.12;blend=.45;patches=[];records=[];start=time.time()
for number,(c,(i,j)) in enumerate(zip(centers,pairs)):
 lo=np.floor((c-4.8)/pitch)*pitch;hi=np.ceil((c+4.8)/pitch)*pitch
 axes=[np.arange(lo[z],hi[z]+pitch*.5,pitch) for z in range(3)];shape=tuple(map(len,axes));p=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
 d1=distance(p,curves[i],radii[i]);d2=distance(p,curves[j],radii[j])
 edge=np.min(np.minimum(p-lo,hi-p),axis=1);q=np.clip((edge-.5)/1.2,0,1);q=q*q*(3-2*q);k=blend*q
 h=np.clip(.5+.5*(d2-d1)/np.maximum(k,1e-9),0,1)
 f=(1-h)*d2+h*d1-k*h*(1-h);f=np.maximum(f,.5*pitch-edge).reshape(shape).astype(np.float32)
 vv,ff,_,_=marching_cubes(f,0,spacing=(pitch,)*3,allow_degenerate=False)
 tm=trimesh.Trimesh(vv+lo,ff,process=True);tm.fix_normals();assert tm.is_watertight
 patch=m3.Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)));assert patch.status()==m3.Error.NoError
 patches.append(patch);records.append({'pair':[i,j],'center_mm':c.tolist(),'bounds_mm':[lo.tolist(),hi.tolist()]})
 if number%25==0:print('Crossings',number+1,'/',len(centers),'seconds',round(time.time()-start,1),flush=True)
tm=trimesh.load(out/'root_only.stl');body=m3.Manifold(m3.Mesh(np.float32(tm.vertices),np.uint32(tm.faces)));before=body.volume()
body=body+m3.Manifold.batch_boolean(patches,m3.OpType.Add)
body=body-m3.Manifold.extrude(v.CAV,100).translate((0,0,v.H0))
parts=body.decompose();main=max(parts,key=lambda x:x.volume());residue=sum(abs(x.volume()) for x in parts if x is not main)
assert residue<1 and all(x.volume()<.01 for x in parts if x is not main);body=main
print('Crossing union added mm3',body.volume()-before,'residue',residue,flush=True)
cache=body.to_mesh64();np.savez_compressed(out.parent/'analysis/crossing_union_full_precision.npz',V=np.asarray(cache.vert_properties)[:,:3],F=np.asarray(cache.tri_verts),merge_from=np.asarray(cache.merge_from_vert),merge_to=np.asarray(cache.merge_to_vert))
(out/'crossing_union_checkpoint.json').write_text(json.dumps({'count':len(patches),'added_body_volume_mm3':body.volume()-before,'pitch_mm':pitch,'smooth_min_k_mm':blend,'patches':records},indent=2))
for tolerance in [.008,.004,.002,.001,.0005]:
 try:mesh=v.to_trimesh(body,tolerance);break
 except AssertionError:print('Body retry tolerance',tolerance,flush=True)
else:raise RuntimeError('Body export not closed')
# If fine export was required for closure, use the same accepted recovery
# route: retain its bounded-welded cache, then simplify that valid mesh at .004.
if len(mesh.faces)>2500000:
 np.savez_compressed(out.parent/'analysis/crossing_repaired_full.npz',V=mesh.vertices,F=mesh.faces)
 recovered=m3.Manifold(m3.Mesh64(np.asarray(mesh.vertices,np.float64),np.asarray(mesh.faces,np.uint64)))
 assert recovered.status()==m3.Error.NoError
 mesh=v.to_trimesh(recovered,.004)
assert mesh.body_count==1
for suffix in ['stl','3mf']:mesh.export(out/f'veil_v11_prototype.{suffix}')
np.savez_compressed(out/'mesh.npz',V=mesh.vertices,F=mesh.faces)
import gzip,shutil
with (out/'veil_v11_prototype.stl').open('rb') as src,gzip.open(out/'veil_v11_prototype.stl.gz','wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst)
report={'method':'Localized polynomial smooth-min tube-distance additions at middle-web crossings, applied to cached root-only CAD','pitch_mm':pitch,'smooth_min_k_mm':blend,'maximum_implicit_distance_offset_mm':blend/4,'zero_blend_boundary_margin_mm':.5,'blend_taper_width_mm':1.2,'count':len(patches),'added_body_volume_mm3':body.volume()-before,'patches':records,'limitations':'Sampled distance/isosurface approximation; no assertion of exact G1 on final triangulated Boolean mesh.'}
(out/'crossing_blend.json').write_text(json.dumps(report,indent=2))
clip=m3.Manifold.cube((58,36,80)).translate((22,34,0));coupon=max((body^clip).decompose(),key=lambda x:x.volume())
for tolerance in [.008,.004,.002,.001,.0005]:
 try:test=v.to_trimesh(coupon,tolerance);break
 except AssertionError:print('Coupon retry tolerance',tolerance,flush=True)
else:raise RuntimeError('Coupon export not closed')
test.apply_translation(-test.bounds[0]);test.export(out/'PRINT_TEST_v11_section.stl')
print('Final',mesh.extents,'cm3',mesh.volume/1000,'faces',len(mesh.faces),'coupon tolerance',tolerance,flush=True)
