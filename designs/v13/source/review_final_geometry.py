"""Basic final file readback for the visual prototype; no FEA or slicing."""
from pathlib import Path
import sys,json,hashlib,ast
import numpy as np,trimesh,manifold3d as m
import veil_v13 as v
root=Path(__file__).resolve().parents[1];out=root/'output';sys.path.insert(0,str(root.parent/'v12/source'));import veil_v12 as old
files={};meshes={}
for name in ['veil_v13_prototype.stl','GAUGE_v13_cavity_1.6mm.stl','PRINT_TEST_v13_section.stl']:
 p=out/name;t=trimesh.load(p);meshes[name]=t
 files[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'extents_mm':t.extents.tolist(),'volume_cm3':float(t.volume/1000),'faces':len(t.faces),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':int(t.body_count)}
 assert t.is_watertight and t.is_winding_consistent and t.body_count==1 and t.volume>0
full=meshes['veil_v13_prototype.stl'];s=trimesh.load(out/'veil_v13_prototype.3mf').to_mesh();assert s.is_watertight and s.body_count==1 and np.max(abs(s.bounds-full.bounds))<1e-5
b=m.Manifold(m.Mesh(np.float32(full.vertices),np.uint32(full.faces)))
clip=m.Manifold.cube((58,36,80)).translate((22,34,0));under=v.supports();clipped=b^clip
# Read the actual adaptive radius choices without rebuilding solid cutters.
tree=ast.parse((root/'source/veil_v13.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='aperture_polygons');fn.name='rounding_values'
for node in ast.walk(fn):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='result' and node.func.attr=='append':node.args=[ast.Name(id='rounding',ctx=ast.Load())]
ns=vars(v).copy();exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'actual_rounding_choices','exec'),ns);rounds=ns['rounding_values']()
r={'scope':'Final softened v13 visual prototype. Basic geometry/format checks only; no FEA, production slicing or physical qualification.','generator_source_sha256':hashlib.sha256((root/'source/veil_v13.py').read_bytes()).hexdigest(),'files':files,'3mf':{'sha256':hashlib.sha256((out/'veil_v13_prototype.3mf').read_bytes()).hexdigest(),'watertight':bool(s.is_watertight),'components':int(s.body_count),'extents_mm':s.extents.tolist(),'volume_cm3':float(s.volume/1000),'max_bounds_difference_from_STL_mm':float(np.max(abs(s.bounds-full.bounds)))},'cavity_set_difference_areas_mm2':[float((v.CAV-old.CAV).area()),float((old.CAV-v.CAV).area())],'seat_height_mm':v.H0,'reference_intersection_mm3':float((b^m.Manifold.extrude(v.PLAN,100).translate((0,0,30.001))).volume()),'cavity_intersection_mm3':float((b^m.Manifold.extrude(v.CAV,100).translate((0,0,30.001))).volume()),'coupon':{'source_clip_bounds_mm':[[22,34,0],[80,70,80]],'understructure_volume_in_clip_cm3':float((under^clip).volume()/1000),'full_model_clip_components':len(clipped.decompose()),'note':'Actual shell apertures and support geometry are included, but this cut specimen does not qualify all manufacturing features or strength.'},'rounding_chart_radius_mm':{'count':len(rounds),'minimum':float(min(rounds)),'maximum':float(max(rounds)),'values':sorted(set(round(float(x),6) for x in rounds))},'support_nominal_width_mm':2.8,'support_minimum_unchamfered_vertical_web_mm':6.8,'support_top_contact_width_mm':1.54,'aperture_preflight':'aperture_spacing_preflight.json; mapped maximum-bevel polygon boundaries, not final volumetric wall-thickness certification'}
(root/'analysis/light_geometry_review.json').write_text(json.dumps(r,indent=2));q=root/'analysis/aperture_spacing_preflight.json';z=json.loads(q.read_text());z['generator_source_sha256']=r['generator_source_sha256'];q.write_text(json.dumps(z,indent=2));print(json.dumps(r,indent=2))
