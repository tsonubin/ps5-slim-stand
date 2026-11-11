from pathlib import Path
import numpy as np,pyvista as pv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
p=R/'stand_1p5mm_port0.npz'
d=np.load(p);t=d['t'];a=d['field'];x,y,z=[d[k] for k in ['x','y','z']];v=a[...,1:];speed=np.linalg.norm(v,axis=-1);speed[t==0]=np.nan
fig,axs=plt.subplots(1,2,figsize=(13,6),layout='constrained')
k=np.argmin(abs(z-12));j=np.argmin(abs(y));mx=np.nanmax(speed)
im=axs[0].pcolormesh(x,y,speed[k]/mx,vmin=0,vmax=1,cmap='turbo',shading='nearest');axs[0].contour(x,y,t[k]==0,levels=[.5],colors='gray',linewidths=.5);axs[0].quiver(x[::5],y[::5],v[k,::5,::5,0],v[k,::5,::5,1],color='white',scale=0.00013,width=.003);axs[0].set(title=f'Horizontal section z={z[k]:g} mm',xlabel='X (mm)',ylabel='Y (mm)',aspect='equal')
axs[1].pcolormesh(x,z,speed[:,j]/mx,vmin=0,vmax=1,cmap='turbo',shading='nearest');axs[1].contour(x,z,t[:,j]==0,levels=[.5],colors='gray',linewidths=.5);axs[1].quiver(x[::4],z[::2],v[::2,j,::4,0],v[::2,j,::4,2],color='white',scale=.00012,width=.003);axs[1].set(title='Central vertical section',xlabel='X (mm)',ylabel='Z (mm)',aspect='equal');fig.colorbar(im,ax=axs,label='Speed / maximum speed in this hypothetical case',shrink=.6)
fig.suptitle('V13 capped-channel flow screen — solid desktop, hypothetical central suction port\nNot a PS5 vent map, fan operating point or temperature prediction',fontsize=12);fig.savefig(R/'flow_sections.png',dpi=160);plt.close(fig)
g=pv.ImageData(dimensions=(len(x),len(y),len(z)),spacing=(x[1]-x[0],y[1]-y[0],z[1]-z[0]),origin=(x[0],y[0],z[0]));g['velocity']=v.reshape(-1,3);g['relative_speed']=np.nan_to_num(speed/mx).ravel()
# Seeds inside the hypothetical top port; integrate backwards toward ambient reservoirs.
ang=np.linspace(0,2*np.pi,24,endpoint=False);pts=np.vstack([np.c_[rad*np.cos(ang),rad*np.sin(ang),np.full(len(ang),27)] for rad in [3,7,11]])
lines=g.streamlines_from_source(pv.PolyData(pts),vectors='velocity',integration_direction='backward',initial_step_length=.3,max_length=250,terminal_speed=1e-9,max_steps=5000)
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import trimesh,manifold3d as m3
fig=plt.figure(figsize=(12,9));ax=fig.add_subplot(projection='3d');ax.set_facecolor('#ecf0f4')
mesh=trimesh.load(R.parent/'output/veil_v13_prototype.stl');body=m3.Manifold(m3.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)))
for hh in [1,7,14,21,28,35,39]:
 for poly in body.slice(hh).to_polygons():
  pp=np.vstack([poly,poly[0]]);ax.plot(pp[:,0],pp[:,1],np.full(len(pp),hh),color='#7b8490',alpha=.25,lw=.5)
segments=[];colors=[];at=0
while at<len(lines.lines):
 n=int(lines.lines[at]);ids=lines.lines[at+1:at+1+n];pp=lines.points[ids]
 segments.extend(np.stack([pp[:-1],pp[1:]],axis=1));colors.extend(lines['relative_speed'][ids[:-1]]);at+=n+1
lc=Line3DCollection(segments,cmap='turbo',linewidths=1.3);lc.set_array(np.asarray(colors));lc.set_clim(0,1);ax.add_collection3d(lc)
a=np.linspace(0,2*np.pi,100);ax.plot(15*np.cos(a),15*np.sin(a),np.full(100,30),color='orange',lw=3)
ax.set(xlim=(-90,100),ylim=(-140,140),zlim=(0,42),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)');ax.set_box_aspect((190,280,84));ax.view_init(28,-55)
fig.colorbar(lc,ax=ax,shrink=.5,label='Speed / maximum in hypothetical case');fig.suptitle('V13 / numerical undercroft streamlines\nSolid desktop + full-domain capped roof at z=30 mm; arbitrary central suction port')
fig.text(.1,.04,'Actual low-Re solver field. Not a PS5 vent map, fan operating point or thermal prediction.',fontsize=11)
fig.savefig(R/'flow_streamlines_3d.png',dpi=150);plt.close(fig);print('rendered',p.name,'streamline points',lines.n_points)
