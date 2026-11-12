"""Analytic guide continuity and comparison; not finished-Boolean G2 certification."""
from pathlib import Path
import json
import numpy as np
import veil_v13 as v
root=Path(__file__).resolve().parents[1]
th=np.linspace(-np.pi,np.pi,14401)
def curve(r,h):
 rr=r(th);d=r(th,1);dd=r(th,2);c=np.cos(th);s=np.sin(th)
 xyz=np.c_[8+rr*c,rr*s,h(th)]
 first=np.c_[d*c-rr*s,d*s+rr*c,h(th,1)]
 second=np.c_[dd*c-2*d*s-rr*c,dd*s+2*d*c-rr*s,h(th,2)]
 k=np.linalg.norm(np.cross(first,second),axis=1)/np.linalg.norm(first,axis=1)**3
 return xyz,first,second,k
zero=lambda t,nu=0:np.zeros_like(t)
report={'scope':'Analytic outer upper/lower perimeter guides. C-infinity finite Fourier series; triangulation, section transitions and aperture boundaries are not certified globally G2.','height_intent':'Nearly level upper rim, planar lower contact ring; preserve irregular cell web and overall lower silhouette.','guides':{}}
for label,r,h,oldr,oldh in [('upper',v.SR,v.SH,v.spline(v.legacy_rim),v.spline(v.legacy_height)),('lower',v.SB,zero,v.spline(v.legacy_base),zero)]:
 x,d,dd,k=curve(r,h);old=curve(oldr,oldh)
 report['guides'][label]={'z_range_mm':[float(x[:,2].min()),float(x[:,2].max())],'previous_z_range_mm':[float(old[0][:,2].min()),float(old[0][:,2].max())],'maximum_plan_change_mm':float(np.linalg.norm(x[:,:2]-old[0][:,:2],axis=1).max()),'maximum_curvature_per_mm':float(k.max()),'previous_maximum_curvature_per_mm':float(old[3].max()),'max_adjacent_curvature_difference_at_14400_segments':float(np.max(np.abs(np.diff(k)))),'seam_position_error_mm':float(np.linalg.norm(x[0]-x[-1])),'seam_first_derivative_error':float(np.linalg.norm(d[0]-d[-1])),'seam_second_derivative_error':float(np.linalg.norm(dd[0]-dd[-1]))}
np.savez_compressed(root/'output/guide_samples.npz',theta=th,upper=curve(v.SR,v.SH)[0],lower=curve(v.SB,zero)[0])
(root/'analysis/guide_continuity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
