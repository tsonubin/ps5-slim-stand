"""Plan-view projections from actual final meshes; no console scaling."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/ps5-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,trimesh
from scipy.spatial import ConvexHull
root=Path(__file__).resolve().parents[3];out=root/'designs/v8/output'
fig,ax=plt.subplots(figsize=(8,10),facecolor='#f6f8fc');ax.set_facecolor('#f6f8fc')
rows=[]
for name,color in [('v7','#8997af'),('v8','#3166db')]:
 m=trimesh.load(root/f'designs/{name}/output/veil_{name}_prototype.stl');p=m.vertices[:,:2];p=p[ConvexHull(p).vertices];p=np.vstack([p,p[0]])
 ax.fill(*p.T,color=color,alpha=.13);ax.plot(*p.T,color=color,lw=2,label=f'{name}: {m.extents[0]:.1f} × {m.extents[1]:.1f} mm')
 rows.append({'version':name,'extents_mm':m.extents.tolist(),'volume_cm3':m.volume/1000,'projected_convex_hull_mm2':ConvexHull(m.vertices[:,:2]).volume})
import veil_v8 as v
for p in v.CAV.to_polygons():
 p=np.vstack([p,p[0]]);ax.plot(*p.T,color='#162b46',lw=1.5,linestyle='--',label='Unchanged reference cavity')
ax.set(aspect='equal',xlabel='X / mm',ylabel='Y / mm',title='Reduced desk footprint / actual mesh envelope')
ax.grid(alpha=.18);ax.legend(loc='upper left',fontsize=10)
fig.text(.12,.025,'Outer contours are convex hulls of the mesh projection.\nCavity is reference-derived; physical fit and vent clearance remain unverified.',fontsize=9,color='#43516a')
fig.tight_layout(rect=[0,.065,1,1]);fig.savefig(out/'footprint_comparison.png',dpi=170);plt.close(fig)
(out/'footprint_comparison.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
