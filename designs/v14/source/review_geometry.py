"""File readback and reference-envelope checks for the v14 exports."""
from pathlib import Path
import sys,json,hashlib,importlib.util
import numpy as np,trimesh,manifold3d as m3
root=Path(__file__).resolve().parents[1];out=root/'output';argv=sys.argv;sys.argv=['x']
spec=importlib.util.spec_from_file_location('veil',root/'source/veil_v14.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
for n in ['veil_v14_prototype.stl','GAUGE_v14_cavity_1.6mm.stl','PRINT_TEST_v14_section.stl']:
 m=trimesh.load(out/n);files[n]={'sha256':sha(out/n),'extents_mm':np.round(m.extents,3).tolist(),'volume_cm3':m.volume/1000,'faces':len(m.faces),'watertight':bool(m.is_watertight and m.is_winding_consistent),'components':int(m.body_count)}
stl=trimesh.load(out/'veil_v14_prototype.stl');t3=trimesh.load(out/'veil_v14_prototype.3mf',force='mesh')
body=m3.Manifold(m3.Mesh(np.float32(stl.vertices),np.uint32(stl.faces)));assert body.status()==m3.Error.NoError
old=trimesh.load(root.parent/'v13/output/GAUGE_v13_cavity_1.6mm.stl')
th=g.TH;gap=g.SR(th)-g.R_C;wt=g.WT(th)
r={'scope':'v14 file readback: format and reference-envelope checks only. No slicing or physical qualification.','files':files,
 '3mf_max_bounds_difference_mm':float(abs(t3.bounds-stl.bounds).max()),'3mf_sha256':sha(out/'veil_v14_prototype.3mf'),
 'reference_plan_intersection_mm3':float((body^m3.Manifold.extrude(g.PLAN,100).translate((0,0,30))).volume()),
 'cavity_intersection_mm3':float((body^m3.Manifold.extrude(g.CAV,100).translate((0,0,30))).volume()),
 'gauge_identical_extents_to_v13':bool(np.allclose(old.extents,files['GAUGE_v14_cavity_1.6mm.stl']['extents_mm'],atol=1e-3)),
 'seat_height_mm':g.H0,'rib_crest_mm':g.RIB_TOP,'pad_centres_xy_mm':[list(p) for p in g.PADS],
 'wall_thickness_mm':{'min':float(wt.min()),'max':float(wt.max()),'rule':'2.8 + extra * smoothstep((radial rim-to-cavity gap - 5)/5), inward only','extra_mm':g.WALL_EXTRA,'perimeter_fraction_above_3.3mm':float((wt>3.3).mean()),'min_radial_gap_minus_thickness_mm':float((gap-wt).min())},
 'generator_sha256':sha(root/'source/veil_v14.py')}
(root/'analysis/geometry_review.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=1))
