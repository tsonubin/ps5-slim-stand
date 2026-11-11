"""Basic v12 geometry readback only; no physical qualification or FEA."""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as m3
import veil_v12 as v
out=Path(__file__).resolve().parents[1]/'output'
p=out/'veil_v12_prototype.stl';mesh=trimesh.load(p)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1
body=m3.Manifold(m3.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)))
assert body.status()==m3.Error.NoError
scene=trimesh.load(out/'veil_v12_prototype.3mf');other=scene.to_mesh()
assert other.is_watertight and other.body_count==1
report={'scope':'Basic geometry only; appearance draft, not engineering qualification','mesh':{'watertight':True,'components':1,'faces':len(mesh.faces),'extents_mm':mesh.extents.tolist(),'volume_cm3':mesh.volume/1000,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},'3mf':{'watertight':bool(other.is_watertight),'extents_mm':other.extents.tolist(),'volume_cm3':other.volume/1000},'reference_plan_intersection_mm3':float((body^m3.Manifold.extrude(v.PLAN,100).translate((0,0,30.001))).volume()),'cavity_intersection_mm3':float((body^m3.Manifold.extrude(v.CAV,100).translate((0,0,30.001))).volume()),'nominal_features_mm':{'shell_normal_depth':2.8,'seat_height':30,'reference_clearance':1.5,'support_wall':2.8,'support_top_contact_width':1.54},'limitations':'Reference-derived cavity, not measured hardware. No FEA, slicer qualification, physical fit/load/creep/impact or ventilation test.'}
(out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
