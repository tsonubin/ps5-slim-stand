"""Check the v15 seat against the scanned console underside and draw output/seat_vs_underside.png.
Writes analysis/underside_review.json: what each pad land sits under, clearance of every other part of the stand
to the console, what lies below the vent row, and the stability margin of the support polygon."""
import json
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import Polygon,Point,MultiPoint,box
from shapely.ops import unary_union
from PIL import Image
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
import veil_v15 as g
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];U=json.loads((ROOT/'references/console-scan/underside.json').read_text());G=np.load(ROOT/'references/console-scan/underside_grid.npz')
m=trimesh.load(R/'output/veil_v15_prototype.stl');x,y=G['x'],G['y'];XX,YY=np.meshgrid(x,y);cover,black,mask=G['cover'],G['black'],G['mask']
def polys(z):
 s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1]);pl,T=s.to_2D();out=[]
 for p in pl.polygons_full:
  e=trimesh.transform_points(np.c_[np.asarray(p.exterior.coords),np.zeros(len(p.exterior.coords))],T)[:,:2];hs=[trimesh.transform_points(np.c_[np.asarray(h.coords),np.zeros(len(h.coords))],T)[:,:2] for h in p.interiors];out.append(Polygon(e,hs))
 return unary_union(out)
lands=polys(29.9);ribs=polys(28.5);cav=Polygon(max(g.CAV.to_polygons(),key=len));inside=lambda geom:geom.intersection(cav.buffer(-.2))
lands_in=inside(lands);rib_in=inside(ribs)
# top surface of the stand inside the cavity, by ray casting down from z=31
ok=mask[::8,::8];px=np.c_[XX[::8,::8][ok],YY[::8,::8][ok]];loc,ri,_=m.ray.intersects_location(np.c_[px,np.full(len(px),31.)],np.tile([0,0,-1.],(len(px),1)),multiple_hits=False)
top=np.full(len(px),0.);top[ri]=loc[:,2];step=np.where(cover[::8,::8][ok],0.,np.where(black[::8,::8][ok],2.0,0.))   # console surface above the seat plane: covers 0, black base >= 2 mm (scan: 2-3)
gap=g.H0+step-top;isb=black[::8,::8][ok]
vr=box(g.VENT_ROW['x'][0],g.VENT_ROW['y'][0],g.VENT_ROW['x'][1],g.VENT_ROW['y'][1]);slots=[box(s['x'][0],s['y'][0],s['x'][1],s['y'][1]) for s in U['vent_slots']]
under=[];
for z in [29.5,28.5,26,22]:
 q=polys(z).intersection(vr);under.append({'z_mm':z,'solid_area_under_vent_row_mm2':float(q.area),'solid_area_under_slots_mm2':float(sum(q.intersection(s).area for s in slots))})
pads=[]
for cx,cy in g.PADS:
 land=max((q for q in getattr(lands,'geoms',[lands]) if q.distance(Point(cx,cy))<8),key=lambda q:q.area);sel=np.array([land.contains(Point(a,b)) for a,b in px])
 c=cover[::8,::8][ok][sel].mean() if sel.any() else 0.;pads.append({'centre_xy_mm':[cx,cy],'land_area_mm2':float(land.area),'fraction_of_land_under_a_cover':float(c),'nearest_vent_slot_mm':float(min(land.distance(s) for s in slots))})
hull=MultiPoint(g.PADS).convex_hull;c0=Point(8,0)
rep={'scope':'Nominal v15 CAD against the registered phone scan of one CFI-2009. Plan positions are good to about 2-3 mm; the step between covers and black base (2-3 mm in the scan) is smoothed by the 2 mm scan mesh.',
 'pads':pads,'land_area_total_mm2':float(sum(p['land_area_mm2'] for p in pads)),'under_vent_row':under,
 'vent_slots':{'count':len(slots),'open_area_mm2':float(sum(s.area for s in slots))},
 'min_gap_stand_to_black_base_mm_if_step_is_2mm':float(gap[isb].min()),'min_gap_stand_to_black_base_at_xy':px[isb][gap[isb].argmin()].round(1).tolist(),
 'support_polygon':{'corners_xy_mm':[list(p) for p in g.PADS],'area_mm2':float(hull.area),'footprint_centre_xy_mm':[8,0],'margin_from_footprint_centre_to_edge_mm':float(hull.exterior.distance(c0)),'centre_inside':bool(hull.contains(c0))}}
(R/'analysis/underside_review.json').write_text(json.dumps(rep,indent=1));print(json.dumps(rep,indent=1))
I=np.asarray(Image.open(ROOT/'references/console-scan/underside_texture.png'))[::-1];ext=[x[0],x[-1],y[0],y[-1]]
fig,ax=plt.subplots(1,2,figsize=(15,13))
for a,(old,title) in zip(ax,[(True,'v14 (withdrawn): pads and rib under the vent row'),(False,'v15: lands under the covers, vent row clear')]):
 a.imshow(I,origin='lower',extent=ext)
 if old:
  for cx,cy in [(-16.5,44),(16.5,44),(-11.5,-44),(11.5,-44)]:a.add_patch(plt.Rectangle((cx-5.3,cy-10.8),10.6,21.6,fc='#ff3b3b88',ec='#ff3b3b',lw=1.5))
  yy=np.linspace(-110,110,200);s0=np.sin(np.pi*yy/250);c0_=np.cos(np.pi*yy/250)
  for sg in (-1,1):a.plot(sg*(14+4.76*s0+4*(c0_-np.cos(np.pi*44/250))),yy,color='#6fd36f',lw=2.5)
  t=np.linspace(-1,1,181)
  for sg in (-1,1):a.plot(8+70*t,sg*(37+8*np.cos(np.pi*t/2)),color='#6fd36f',lw=2.5)
 else:
  from matplotlib.path import Path as MP;from matplotlib.patches import PathPatch
  for q in getattr(rib_in,'geoms',[rib_in]):
   rings=[np.asarray(q.exterior.coords)]+[np.asarray(r.coords) for r in q.interiors]
   a.add_patch(PathPatch(MP(np.vstack(rings),np.concatenate([[MP.MOVETO]+[MP.LINETO]*(len(r)-2)+[MP.CLOSEPOLY] for r in rings])),fc='#6fd36fbb',ec='#6fd36f',lw=.6))
  for q in getattr(lands_in,'geoms',[lands_in]):a.fill(*q.exterior.xy,fc='#ff3b3b99',ec='#ff3b3b',lw=1.5)
 for s in slots:a.add_patch(plt.Rectangle((s.bounds[0],s.bounds[1]),s.bounds[2]-s.bounds[0],s.bounds[3]-s.bounds[1],fill=False,ec='#ffb000',lw=1))
 a.plot(*cav.exterior.xy,color='#9ad',lw=1,ls='--');a.set_xlim(-55,68);a.set_ylim(-118,118);a.set_xticks(range(-50,61,10));a.set_yticks(range(-110,111,10));a.grid(lw=.3,color='#777');a.set_title(title);a.set_xlabel('x / mm (+x disc-drive side)');a.set_ylabel('y / mm (+y rear)')
fig.suptitle('Scanned underside of a real CFI-2009, seen from above through the console. Red = seat lands, green = ribs (1 mm below the seat), orange = vent slots, dashed = cavity wall',fontsize=11)
fig.savefig(R/'output/seat_vs_underside.png',dpi=85,bbox_inches='tight')
