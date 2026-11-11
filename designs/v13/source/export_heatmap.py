"""Offline WebGL viewer containing actual solved FE boundary fields."""
from pathlib import Path
import json,sys,gzip,base64
import numpy as np
from skfem import MeshTet
root=Path(__file__).resolve().parents[1];data=[]
variants=[('v13_coarse_result','v13 — coarse interior mesh'),('v13_fine_result','v13 — finer interior mesh'),('v13_quality_result','v13 — optimized-quality gravity check')]
for tag,label in variants:
 p=root/'analysis'/f'{tag}.npz'
 if not p.exists():continue
 a=np.load(p);r=json.loads(p.with_suffix('.json').read_text());m=MeshTet(a['nodes'].T,a['elements'].T);boundary=m.boundary_facets();f=m.facets[:,boundary].T;owners=m.f2t[0,boundary]
 used=np.unique(f);mapping=np.full(len(a['nodes']),-1);mapping[used]=np.arange(len(used));faces=mapping[f]
 cases={}
 for case in ['vertical_1g','eccentric_1g','rim_side_10N']:
  if case+'_vm' not in a:continue
  cases[case]={'vm':np.round(a[case+'_vm'][owners],7).tolist(),'u':np.round(a[case+'_u'][used],8).tolist(),'metrics':r['results'][case]}
 data.append({'label':label,'id':tag,'vertices':np.round(a['nodes'][used],5).tolist(),'faces':faces.tolist(),'cases':cases,'report':{k:v for k,v in r.items() if k!='results'}})
payload=base64.b64encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),compresslevel=9,mtime=0)).decode()
html=(root/'source/heatmap_template.html').read_text().replace('__GZIP_DATA__',payload)
(root/'output/stress_heatmap_3d.html').write_text(html);print('Viewer models',len(data),'bytes',len(html))
