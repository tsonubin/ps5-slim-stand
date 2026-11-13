"""Exterior-wall smoothness evidence for v15 versus v13 (analytic guides, not the triangulated mesh)."""
from pathlib import Path
import sys,json,importlib
import numpy as np
from scipy.signal import find_peaks
HERE=Path(__file__).resolve().parent
def load(name,folder):
 sys.path.insert(0,str(folder));m=importlib.import_module(name);sys.path.pop(0);return m
def significant(k,prom=.003):
 kk=np.tile(k,3);n=len(k);a,_=find_peaks(kk,prominence=prom);b,_=find_peaks(-kk,prominence=prom);return int(np.sum((a>=n)&(a<2*n))+np.sum((b>=n)&(b<2*n)))
def review(v):
 th=np.linspace(-np.pi,np.pi,7200,endpoint=False);out={'sections':{},'silhouettes':{}}
 for q in [0,.25,.5,.75,1]:
  r=v.SR(th)+(v.SB(th)-v.SR(th))*q*q;d=v.SR(th,1)+(v.SB(th,1)-v.SR(th,1))*q*q;dd=v.SR(th,2)+(v.SB(th,2)-v.SR(th,2))*q*q
  k=(r*r+2*d*d-r*dd)/(r*r+d*d)**1.5;ds=np.sqrt(r*r+d*d)*2*np.pi/len(th);s=np.sign(k)
  out['sections'][f'q={q}']={'inflections':int(np.sum(s!=np.roll(s,1))),'inward_curving_length_mm':float(ds[k<0].sum()),'min_curvature_per_mm':float(k.min()),'tightest_radius_mm':float(1/k.max()),'significant_curvature_extrema':significant(k)}
 # Orthographic silhouettes from 12 azimuths: outermost wall point per height, both edges.
 worst=0;count=0
 for az in np.arange(0,180,15):
  n=np.array([np.cos(np.radians(az)),np.sin(np.radians(az))]);zf=np.linspace(.02,.98,197);edge=[]
  for f in zf:
   h=v.SH(th);z=f*h;q=1-f;r=v.SR(th)+(v.SB(th)-v.SR(th))*q*q;w=(r[:,None]*np.c_[np.cos(th),np.sin(th)])@n;i=np.argmax(w);j=np.argmin(w);edge.append((w[i],z[i],w[j],z[j]))
  e=np.array(edge);infl=0
  for col in (0,2):
   w=e[:,col];zz=e[:,col+1];d2=np.gradient(np.gradient(w,zz),zz);sg=np.sign(d2[3:-3]);sg=sg[np.abs(d2[3:-3])>1e-4];infl+=int(np.sum(sg[1:]!=sg[:-1]))
  out['silhouettes'][f'{az:g}deg']={'profile_inflections':infl};count+=infl
 out['silhouette_inflections_total_12_views']=count
 xy=np.c_[8+v.SB(th)*np.cos(th),v.SB(th)*np.sin(th)];rim=np.c_[8+v.SR(th)*np.cos(th),v.SR(th)*np.sin(th)]
 out['base_size_mm']=np.ptp(xy,axis=0).round(2).tolist();out['rim_size_mm']=np.ptp(rim,axis=0).round(2).tolist()
 g=v.SR(v.TH)-v.R_C;out['rim_to_cavity_gap_mm']=[float(g.min()),float(g.max())]
 delta=v.SB(th)-v.SR(th);out['flare_mm']=[float(delta.min()),float(delta.max())];out['max_wall_lean_from_vertical_deg']=float(np.degrees(np.arctan(2*delta/v.SH(th))).max())
 return out
rep={'scope':'Analytic exterior guide surface r(theta,z). Horizontal sections at 5 heights and silhouettes from 12 azimuths. Does not certify aperture edges or the triangulated Boolean result.',
 'v13':review(load('veil_v13',HERE.parent/'baseline_v13/source')),'v15':review(load('veil_v15',HERE))}
(HERE.parent/'analysis/wall_smoothness.json').write_text(json.dumps(rep,indent=2))
for ver in ['v13','v15']:
 r=rep[ver];print(ver,'base',r['base_size_mm'],'rim',r['rim_size_mm'],'gap',np.round(r['rim_to_cavity_gap_mm'],2),'flare',np.round(r['flare_mm'],2),'lean',round(r['max_wall_lean_from_vertical_deg'],1),'silhouette inflections',r['silhouette_inflections_total_12_views'])
 for k,x in r['sections'].items():print('  ',k,x)
