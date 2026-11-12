"""Plan-view maps of the table-sealed, wall-intake case (suction over the whole core underside).
Left: depth-averaged speed and streamlines under the seat. Right: suction reaching each part of
the underside, relative to the no-stand mean. Colours are solved lattice fields, relative only."""
from pathlib import Path
import sys,json
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;tag=sys.argv[1] if len(sys.argv)>1 else '1p5mm'
s=np.load(R/f'stand_{tag}_portcore.npz');e=np.load(R/f'empty_{tag}_portcore.npz')
t=s['t'];f=s['field'];x=s['x'];y=s['y'];fluid=(t[1:-1]==1)
u=np.where(fluid[...,None],f[1:-1,...,1:],0);n=np.maximum(fluid.sum(0),1)
ux=u[...,0].sum(0)/n;uy=u[...,1].sum(0)/n;speed=np.hypot(ux,uy);blocked=fluid.mean(0)<.34
def port_flux(a):
 tt=a['t'];ff=a['field'];q=ff[-2,...,3]*ff[-2,...,0];return np.where(tt[-1]==3,q,np.nan),(e['t'][-1]==3)
qs,core=port_flux(s);qe,_=port_flux(e);ref=np.nanmean(qe);rel=np.where(core,np.nan_to_num(qs)/ref,np.nan)
fig,ax=plt.subplots(1,2,figsize=(13,9.2),facecolor='#0e1116')
ext=[x[0],x[-1],y[0],y[-1]]
for a in ax:a.set_facecolor('#0e1116');a.set_aspect('equal');a.tick_params(colors='#cbd5e2');a.set_xlabel('x / mm',color='#cbd5e2');a.set_ylabel('y / mm',color='#cbd5e2');[sp.set_color('#44506a') for sp in a.spines.values()]
vmax=np.percentile(speed[~blocked],99);im=ax[0].imshow(np.ma.masked_where(blocked,speed/vmax),origin='lower',extent=ext,cmap='viridis',vmin=0,vmax=1)
ax[0].imshow(np.ma.masked_where(~blocked,blocked),origin='lower',extent=ext,cmap='gray',vmin=0,vmax=1.6,alpha=.9)
ax[0].streamplot(x,y,ux,uy,color='white',density=1.7,linewidth=.5,arrowsize=.6)
ax[0].contour(x,y,core.astype(float),[.5],colors='#ff8a5c',linewidths=1.2)
ax[0].set_title('Air speed under the seat (depth-averaged, relative)\norange outline = console underside, grey = stand',color='white',fontsize=11)
c=fig.colorbar(im,ax=ax[0],shrink=.7);c.ax.tick_params(colors='#cbd5e2');c.set_label('speed / 99th-percentile speed',color='#cbd5e2')
im2=ax[1].imshow(rel,origin='lower',extent=ext,cmap='magma',vmin=0,vmax=max(1.,np.nanpercentile(rel,99)))
ax[1].contour(x,y,blocked.astype(float),[.5],colors='#7f8aa3',linewidths=.5)
ax[1].set_title('Suction reaching the underside\n1 = mean with no stand; black inside outline = covered by pad or rib',color='white',fontsize=11)
c=fig.colorbar(im2,ax=ax[1],shrink=.7);c.ax.tick_params(colors='#cbd5e2');c.set_label('local flux / no-stand mean flux',color='#cbd5e2')
se=json.loads((R/f'stand_{tag}_portcore.json').read_text());ee=json.loads((R/f'empty_{tag}_portcore.json').read_text())
fig.suptitle(f'VEIL v14 / table-sealed, wall-intake screen / {se["pitch_mm"]:g} mm grid / flow with stand = {100*se["qout_lattice"]/ee["qout_lattice"]:.1f}% of no-stand flow',color='white',fontsize=13)
fig.text(.5,.02,'Assumed: sealed table, solid cap at seat height, uniform suction over the whole core underside, creeping-flow lattice-Boltzmann. Real vent map and fan curve unmeasured.',ha='center',color='#9aa7bd',fontsize=9)
out=R.parent/'output'/f'airflow_sealed_{tag}.png';fig.savefig(out,dpi=130,facecolor=fig.get_facecolor(),bbox_inches='tight');print(out.name)
