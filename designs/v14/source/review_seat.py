"""Seat-contact evidence for v14 versus v13 against the fan-made reference core (not a scan)."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh,manifold3d as m3
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3];W=3.2*9.81
scene=trimesh.load(ROOT/'references/console-model/PS5_Slim.glb');core=scene.geometry['unnamed_6'];cover=scene.geometry['unnamed_4']
n=core.face_normals;c=core.triangles_center;sel=(n[:,2]<-.95)&(c[:,2]<.05)
foot=max(unary_union([Polygon(t[:,:2]).buffer(1e-4) for t in core.triangles[sel]]).buffer(-1e-4).geoms,key=lambda g:g.area)
def seat(stl):
 m=trimesh.load(stl);nn=m.face_normals;cc=m.triangles_center;ss=(nn[:,2]>.99)&(np.abs(cc[:,2]-30)<.02)
 land=unary_union([Polygon(t[:,:2]).buffer(1e-4) for t in m.triangles[ss]]).buffer(-1e-4);con=land.intersection(foot)
 parts=[g for g in getattr(con,'geoms',[con]) if g.area>.5];out={'stl_sha256':hashlib.sha256(Path(stl).read_bytes()).hexdigest(),'flat_seat_area_mm2':float(land.area),'contact_area_on_core_mm2':float(con.area),'mean_pressure_MPa_at_3p2kg':float(W/con.area),'patches':[]}
 for g in sorted(parts,key=lambda g:-g.area):
  r=g.minimum_rotated_rectangle;xy=np.array(r.exterior.coords);e=sorted([np.linalg.norm(xy[0]-xy[1]),np.linalg.norm(xy[1]-xy[2])])
  out['patches'].append({'area_mm2':float(g.area),'centroid_xy_mm':np.round(g.centroid.coords[0],2).tolist(),'bounding_length_mm':float(e[1]),'bounding_width_mm':float(e[0]),'max_inscribed_width_mm':float(2*max(d for d in np.arange(0,12,.05) if not g.buffer(-d).is_empty)),'min_distance_to_core_edge_mm':float(g.distance(foot.exterior)),'fully_on_core':bool(foot.contains(g.buffer(-.01)))})
 hull=con.convex_hull;com=Point(core.centroid[:2]);out['reference_core_centroid_xy_mm']=np.round(core.centroid[:2],2).tolist();out['centroid_inside_contact_hull']=bool(hull.contains(com));out['centroid_margin_to_hull_edge_mm']=float(hull.exterior.distance(com))
 # Rigid 3-point worst case: load carried by the three patches nearest the centroid on 10% of their area.
 body=m3.Manifold(m3.Mesh(np.float32(m.vertices),np.uint32(m.faces)))
 slot=m3.Manifold.extrude(m3.CrossSection([np.asarray(foot.exterior.coords)[:-1][::-1]]).offset(12)-m3.CrossSection([np.asarray(foot.exterior.coords)[:-1][::-1]]),float(cover.bounds[0][2])).translate((0,0,30))
 out['stand_volume_inside_core_to_cover_slot_mm3']=float((body^slot).volume())
 V=m.vertices;inside=np.array([foot.contains(Point(p[:2])) for p in V[V[:,2]>28]]);far=np.array([land.distance(Point(p[:2]))>2.5 for p in V[V[:,2]>28]]);out['highest_stand_point_under_core_away_from_seat_lands_mm']=float(V[V[:,2]>28][inside&far][:,2].max()) if (inside&far).any() else None
 return out
rep={'scope':'Flat stand faces at z=30 intersected with the flat bottom of the fan-made reference core. Nominal geometry; no solved contact, no hardware measurement.','assumed_mass_kg':3.2,'reference_core_flat_bottom_area_mm2':float(foot.area),'reference_cover_lowest_edge_above_core_bottom_mm':float(cover.bounds[0][2]),
 'v13':seat(ROOT/'designs/v13/output/veil_v13_prototype.stl'),'v14':seat(ROOT/'designs/v14/output/veil_v14_prototype.stl')}
(ROOT/'designs/v14/analysis/seat_contact.json').write_text(json.dumps(rep,indent=2))
for k in ['v13','v14']:
 r=rep[k];print(k,'contact %.1f mm2, mean %.4f MPa, COM inside %s margin %.1f, slot volume %.1f, highest non-land point under core %s'%(r['contact_area_on_core_mm2'],r['mean_pressure_MPa_at_3p2kg'],r['centroid_inside_contact_hull'],r['centroid_margin_to_hull_edge_mm'],r['stand_volume_inside_core_to_cover_slot_mm3'],r['highest_stand_point_under_core_away_from_seat_lands_mm']))
 for p in r['patches']:print('   ',p)
