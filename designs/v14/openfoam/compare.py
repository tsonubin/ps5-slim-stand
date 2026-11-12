"""Collect the OpenFOAM sweep, check it against the lattice-Boltzmann screen, and draw the README figure.
usage: compare.py            (after post_case.py has been run on every case)
Writes openfoam/summary.json and output/airflow_openfoam.png.
Both models share the geometry of the screen (sealed table, cap at seat height, suction over the core underside);
they differ in physics: OpenFOAM is steady RANS (k-omega SST) at an ASSUMED flow rate, the lattice-Boltzmann
screen is creeping flow at a fixed suction. All flow rates are assumptions, not measurements."""
import json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;C=R/'cases';AIR=R.parent/'airflow'
S={p.parent.name:json.loads(p.read_text()) for p in sorted(C.glob('*/summary.json'))}
flows=[.25,.5,1.,1.5];sweep=[]
for q in flows:
 e,s=S.get(f'empty_q{q}'),S.get(f'stand_q{q}')
 if e and s:sweep.append({'flow_m3_per_min':q,'no_stand_Pa':e['pressure_drop_total_Pa'],'with_stand_Pa':s['pressure_drop_total_Pa'],'added_by_stand_Pa':s['pressure_drop_total_Pa']-e['pressure_drop_total_Pa'],'ratio':s['pressure_drop_total_Pa']/e['pressure_drop_total_Pa'],
  'oscillation_std_Pa':[e['outlet_static_p_std_Pa'],s['outlet_static_p_std_Pa']],'mass_imbalance_fraction':max(e['mass_imbalance_fraction'],s['mass_imbalance_fraction'])})
out={'scope':'Table-sealed, wall-intake screen in OpenFOAM v2412 (simpleFoam, k-omega SST). Flow rates are ASSUMED; the real fan operating point and vent map are unmeasured. Pressure drop is room total pressure minus outlet total pressure.','sweep':sweep}
q=np.array([r['flow_m3_per_min'] for r in sweep]);fit={}
for key in ['no_stand_Pa','with_stand_Pa']:
 n,lnk=np.polyfit(np.log(q),np.log([r[key] for r in sweep]),1);fit[key]={'exponent':float(n),'Pa_at_1_m3_per_min':float(np.exp(lnk))}
out['power_law_fit_dp_equals_k_Q_to_n']=fit
# Flow kept at equal suction: the stand flow whose pressure drop equals the no-stand drop at each reference flow.
ke,ne=fit['no_stand_Pa']['Pa_at_1_m3_per_min'],fit['no_stand_Pa']['exponent'];ks,ns=fit['with_stand_Pa']['Pa_at_1_m3_per_min'],fit['with_stand_Pa']['exponent']
out['flow_kept_at_equal_suction']={f'{f:g}':float((ke*f**ne/ks)**(1/ns)/f) for f in flows}
ref={}
for name,label in [('stand_q1.0_lvl3','stand surface refinement level 3 (base cell 2.5 mm)'),('stand_q1.0_h1.8','base cell 1.8 mm (stand level 2)'),('empty_q1.0_h1.8','no stand, base cell 1.8 mm')]:
 if name in S:
  b=S['empty_q1.0' if name.startswith('empty') else 'stand_q1.0'];ref[name]={'what':label,'cells':S[name]['cells'],'baseline_cells':b['cells'],'pressure_drop_total_Pa':S[name]['pressure_drop_total_Pa'],'baseline_Pa':b['pressure_drop_total_Pa'],'change':S[name]['pressure_drop_total_Pa']/b['pressure_drop_total_Pa']-1}
out['mesh_refinement_at_1_m3_per_min']=ref
# Lattice-Boltzmann comparison (1.5 mm grid, same screen).
L={k:np.load(AIR/f'{k}_1p5mm_portcore.npz') for k in ['stand','empty']};LJ={k:json.loads((AIR/f'{k}_1p5mm_portcore.json').read_text()) for k in L}
def lbm_plan(a):
 t=a['t'];f=a['field'];fluid=t[1:-1]==1;u=np.where(fluid[...,None],f[1:-1,...,1:],0);n=np.maximum(fluid.sum(0),1);return u[...,0].sum(0)/n,u[...,1].sum(0)/n,fluid.mean(0)
def lbm_sides(a):
 t=a['t'];f=a['field'];rho=f[...,0];fl=(t==1);q={'x_min':(f[1:-1,:,1,1]*rho[1:-1,:,1]*fl[1:-1,:,1]).sum(),'x_max':-(f[1:-1,:,-2,1]*rho[1:-1,:,-2]*fl[1:-1,:,-2]).sum(),'y_min':(f[1:-1,1,:,2]*rho[1:-1,1,:]*fl[1:-1,1,:]).sum(),'y_max':-(f[1:-1,-2,:,2]*rho[1:-1,-2,:]*fl[1:-1,-2,:]).sum()}
 tot=sum(q.values());return {k:float(v/tot) for k,v in q.items()}
cmp={'lattice_boltzmann_flow_kept_at_equal_suction':LJ['stand']['qout_lattice']/LJ['empty']['qout_lattice'],'openfoam_flow_kept_at_equal_suction':out['flow_kept_at_equal_suction'],
 'openfoam_resistance_ratio_at_equal_flow':{f"{r['flow_m3_per_min']:g}":r['ratio'] for r in sweep},'inflow_share_by_side':{}}
for kind in ['stand','empty']:
 if f'{kind}_q1.0' in S:cmp['inflow_share_by_side'][kind]={'openfoam_1_m3_per_min':S[f'{kind}_q1.0']['inflow_share_by_side'],'lattice_boltzmann':lbm_sides(L[kind])}
P={k:np.load(C/f'{k}_q1.0/plan.npz') for k in ['stand','empty'] if (C/f'{k}_q1.0/plan.npz').exists()}
if 'stand' in P:
 from scipy.interpolate import RegularGridInterpolator as RGI
 lx,ly,lf=lbm_plan(L['stand']);xs,ys=L['stand']['x'],L['stand']['y'];p=P['stand'];X,Y=np.meshgrid(p['x'],p['y'])
 ls=RGI((ys,xs),np.hypot(lx,ly),bounds_error=False,fill_value=0)(np.c_[Y.ravel(),X.ravel()]).reshape(X.shape);lfl=RGI((ys,xs),lf,bounds_error=False,fill_value=0)(np.c_[Y.ravel(),X.ravel()]).reshape(X.shape)
 os_=np.hypot(p['ux'],p['uy']);m=(lfl>.5)&(p['fluid_fraction']>.5);a=os_[m]/os_[m].mean();b=ls[m]/ls[m].mean()
 cmp['plan_speed_map_correlation_stand']={'pearson_r':float(np.corrcoef(a,b)[0,1]),'cells_compared':int(m.sum()),'note':'depth-averaged horizontal speed below seat height on a 5 mm plan grid, each map normalised by its own mean'}
out['comparison_with_lattice_boltzmann']=cmp;out['cases']=S;(R/'summary.json').write_text(json.dumps(out,indent=2))
# Figure
fig=plt.figure(figsize=(17,8.2),facecolor='#0e1116');gs=fig.add_gridspec(1,3,width_ratios=[1,1,1.1],left=.05,right=.98,top=.86,bottom=.1,wspace=.28)
def style(a):
 a.set_facecolor('#0e1116');a.tick_params(colors='#cbd5e2');[sp.set_color('#44506a') for sp in a.spines.values()];a.xaxis.label.set_color('#cbd5e2');a.yaxis.label.set_color('#cbd5e2')
if 'stand' in P:
 vmax=np.percentile(np.hypot(P['stand']['ux'],P['stand']['uy'])[P['stand']['fluid_fraction']>.3],99)
 for i,k in enumerate(['empty','stand']):
  if k not in P:continue
  a=fig.add_subplot(gs[i]);style(a);p=P[k];sp=np.hypot(p['ux'],p['uy']);blocked=p['fluid_fraction']<.5;ext=[p['x'][0]-2.5,p['x'][-1]+2.5,p['y'][0]-2.5,p['y'][-1]+2.5]
  im=a.imshow(np.ma.masked_where(blocked,sp),origin='lower',extent=ext,cmap='viridis',vmin=0,vmax=vmax);a.imshow(np.ma.masked_where(~blocked,blocked),origin='lower',extent=ext,cmap='gray',vmin=0,vmax=1.6,alpha=.9)
  a.streamplot(p['x'],p['y'],p['ux'],p['uy'],color='white',density=1.5,linewidth=.5,arrowsize=.6);a.set_aspect('equal');a.set_xlabel('x / mm');a.set_ylabel('y / mm')
  s=S[f'{k}_q1.0'];a.set_title(('No stand' if k=='empty' else 'With stand')+f": {s['pressure_drop_total_Pa']:.2f} Pa at an assumed 1.0 m³/min\nmean air speed below the seat, grey = mostly solid",color='white',fontsize=10)
  c=fig.colorbar(im,ax=a,shrink=.7,pad=.03);c.ax.tick_params(colors='#cbd5e2');c.ax.set_title('m/s',color='#cbd5e2',fontsize=9)
a=fig.add_subplot(gs[2]);style(a);qq=np.linspace(.2,1.6,50)
for key,col,lab in [('no_stand_Pa','#6fb7ff','no stand'),('with_stand_Pa','#ff8a5c','with stand')]:
 a.plot(q,[r[key] for r in sweep],'o',color=col,label=f"{lab}: Δp ≈ {fit[key]['Pa_at_1_m3_per_min']:.2f}·Q^{fit[key]['exponent']:.2f}");a.plot(qq,fit[key]['Pa_at_1_m3_per_min']*qq**fit[key]['exponent'],'-',color=col,lw=1)
a.set_xlabel('assumed flow / m³ per min');a.set_ylabel('pressure drop / Pa');a.grid(color='#2a3345',lw=.5);a.legend(facecolor='#161b24',edgecolor='#44506a',labelcolor='white',fontsize=9)
a.set_title('Pressure drop against assumed flow',color='white',fontsize=11)
fig.suptitle('VEIL v14 / OpenFOAM v2412, steady k-ω SST / table sealed, air enters through the wall openings',color='white',fontsize=13)
fig.text(.5,.02,'Assumed: sealed table, solid cap at seat height, uniform outflow over the whole core underside, flow rates not measured. Real vent map and fan curve unknown.',ha='center',color='#9aa7bd',fontsize=9)
o=R.parent/'output/airflow_openfoam.png';fig.savefig(o,dpi=120,facecolor=fig.get_facecolor(),bbox_inches='tight');print(json.dumps(out,indent=1));print(o.name)
