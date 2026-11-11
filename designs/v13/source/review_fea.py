"""Post-solve mesh quality, conservation and geometry provenance; no filtering peaks."""
from pathlib import Path
import numpy as np,json,hashlib,trimesh
root=Path(__file__).resolve().parents[1];out={};cad=root/'output/veil_v13_prototype.stl';surface=trimesh.load(cad)
for tag in ['v13_coarse_result','v13_fine_result','v13_quality_result']:
 p=root/'analysis'/f'{tag}.npz'
 if not p.exists():continue
 a=np.load(p);r=json.loads(p.with_suffix('.json').read_text());v=a['nodes'][a['elements']];cent=v.mean(1);edge2=sum(np.sum((v[:,j]-v[:,i])**2,1) for i,j in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]);q=12*(3*a['volumes'])**(2/3)/edge2
 res={'tets':len(v),'mean_ratio_quality_percentiles':dict(zip(['min','p0.01','p0.1','p1','p50'],np.percentile(q,[0,.01,.1,1,50]).tolist())),'tet_count_quality_below_0.001':int(sum(q<.001)),'cases':{}}
 for case in ['vertical_1g','eccentric_1g','rim_side_10N']:
  if case not in r['results']:continue
  m=r['results'][case];vm=a[case+'_vm'];i=int(vm.argmax());distance=np.linalg.norm(cent-cent[i],axis=1);near=distance<3;order=np.argsort(vm[near]);nv=a['volumes'][near][order];stress95=vm[near][order[np.searchsorted(np.cumsum(nv),.95*sum(nv))]]
  pt,d,fi=trimesh.proximity.closest_point(surface,cent[i:i+1]);u=a[case+'_u'];imax=int(np.linalg.norm(u,axis=1).argmax())
  item={'peak_tet_volume_mm3':float(a['volumes'][i]),'peak_tet_mean_ratio_quality':float(q[i]),'peak_center_mm':cent[i].tolist(),'peak_distance_to_manufacturing_surface_mm':float(d[0]),'within3mm_volume_weighted_p95_MPa':float(stress95),'force_balance_error_N':float(np.linalg.norm(np.array(m['support_reaction_N'])+m['applied_force_N'])),'max_displacement_node_mm':a['nodes'][imax].tolist()}
  if 'support_reaction_moment_Nmm' in m:item['moment_balance_error_Nmm']=float(np.linalg.norm(np.array(m['support_reaction_moment_Nmm'])+m['load_moment_about_origin_Nmm']))
  assert item['force_balance_error_N']<1e-4
  res['cases'][case]=item
 out[tag]=res
report={'manufacturing_stl_sha256':hashlib.sha256(cad.read_bytes()).hexdigest(),'regularized_surface_sha256':hashlib.sha256((root/'analysis/regularized.stl').read_bytes()).hexdigest(),'quality_definition':'Mean ratio12*(3V)^(2/3)/sum(squared six edge lengths),1 for regular tetrahedron; no elements or peaks removed.','models':out}
(root/'analysis/fea_review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
