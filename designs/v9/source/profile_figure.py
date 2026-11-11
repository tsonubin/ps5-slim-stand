from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ps5-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,json
from shapely.geometry import Polygon
from veil_v9 import wire_profiles
out=Path(__file__).resolve().parents[1]/'output';fig,axes=plt.subplots(1,4,figsize=(12,3.5),facecolor='#f3f5fa');data=[]
for ax,name,p in zip(axes,['Triangle','Circle','Cross / X','Square'],wire_profiles()):
 poly=Polygon(p);ax.fill(p[:,0],p[:,1],color='#2c58b7');ax.set(xlim=(-3.5,3.5),ylim=(-3.5,3.5),aspect='equal',title=f'{name}\n{poly.area:.2f} mm²',xlabel='mm');ax.grid(alpha=.2);ax.set_axisbelow(True)
 # Polygon second moments about centroid, from signed Green-theorem sums.
 q=p-np.asarray(poly.centroid.coords)[0];x,y=q.T;xn,yn=np.roll(q,-1,axis=0).T;c=x*yn-xn*y;sign=np.sign(c.sum())
 Ixx=sign*np.sum((y*y+y*yn+yn*yn)*c)/12;Iyy=sign*np.sum((x*x+x*xn+xn*xn)*c)/12;Ixy=sign*np.sum((2*x*y+x*yn+xn*y+2*xn*yn)*c)/24
 data.append({'profile':name,'area_mm2':poly.area,'principal_second_moments_mm4':np.linalg.eigvalsh([[Ixx,-Ixy],[-Ixy,Iyy]]).tolist(),'nominal_X_arm_mm':1.6 if name=='Cross / X' else None})
fig.suptitle('THE STRAND CROSS-SECTIONS — cut across a wire, not through a mesh cell',fontsize=13)
fig.tight_layout(rect=(0,0,1,.9));fig.savefig(out/'strand_profiles.png',dpi=180)
(out/'strand_profiles.json').write_text(json.dumps(data,indent=2))
