"""Collect the OpenFOAM vent-slot study and draw output/airflow_openfoam.png.
usage: compare.py            (after post_case.py has been run on every case)
Three set-ups share one console underside (18 measured vent slots as the only outlet):
 desk  - console standing straight on the desk, air reaches the slots through the gap under the black base;
 hover - console held 30 mm up with nothing under it;
 stand - console on the v15 stand.
Pressure drop is room total pressure minus total pressure at the top of the slot ducts. Flow rates are ASSUMED:
how much air the console really draws through these slots is not known."""
import json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;C=R/'cases'
S={p.parent.name:json.loads(p.read_text()) for p in sorted(C.glob('*/summary.json'))}
flows=[.03,.06,.12];KINDS=['desk','hover','stand'];sweep=[]
for q in flows:
 r={k:S.get(f'{k}_q{q}') for k in KINDS}
 if all(r.values()):
  dp={k:r[k]['pressure_drop_total_Pa'] for k in KINDS}
  sweep.append({'flow_m3_per_min':q,'slot_speed_m_per_s':r['stand']['outlet_speed_m_per_s'],**{f'{k}_Pa':dp[k] for k in KINDS},'stand_minus_hover_Pa':dp['stand']-dp['hover'],'stand_over_hover':dp['stand']/dp['hover'],'desk_over_stand':dp['desk']/dp['stand'],
   'oscillation_std_Pa':{k:r[k]['outlet_static_p_std_Pa'] for k in KINDS},'mass_imbalance_fraction':max(r[k]['mass_imbalance_fraction'] for k in KINDS)})
out={'scope':'OpenFOAM v2412 (simpleFoam, k-omega SST). Air leaves only through the 18 vent slots measured on a scanned CFI-2009 underside. Flow rates are ASSUMED. Pressure drop is room total pressure minus outlet total pressure and includes the loss of the slots themselves, which is the same in all three set-ups.','sweep':sweep}
q=np.array([r['flow_m3_per_min'] for r in sweep]);fit={}
for k in KINDS:
 if len(sweep)>1:n,lnk=np.polyfit(np.log(q),np.log([r[f'{k}_Pa'] for r in sweep]),1);fit[k]={'exponent':float(n),'Pa_at_0.06_m3_per_min':float(np.exp(lnk)*.06**n)}
out['power_law_fit_dp_equals_k_Q_to_n']=fit
var={}
for name,base,label in [('desk_q0.06_s2.0','desk_q0.06','desk, black base recessed 2.0 mm instead of 2.5'),('desk_q0.06_s3.5','desk_q0.06','desk, recessed 3.5 mm'),('stand_q0.06_s2.0','stand_q0.06','stand, recessed 2.0 mm'),('stand_q0.06_s3.5','stand_q0.06','stand, recessed 3.5 mm'),
  ('stand_q0.06_h1.8','stand_q0.06','stand, base cell 1.8 mm instead of 2.5'),('hover_q0.06_h1.8','hover_q0.06','hover, base cell 1.8 mm'),('desk_q0.06_h1.8','desk_q0.06','desk, base cell 1.8 mm')]:
 if name in S and base in S:var[name]={'what':label,'cells':S[name]['cells'],'baseline_cells':S[base]['cells'],'pressure_drop_total_Pa':S[name]['pressure_drop_total_Pa'],'baseline_Pa':S[base]['pressure_drop_total_Pa'],'change':S[name]['pressure_drop_total_Pa']/S[base]['pressure_drop_total_Pa']-1}
out['variations_at_0.06_m3_per_min']=var
out['inflow_share_by_side']={k:S[f'{k}_q0.06']['inflow_share_by_side'] for k in KINDS if f'{k}_q0.06' in S};out['cases']=S;(R/'summary.json').write_text(json.dumps(out,indent=2))
P={k:np.load(C/f'{k}_q0.06/plan.npz') for k in KINDS if (C/f'{k}_q0.06/plan.npz').exists()}
U=json.loads((R.parents[2]/'references/console-scan/underside.json').read_text())
fig=plt.figure(figsize=(21,8.4),facecolor='#0e1116');gs=fig.add_gridspec(1,4,width_ratios=[1,1,1,1.15],left=.04,right=.985,top=.86,bottom=.1,wspace=.3)
def style(a):
 a.set_facecolor('#0e1116');a.tick_params(colors='#cbd5e2');[sp.set_color('#44506a') for sp in a.spines.values()];a.xaxis.label.set_color('#cbd5e2');a.yaxis.label.set_color('#cbd5e2')
names={'desk':'On the desk, no stand','hover':'Held 30 mm up, no stand','stand':'On the v15 stand'}
for i,k in enumerate(KINDS):
 if k not in P:continue
 a=fig.add_subplot(gs[i]);style(a);p=P[k];sp=np.hypot(p['ux'],p['uy']);blocked=p['fluid_fraction']<.3;ext=[p['x'][0]-2.5,p['x'][-1]+2.5,p['y'][0]-2.5,p['y'][-1]+2.5]
 im=a.imshow(np.ma.masked_where(blocked,sp),origin='lower',extent=ext,cmap='viridis',vmin=0,vmax=np.percentile(sp[~blocked],99));a.imshow(np.ma.masked_where(~blocked,blocked),origin='lower',extent=ext,cmap='gray',vmin=0,vmax=1.6,alpha=.9)
 a.streamplot(p['x'],p['y'],p['ux'],p['uy'],color='white',density=1.4,linewidth=.5,arrowsize=.6)
 for s in U['vent_slots']:a.add_patch(plt.Rectangle((s['x'][0],s['y'][0]),s['x'][1]-s['x'][0],s['y'][1]-s['y'][0],fill=False,ec='#ffb000',lw=.8))
 a.set_aspect('equal');a.set_xlabel('x / mm');a.set_ylabel('y / mm');s=S[f'{k}_q0.06']
 a.set_title(f"{names[k]}: {s['pressure_drop_total_Pa']:.2f} Pa\nmean air speed below the black base, grey = solid, orange = vent slots",color='white',fontsize=9.5)
 c=fig.colorbar(im,ax=a,shrink=.7,pad=.03);c.ax.tick_params(colors='#cbd5e2');c.ax.set_title('m/s',color='#cbd5e2',fontsize=9)
a=fig.add_subplot(gs[3]);style(a);qq=np.linspace(.025,.13,50)
for k,col in zip(KINDS,['#ff5c7a','#6fb7ff','#ffb35c']):
 if not sweep:break
 a.plot(q,[r[f'{k}_Pa'] for r in sweep],'o',color=col,label=names[k]+(f": Δp ∝ Q^{fit[k]['exponent']:.2f}" if k in fit else ''))
 if k in fit:a.plot(qq,fit[k]['Pa_at_0.06_m3_per_min']*(qq/.06)**fit[k]['exponent'],'-',color=col,lw=1)
a.set_yscale('log');a.set_xlabel('assumed flow through the slots / m³ per min');a.set_ylabel('pressure drop / Pa');a.grid(color='#2a3345',lw=.5,which='both');a.legend(facecolor='#161b24',edgecolor='#44506a',labelcolor='white',fontsize=9)
a.set_title('Pressure drop against assumed flow',color='white',fontsize=11)
fig.suptitle('VEIL v15 / OpenFOAM v2412, steady k-ω SST / air leaves only through the 18 vent slots of the scanned underside; maps at an assumed 0.06 m³/min',color='white',fontsize=13)
fig.text(.5,.02,'Assumed: flow rates (the real flow through these slots is not measured), black base recessed 2.5 mm above the cover bottoms and open at the front and rear ends, sealed desk.',ha='center',color='#9aa7bd',fontsize=9)
o=R.parent/'output/airflow_openfoam.png';fig.savefig(o,dpi=110,facecolor=fig.get_facecolor(),bbox_inches='tight');print(json.dumps({k:out[k] for k in ['sweep','power_law_fit_dp_equals_k_Q_to_n','variations_at_0.06_m3_per_min','inflow_share_by_side']},indent=1));print(o.name)
