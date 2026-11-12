"""Verify the polynomial blending algebra, not geometric/physical safety."""
from pathlib import Path
import json
import numpy as np
k=.85
def field(a,b):
    h=np.clip(.5+.5*(b-a)/k,0,1)
    return (1-h)*b+h*a-k*h*(1-h)
eps=1e-6
left=(field(0,0)-field(-eps,0))/eps
right=(field(eps,0)-field(0,0))/eps
x=np.linspace(-2,2,10001)
assert abs(left-.5)<1e-5 and abs(right-.5)<1e-5
assert np.max(np.abs(field(x,0)-field(0,x)))<1e-14
assert np.max(np.abs(field(x[np.abs(x)>=k],0)-np.minimum(x[np.abs(x)>=k],0)))<1e-14
assert abs(field(0,0)+k/4)<1e-14
report={'scope':'Polynomial smooth-min formula only; not geometry continuity certification','k_mm':k,'equal_distance_left_derivative':float(left),'equal_distance_right_derivative':float(right),'maximum_distance_offset_mm':k/4,'symmetry_and_inactive_region_passed':True}
(Path(__file__).resolve().parents[1]/'output/junction_field_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
