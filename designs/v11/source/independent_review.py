"""Independent geometry/mathematical screens. Does not build or modify CAD or run FEA."""
from pathlib import Path
import sys,json,ast,hashlib
import numpy as np
import trimesh,manifold3d as m3
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'source'))
import veil_v11 as g
report={'scope':'Independent sampled geometry and algebra review; not physical validation or an exact G1 certificate'}
# Execute the ACTUAL scalar assignments from the blend module, not a rewritten formula.
tree=ast.parse((root/'source/junction_blend.py').read_text())
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='junction_patches')
assignments=[x for x in ast.walk(fn) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('h','f') for t in x.targets)]
assignments=sorted(assignments,key=lambda a:a.lineno)[:2]
assert [a.targets[0].id for a in assignments]==['h','f']
code=compile(ast.fix_missing_locations(ast.Module(body=assignments,type_ignores=[])),'actual_blend_assignments','exec')
def field(a,b,k):
 ns={'np':np,'d1':a,'d2':b,'k':k};exec(code,ns);return ns['f']
k=.85;eps=1e-6
slopes={}
for a in [-k,0,k]:
 slopes[str(a)]={'left':float((field(a,0,k)-field(a-eps,0,k))/eps),'right':float((field(a+eps,0,k)-field(a,0,k))/eps)}
for a,target in [(-k,1.),(0,.5),(k,0.)]:
 assert abs(slopes[str(a)]['left']-target)<1e-5 and abs(slopes[str(a)]['right']-target)<1e-5
rng=np.random.default_rng(17);a=rng.uniform(-5,5,100000);b=rng.uniform(-5,5,100000);kk=rng.uniform(.001,k,100000);f=field(a,b,kk);offset=np.minimum(a,b)-f
assert np.max(abs(field(a,b,kk)-field(b,a,kk)))<1e-12
assert np.min(offset)>-1e-12 and np.max(offset-kk/4)<1e-12
assert np.min(field(a+eps,b,kk)-f)>-1e-12 and np.min(field(a,b+eps,kk)-f)>-1e-12
inactive=abs(a-b)>=kk;assert np.max(abs(f[inactive]-np.minimum(a,b)[inactive]))<1e-12
assert np.max(abs(field(a,b,0)-np.minimum(a,b)))<1e-12
report['smooth_min']={'source_assignments':ast.unparse(ast.Module(body=assignments,type_ignores=[])),'derivatives_d1_d2zero':slopes,'random_samples':len(a),'symmetry_monotonicity_additive_bound_inactive_and_zero_blend':'passed','maximum_offset_mm':k/4,'limitations':'C1 algebra in smooth input distance fields only. Approximate polyline fields, clipping, Boolean union and triangulation can introduce surface discontinuities.'}
# Dense sampling of independent parameter values, beyond construction tessellation.
v=np.linspace(0,1,10001);records=[];angle=[];der=[];speedmin=[];radiusmin=[];patherr=[]
guide=np.load(root/'output/guide_curves.npz');ident=guide['identities']
for index,(direction,k,count) in enumerate(ident):
 p,th=g.wire_curve(v,int(direction),int(k),int(count));dp=np.gradient(p,v,axis=0,edge_order=2);ddp=np.gradient(dp,v,axis=0,edge_order=2)
 speed=np.linalg.norm(dp,axis=1);curvature=np.linalg.norm(np.cross(dp,ddp),axis=1)/speed**3;ratio=g.wire_radius(v)*curvature
 i=np.argmax(ratio[2:-2])+2
 records.append({'direction':int(direction),'wire_index':int(k),'max_radius_times_curvature':float(ratio[i]),'at_parameter':float(v[i]),'minimum_curvature_radius_mm':float(1/curvature[2:-2].max())})
 der.append(float(np.min(direction*np.gradient(th,v))));speedmin.append(float(speed.min()));radiusmin.append(float(g.wire_radius(v).min()))
 for j,top in [(0,False),(-1,True)]:
  d=(g.ring_curve(th[j]+1e-5,top)-g.ring_curve(th[j]-1e-5,top))/(2e-5)
  angle.append(float(np.degrees(np.arccos(np.clip(abs(np.dot(d,dp[j]))/np.linalg.norm(d)/np.linalg.norm(dp[j]),0,1)))))
 built,_=g.wire_curve(guide['v'],int(direction),int(k),int(count));patherr.append(float(np.max(abs(built-guide['points'][index]))))
assert min(der)>.4 and max(x['max_radius_times_curvature'] for x in records)<1 and max(patherr)<1e-8
report['centerlines']={'strands':len(ident),'samples_per_strand':len(v),'minimum_signed_theta_derivative':min(der),'minimum_speed_mm_per_parameter':min(speedmin),'minimum_curvature_radius_mm':min(x['minimum_curvature_radius_mm'] for x in records),'max_radius_times_curvature':max(x['max_radius_times_curvature'] for x in records),'max_endpoint_tangent_mismatch_degrees':max(angle),'maximum_difference_from_saved_sweep_points_mm':max(patherr),'nominal_minimum_diameter_mm':2*min(radiusmin),'records':records,'limitations':'Sampled local tube regularity, not a global self-intersection proof. Endpoint centerline tangency does not prove exported surface G1 continuity.'}
# Exact fit envelope equality, plus independent read-back of final files when present.
sys.path.insert(0,str(root.parent/'v10/source'));import veil_v10 as old
report['cavity_source']={'outline_unchanged':g.OL==old.OL,'v11_minus_v10_area_mm2':float((g.CAV-old.CAV).area()),'v10_minus_v11_area_mm2':float((old.CAV-g.CAV).area()),'clearance_mm':g.CLEAR,'seat_height_mm':g.H0}
assert report['cavity_source']['outline_unchanged'] and report['cavity_source']['v11_minus_v10_area_mm2']==0 and report['cavity_source']['v10_minus_v11_area_mm2']==0
final=root/'output/veil_v11_prototype.stl'
if final.exists() and (root/'output/PRINT_TEST_v11_section.stl').exists():
 def load(name):
  mesh=trimesh.load(root/'output'/name);return mesh,m3.Manifold(m3.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)))
 t,b=load(final.name);under,um=load('undercroft_sleek.stl');coupon,cm=load('PRINT_TEST_v11_section.stl')
 assert t.is_watertight and t.is_winding_consistent and t.body_count==1 and coupon.is_watertight and coupon.body_count==1
 clip=m3.Manifold.cube((58,36,80)).translate((22,34,0))
 report['final_mesh']={'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'components':int(t.body_count),'extents_mm':t.extents.tolist(),'volume_mm3':float(t.volume),'reference_intersection_mm3':float((b^m3.Manifold.extrude(g.PLAN,100).translate((0,0,g.H0+.001))).volume()),'clearance_envelope_intersection_mm3':float((b^m3.Manifold.extrude(g.CAV,100).translate((0,0,g.H0+.001))).volume())}
 report['coupon']={'extents_mm':coupon.extents.tolist(),'volume_mm3':float(coupon.volume),'components':int(coupon.body_count),'understructure_volume_in_clip_mm3':float((um^clip).volume()),'limitations':'Cut specimen includes actual web and underside but is not a complete structural/printing qualification.'}
else:report['final_mesh']={'status':'complete export set not yet available; source/path review only'}
(root/'analysis').mkdir(exist_ok=True)
(root/'analysis/independent_review.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='centerlines'},indent=2))
print('Centerline summary',json.dumps({k:v for k,v in report['centerlines'].items() if k!='records'}))
