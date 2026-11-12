from pathlib import Path
import sys,json,time
import numpy as np,trimesh
from skimage.measure import marching_cubes
sys.path.insert(0,'designs/v11/source')
pth=Path('designs/v11/source/blend_crossings.py');ns={'__file__':str(pth.resolve()),'__name__':'resolution_review'}
exec(compile(pth.read_text().split("print('Crossing patches'")[0],str(pth),'exec'),ns)
centers=ns['centers'];pairs=ns['pairs'];curves=ns['curves'];radii=ns['radii'];distance=ns['distance']
# Pick a repeatable exterior intersection in the middle of the web.
idx=min(range(len(centers)),key=lambda k:np.linalg.norm(centers[k]-[55,-30,24]));c=centers[idx];i,j=pairs[idx]
lo=np.floor((c-4.8)/.12)*.12;hi=np.ceil((c+4.8)/.12)*.12
results=[]
for pitch in [.12,.06]:
 axes=[np.arange(lo[z],hi[z]+pitch*.5,pitch) for z in range(3)];shape=tuple(map(len,axes));p=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
 d1=distance(p,curves[i],radii[i]);d2=distance(p,curves[j],radii[j]);edge=np.min(np.minimum(p-lo,hi-p),axis=1);q=np.clip((edge-.5)/1.2,0,1);k=.45*q*q*(3-2*q);h=np.clip(.5+.5*(d2-d1)/np.maximum(k,1e-9),0,1)
 f=(1-h)*d2+h*d1-k*h*(1-h);hard=np.minimum(d1,d2);vol=[]
 for scalar in [hard,f]:
  field=np.maximum(scalar,.03-edge).reshape(shape).astype(np.float32)
  vv,ff,_,_=marching_cubes(field,0,spacing=(pitch,)*3,allow_degenerate=False);tm=trimesh.Trimesh(vv+lo,ff,process=True);tm.fix_normals();assert tm.is_watertight;vol.append(float(tm.volume))
 results.append({'pitch_mm':pitch,'hard_union_volume_mm3':vol[0],'smooth_union_volume_mm3':vol[1],'fillet_added_volume_mm3':vol[1]-vol[0]});print(results[-1],flush=True)
r={'scope':'One representative crossing patch; compares sampled hard and smooth implicit unions, not full-stand convergence or exact G1','pair':[i,j],'center_mm':c.tolist(),'common_bounds_mm':[lo.tolist(),hi.tolist()],'smooth_min_k_mm':.45,'results':results,'relative_added_volume_change_on_halving_pitch':results[1]['fillet_added_volume_mm3']/results[0]['fillet_added_volume_mm3']-1,'limitations':'Local sample only. Marching-cubes surface interpolation can resolve subvoxel motion but must be checked geometrically; this test does not certify all305crossings.'}
Path('designs/v11/analysis/crossing_resolution_review.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
