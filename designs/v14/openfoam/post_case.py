"""Summarise one OpenFOAM case of the table-sealed, wall-intake screen.
usage: post_case.py <case_dir>          -> writes <case_dir>/summary.json and <case_dir>/plan.npz
Pressure drop = total pressure of the still room air (0) minus the area-average total pressure on the outlet patch.
The case's p is kinematic (m2/s2), so it is multiplied by rho. The outlet velocity is uniform by its boundary condition,
so outlet total pressure = <p> + 0.5 (Q/A)^2. Values are averaged over the last third of the iteration history,
because the steady solver settles into a small oscillation rather than a fixed point.
plan.npz holds the depth-averaged horizontal velocity below seat height on a 5 mm plan grid."""
import sys,json,re
from pathlib import Path
import numpy as np
case=Path(sys.argv[1]).resolve();info=json.loads((case/'case.json').read_text());rho=info['rho_kg_per_m3'];Q=info['flow_m3_per_s']
def history(name):
 f=next((case/'postProcessing'/name).glob('*/surfaceFieldValue.dat'));txt=f.read_text();area=float(re.search(r'# Area\s*:\s*(\S+)',txt).group(1))
 return np.array([[float(v) for v in l.split()] for l in txt.split('\n') if l and l[0]!='#']),area
def field(path):
 """Internal field and boundary values of an ASCII OpenFOAM vol/surface field."""
 txt=path.read_text()
 def block(s):
  m=re.match(r'\s*nonuniform List<(\w+)>\s*(\d+)\s*\(',s)
  if not m:
   u=re.match(r'\s*uniform\s*(\([^)]*\)|\S+?);',s);return None if not u else np.array([float(v) for v in u.group(1).strip('()').split()])
  n=int(m.group(2));body=s[m.end():];w=3 if m.group(1)=='vector' else 1
  vals=np.array(body[:body.index('\n)\n')].replace('(',' ').replace(')',' ').split(),float) if n else np.zeros(0)
  return vals.reshape(n,w) if w==3 else vals
 out={'internal':block(txt[txt.index('internalField')+len('internalField'):])};b=txt[txt.index('boundaryField'):]
 for m in re.finditer(r'\n    (\w+)\n    \{',b):
  seg=b[m.end():];k=seg.find('value');end=seg.find('\n    }')
  if 0<=k<end:out[m.group(1)]=block(seg[k+5:])
 return out
P,A=history('outletP');S,_=history('sidesPhi');n=len(P);w=slice(-max(3,n//3),None);Uo=Q/A
p=P[w,1].mean();pt=p+.5*Uo*Uo
log=(case/'log.simpleFoam').read_text();res={k:float(re.findall(rf'Solving for {k}, Initial residual = (\S+),',log)[-1]) for k in ['Ux','Uy','Uz','p','k','omega']}
cm=(case/'log.checkMesh').read_text()
out={'case':case.name,**info,'cells':int(re.search(r'cells:\s+(\d+)',cm).group(1)),'checkMesh':'OK' if 'Mesh OK' in cm else 'see log.checkMesh','max_non_orthogonality_deg':float(re.search(r'Mesh non-orthogonality Max: (\S+)',cm).group(1)),
 'iterations':int(P[-1,0]),'averaging_window_iterations':[int(P[w,0][0]),int(P[w,0][-1])],'outlet_area_m2':A,'outlet_speed_m_per_s':Uo,
 'outlet_static_p_Pa':rho*p,'outlet_static_p_std_Pa':rho*P[w,1].std(),'pressure_drop_total_Pa':-rho*pt,'pressure_drop_static_Pa':-rho*p,
 'inflow_through_sides_m3_per_s':-S[w,1].mean(),'mass_imbalance_fraction':abs(-S[w,1].mean()-Q)/Q,'final_initial_residuals':res}
t=sorted((d for d in case.iterdir() if d.name.isdigit() and d.name!='0'),key=lambda d:int(d.name))[-1]
C=field(t/'C');U=field(t/'U');V=field(t/'V');phi=field(t/'phi')
fc=C['sides']*1e3;ph=phi['sides'];X0,X1,Y0,Y1=-90,100,-140,140;tol=.5
side={'x_min':abs(fc[:,0]-X0)<tol,'x_max':abs(fc[:,0]-X1)<tol,'y_min':abs(fc[:,1]-Y0)<tol,'y_max':abs(fc[:,1]-Y1)<tol}
out['inflow_share_by_side']={k:float(-ph[m].sum()/-ph.sum()) for k,m in side.items()}
c=C['internal']*1e3;u=U['internal'];v=V['internal'];below=c[:,2]<30;h=5.;   # 5 mm bins: a whole multiple of the 2.5 mm base cell, so no bin is left empty
xe=np.arange(X0,X1+h/2,h);ye=np.arange(Y0,Y1+h/2,h)
H=lambda wgt:np.histogram2d(c[below,1],c[below,0],bins=[ye,xe],weights=wgt)[0]
vol=H(v[below]);ux=H(u[below,0]*v[below])/np.maximum(vol,1e-30);uy=H(u[below,1]*v[below])/np.maximum(vol,1e-30)
np.savez_compressed(case/'plan.npz',x=(xe[:-1]+xe[1:])/2,y=(ye[:-1]+ye[1:])/2,ux=ux,uy=uy,fluid_fraction=vol/(h*h*30e-9))
out['time_folder']=t.name;(case/'summary.json').write_text(json.dumps(out,indent=2))
print(case.name,'cells',out['cells'],'dp_total %.3f Pa'%out['pressure_drop_total_Pa'],'static %.3f +- %.3f'%(out['pressure_drop_static_Pa'],out['outlet_static_p_std_Pa']),'imbalance %.1e'%out['mass_imbalance_fraction'],{k:round(s,3) for k,s in out['inflow_share_by_side'].items()})
