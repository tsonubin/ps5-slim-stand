"""Geometry and quasi-static estimates only. No G-code, FEA, CFD, or physical test."""
from pathlib import Path
import json,sys,hashlib
import numpy as np, trimesh, manifold3d as m3
from scipy.spatial import ConvexHull
sys.path.insert(0,str(Path(__file__).parent))
import veil_v7 as v
out=Path(__file__).resolve().parent.parent/'output'
mesh=trimesh.load(out/'veil_v7_prototype.stl')
body=m3.Manifold(m3.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)))
assert mesh.is_watertight and mesh.is_winding_consistent and body.status()==m3.Error.NoError
report={'scope':'Geometric checks and conditional rigid-body estimates, NOT physical qualification','mesh':{},'sections':{}}
for p in out.glob('*.stl'):
 t=trimesh.load(p);report['mesh'][p.name]={'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':int(t.body_count),'bounds_mm':t.bounds.tolist(),'volume_cm3':float(t.volume/1000),'faces':len(t.faces),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 assert t.is_watertight and t.body_count==1
scene=trimesh.load(out/'veil_v7_prototype.3mf'); t=scene.to_mesh()
report['3mf']={'watertight':bool(t.is_watertight),'extents_mm':t.extents.tolist(),'volume_cm3':float(t.volume/1000)}
report['reference_plan_intersection_mm3']=float((body^m3.Manifold.extrude(v.PLAN,100).translate((0,0,v.H0+.001))).volume())
report['cavity_envelope_intersection_mm3']=float((body^m3.Manifold.extrude(v.CAV,100).translate((0,0,v.H0+.001))).volume())
for z in [0.1,6,12,20,29.9,30.1,40,50,60]:
 sec=body.slice(z);report['sections'][str(z)]={'solid_area_mm2':sec.area(),'inside_reference_plan_mm2':(sec^v.PLAN).area()}
contact=body.slice(.1); polys=contact.to_polygons();p=np.concatenate(polys);hull=ConvexHull(p)
# Actual contact geometry hull, no assumption that every corner of a bounding box touches.
eq=hull.equations
com_xy=mesh.center_mass[:2]; mass_stand=mesh.volume/1000*1.24/1000
estimates=[]
for cx in [-5,5,15]:
 for cy in [-15,0,15]:
  combined=(3.2*np.array([cx,cy])+mass_stand*com_xy)/(3.2+mass_stand)
  distance=-(eq[:,:2]@combined+eq[:,2]);min_d=float(distance.min())
  estimates.append({'assumed_console_com_xy_mm':[cx,cy],'nearest_pivot_mm':min_d,'top_push_N':(3.2+mass_stand)*9.81*min_d/388,'tilt_deg':float(np.degrees(np.arctan(min_d/((3.2*209+mass_stand*mesh.center_mass[2])/(3.2+mass_stand)))))})
report['tipping']={'assumptions':'3.2kg console, CoM 179mm above base, console lift30mm, horizontal push at388mm, solid PLA density1.24g/cm3, rigid no-slip coupling. Not valid if console moves independently in loose cavity. No comparison to Sony stand.','scenarios':estimates}
# Geometric layer coverage: not an extrusion/toolpath simulation.
records=[]; previous=body.slice(.1)
for z in np.arange(.3,mesh.bounds[1,2],.2):
 sec=body.slice(float(z)); unsupported=sec-previous.offset(.2)
 floating=sum(1 for part in sec.decompose() if (part^previous).area()<1e-6)
 records.append({'z_mm':round(float(z),2),'beyond_45deg_support_area_mm2':float(unsupported.area()),'new_nonoverlapping_islands':floating})
 previous=sec
report['layer_screen']={'layer_height_mm':.2,'method':'Area outside preceding cross section expanded 0.2mm; no extrusion width, bridging, cooling or material model. New islands have zero direct overlap with prior layer; diagonal extrusion may still support them.','layers':len(records),'worst_layers':sorted(records,key=lambda a:a['beyond_45deg_support_area_mm2'],reverse=True)[:12],'sum_new_nonoverlapping_islands':sum(r['new_nonoverlapping_islands'] for r in records)}
(out/'layer_screen.json').write_text(json.dumps(records,indent=2))
# Model-derived support footprint, not a measurement of the physical console.
s=trimesh.load(Path(__file__).resolve().parents[3]/'references/console-model/PS5_Slim.glb')
g=s.geometry['unnamed_6']; section=g.section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
if section is not None:
 contours=[p[:,:2].tolist() for p in section.discrete if np.linalg.norm(p[0]-p[-1])<.01]
 core=m3.CrossSection(contours,m3.FillRule.EvenOdd)
 report['reference_core_contact']={'slice_console_z_mm':.5,'core_area_mm2':core.area(),'rib_top_overlap_mm2':(body.slice(29.9)^core).area(),'warning':'Fan-made core mesh section, not verified contact face. Holes and actual feet unknown.'}
report['nominal_features_mm']={'strand_triangle_circumradius':3.,'strand_circle_radius':1.9,'strand_square_side':3.5,'strand_X_arm_width':1.6,'strand_X_envelope':5.,'local_collar_max_scale':1.3,'under_console_ribs':v.RIB_T,'rim_band_height':v.RIM_BAND,'base_band_height':v.BASE_BAND,'reference_clearance':v.CLEAR}
(out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
