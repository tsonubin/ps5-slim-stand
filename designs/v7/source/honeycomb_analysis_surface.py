from pathlib import Path
import numpy as np
import veil_v7 as v
# Reconstruct the same honeycomb layout using planar CSG rather than many tiny
# loft segments, to avoid coincident-facet artifacts in the analysis mesh.
radius=22.;edges={}
for col in range(-4,5):
 for row in range(-5,6):
  c=np.array([8+1.5*radius*col,np.sqrt(3)*radius*(row+.5*(col%2))])
  pts=c+radius*np.c_[np.cos(np.arange(6)*np.pi/3),np.sin(np.arange(6)*np.pi/3)]
  for p,q in zip(pts,np.roll(pts,-1,axis=0)):
   if abs((p+q)[0]/2)>110 or abs((p+q)[1]/2)>150:continue
   edges[tuple(sorted((tuple(np.round(p,5)),tuple(np.round(q,5)))))]=(p,q)
rects=[];cuts=[]
for p,q in edges.values():
 u=(q-p)/np.linalg.norm(q-p);n=np.array([-u[1],u[0]])*v.RIB_T/2
 rects.append([p-n,q-n,q+n,p+n]);h=min(12,radius*.45)
 cs=v.CS([[(-h/1.5,-1),(h/1.5,-1),(h/1.5,0),(0,h),(-h/1.5,0)]])
 cut=v.Manifold.extrude(cs,v.RIB_T+2).rotate((90,0,0)).translate((0,(v.RIB_T+2)/2,0)).rotate((0,0,np.degrees(np.arctan2(u[1],u[0])))).translate((*((p+q)/2),0));cuts.append(cut)
w=v.Manifold.extrude(v.CS(rects,v.m3.FillRule.Positive),30)-v.Manifold.batch_boolean(cuts,v.m3.OpType.Add)
# Constant reference-plan boundary keeps the comparison focused on the core ribs.
plan=v.CS([(v.CENTER+v.r_out(30)[:,None]*v.U).tolist()]);w=w^v.Manifold.extrude(plan,30)
parts=w.decompose();main=max(parts,key=lambda p:p.volume());print('CSG honeycomb',w.volume(),'minor excluded',sum(p.volume() for p in parts)-main.volume(),flush=True)
t=v.to_trimesh(main,.002);out=Path(__file__).resolve().parents[1]/'analysis/honeycomb_csg.stl';t.export(out)
