"""Read-only dense path and sampled sweep clearance screen before expensive CSG."""
from pathlib import Path
import numpy as np,json
from shapely.geometry import Polygon
from shapely import contains_xy,distance,points
import veil_v11 as g
root=Path(__file__).resolve().parents[1];poly=Polygon(max(g.CAV.to_polygons(),key=len));lo=np.full(3,np.inf);hi=-lo;penetrations=[];outside=[];records=[]
def sweep_vertices(p,r,closed=False):
 global lo,hi
 t=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0) if closed else np.gradient(p,axis=0);t/=np.linalg.norm(t,axis=1)[:,None]
 radial=np.c_[p[:,:2]-g.CENTER,np.zeros(len(p))];radial-=np.sum(radial*t,axis=1)[:,None]*t;radial/=np.linalg.norm(radial,axis=1)[:,None];normal=np.cross(t,radial);a=np.linspace(0,2*np.pi,48,endpoint=False)
 r=np.broadcast_to(r,len(p));q=p[:,None,:]+r[:,None,None]*(np.cos(a)[None,:,None]*radial[:,None,:]+np.sin(a)[None,:,None]*normal[:,None,:]);q=q.reshape(-1,3)
 lo=np.minimum(lo,q.min(0));hi=np.maximum(hi,q.max(0));q=q[q[:,2]>30.001]
 inside=contains_xy(poly,q[:,0],q[:,1]);d=distance(points(q[:,:2]),poly.boundary);penetrations.extend(d[inside]);outside.extend(d[~inside])
def curvature(p,param,r,label):
 dp=np.gradient(p,param,axis=0,edge_order=2);ddp=np.gradient(dp,param,axis=0,edge_order=2);sp=np.linalg.norm(dp,axis=1);k=np.linalg.norm(np.cross(dp,ddp),axis=1)/sp**3
 records.append({'curve':label,'minimum_speed_mm_per_parameter':float(sp[2:-2].min()),'minimum_curvature_radius_mm':float(1/k[2:-2].max()),'max_radius_times_curvature':float(np.max((r*k)[2:-2]))})
th=np.linspace(-np.pi,np.pi,1440,endpoint=False);dense=np.linspace(-np.pi,np.pi,21601)
for top in [False,True]:
 r=2.4 if top else 3;sweep_vertices(g.ring_curve(th,top),r,True);curvature(g.ring_curve(dense,top),dense,r,'top_ring' if top else 'base_ring')
for i,f in enumerate([.36,.69]):
 fun=lambda a:g.surface(a,f+.12*np.sin(a+i*1.7)+.065*np.cos(2*a-.4))
 sweep_vertices(fun(th),1.65,True);curvature(fun(dense),dense,1.65,f'contour_{i}')
v=np.linspace(0,1,10001);signed=[]
for direction,count in [(1,37),(-1,29)]:
 for k in range(count):
  p,a=g.wire_curve(v,direction,k,count);curvature(p,v,g.wire_radius(v),f'wire_{direction}_{k}');signed.append(float(np.min(direction*np.gradient(a,v))))
  vv=np.linspace(0,1,401);q,_=g.wire_curve(vv,direction,k,count);sweep_vertices(q,g.wire_radius(vv))
report={'scope':'Source sweep vertices and densely sampled centerlines only; not final Boolean/SDF mesh or physical validation','preclip_bounds_mm':[lo.tolist(),hi.tolist()],'desk_clipped_extents_mm':[float(hi[0]-lo[0]),float(hi[1]-lo[1]),float(hi[2])],'above_seat_vertices_inside_cavity':len(penetrations),'max_sampled_cavity_penetration_mm':float(max(penetrations,default=0)),'minimum_sampled_outside_cavity_distance_mm':float(min(outside,default=0)),'minimum_signed_wire_theta_derivative':min(signed),'max_radius_times_curvature':max(r['max_radius_times_curvature'] for r in records),'curve_records':records,'limitations':'Discrete profile vertices/paths do not guarantee face-interior clearance or global self-intersection freedom; final export needs separate checks.'}
(root/'analysis/preflight.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='curve_records'},indent=2));print('Worst curves',sorted(records,key=lambda r:r['max_radius_times_curvature'],reverse=True)[:5])
assert not penetrations and report['max_radius_times_curvature']<1 and min(signed)>.4
