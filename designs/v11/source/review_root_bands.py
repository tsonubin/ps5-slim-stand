from pathlib import Path
import sys,json,numpy as np,trimesh
from scipy.spatial import cKDTree
sys.path.insert(0,'designs/v11/source');import veil_v11 as v
from junction_blend import distance
out=Path('designs/v11/output');a=np.load(out/'guide_curves.npz');report=json.loads((out/'junction_blend.json').read_text());pre=trimesh.load(out/'preblend_skin.stl');root=trimesh.load(out/'root_only.stl')
# Deterministic sample of actual root-stage surface vertices and triangle centers.
p=np.vstack([root.vertices[::max(1,len(root.vertices)//6000)],root.triangles_center[::max(1,len(root.faces)//6000)]])
th=np.linspace(-np.pi,np.pi,4320,endpoint=False);rb=v.ring_curve(th,False);rt=v.ring_curve(th,True)
db,ib=cKDTree(rb).query(p);dt,it=cKDTree(rt).query(p);near=(db<3.3)|(dt<2.7);p=p[near&(p[:,2]>.3)]
active=np.zeros(len(p));inpatch=np.zeros(len(p),bool);boundary=np.zeros(len(p),bool)
for rec in report['patches']:
 wi=rec['wire'];top=rec['top'];lo,hi=np.array(rec['bounds_mm']);inside=np.all((p>lo+.1-1e-5)&(p<hi-.1+1e-5),axis=1);ids=np.flatnonzero(inside)
 if not len(ids):continue
 x=p[ids];edge=np.minimum(x-lo,hi-x).min(1);inpatch[ids]=True;boundary[ids[edge<=.5]]=True
 sl=slice(-121,None) if top else slice(0,121);curve=a['points'][wi][sl];r=a['radius'][wi][sl];t=a['theta'][wi][-1 if top else 0];ring=v.ring_curve(np.linspace(t-.43,t+.43,601),top);rr=np.full(len(ring),2.4 if top else 3)
 d1=distance(x,curve,r);d2=distance(x,ring,rr);q=np.clip((edge-.5)/1.2,0,1);k=.85*q*q*(3-2*q);delta=np.maximum(k-np.abs(d1-d2),0)**2/(4*np.maximum(k,1e-12));active[ids]=np.maximum(active[ids],delta)
mask=boundary&(active<1e-7);samples=p[mask]
print('All sampled root-ring points',len(p),'zero-blend-boundary points',len(samples),flush=True)
closest,dist,faces=trimesh.proximity.closest_point(pre,samples);signed=np.sum((samples-closest)*pre.face_normals[faces],axis=1)
result={'scope':'Sampled actual root-only surface at recorded patch boundary zones, excluding any analytically active root fillet. Original preblend skin comparison; not a global Hausdorff or continuity certificate.','samples':len(samples),'distance_p50_mm':float(np.percentile(dist,50)),'distance_p95_mm':float(np.percentile(dist,95)),'distance_max_mm':float(dist.max()),'outward_normal_projection_max_mm':float(signed.max()),'theoretical_48gon_sagitta_base_mm':float(3*(1-np.cos(np.pi/48))),'largest_samples':[{'point':samples[i].tolist(),'distance_mm':float(dist[i]),'signed_normal_projection_mm':float(signed[i])} for i in np.argsort(dist)[-10:]],'root_sha256':__import__('hashlib').sha256((out/'root_only.stl').read_bytes()).hexdigest()}
Path('designs/v11/analysis/root_band_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
