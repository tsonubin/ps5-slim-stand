from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ps5-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
import numpy as np,trimesh,manifold3d as m3
out=Path(__file__).resolve().parents[1]/'output'
t=trimesh.load(out/'veil_v9_prototype.stl');b=m3.Manifold(m3.Mesh(np.float32(t.vertices),np.uint32(t.faces)))
fig,axs=plt.subplots(1,4,figsize=(12,7),facecolor='#f4f6fa')
def draw(ax,section,color):
 verts=[];codes=[]
 for p in section.to_polygons():
  verts.extend([*p,p[0]]);codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(p)-1)+[PlotPath.CLOSEPOLY])
 if verts:ax.add_patch(PathPatch(PlotPath(verts,codes),facecolor=color,edgecolor='none'))
for ax,z in zip(axs,[13.7,14.1,30.1,45.1]):
 prev=b.slice(z-.2);sec=b.slice(z);risk=sec-prev.offset(.2)
 draw(ax,prev.offset(.2),'#c3c9d3');draw(ax,sec,'#345caf');draw(ax,risk,'#ed493c')
 ax.set(xlim=(-85,100),ylim=(-130,130),aspect='equal',title=f'z = {z:.1f} mm\n{risk.area():.1f} mm² flagged',xlabel='X / mm');ax.set_ylabel('Y / mm');ax.grid(alpha=.15)
fig.suptitle('GEOMETRIC LAYER SCREEN — red extends beyond a 45° support envelope',fontsize=13)
fig.text(.5,.03,'0.2 mm sections. Gray: preceding layer + 0.2 mm. Blue: current layer.\nNot slicer toolpaths; bridging, extrusion width and material behavior are not simulated.',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.09,1,.94));fig.savefig(out/'layer_screen.png',dpi=160);plt.close(fig)
