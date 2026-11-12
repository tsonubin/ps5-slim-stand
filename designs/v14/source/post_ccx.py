"""Read CalculiX .frd results for a deck directory, summarise, and render von Mises heatmaps.
usage: post_ccx.py <deck_dir> [render]
Strength reference: EOS PA 2200 data sheet, tensile strength 48 MPa in X/Y and 42 MPa in Z (build direction)."""
import sys,json
from pathlib import Path
import numpy as np
d=Path(sys.argv[1]).resolve();M=np.load(d/'model.npz');xyz=M['xyz'];conn=M['conn'];nn=len(xyz);info=json.loads((d/'model.json').read_text())
def frd(path):
 out={};cur=None;rows=[]
 with open(path) as f:
  for line in f:
   if line.startswith(' -4'):cur=line.split()[1];rows=[];out[cur]=rows
   elif line.startswith(' -1') and cur:rows.append(line)
   elif line.startswith(' -3'):cur=None
 res={}
 for k,rows in out.items():
  if k not in('DISP','STRESS'):continue
  n=3 if k=='DISP' else 6;a=np.zeros((nn,n))
  for r in rows:
   i=int(r[3:13])-1
   if i<nn:a[i]=[float(r[13+12*j:25+12*j]) for j in range(n)]
  res[k]=a
 return res
def vmises(s):
 xx,yy,zz,xy,yz,zx=s.T;return np.sqrt(.5*((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)+3*(xy**2+yz**2+zx**2))
p=xyz[conn[:,:4]];vol=np.abs(np.linalg.det(p[:,1:]-p[:,:1]))/6
zones={'pads_and_rib_crossings':(np.abs(xyz[:,0])<24)&(np.abs(np.abs(xyz[:,1])-44)<13)&(xyz[:,2]>8),'plus_x_wall_struts':(xyz[:,0]>38)&(xyz[:,1]>-5)&(xyz[:,1]<112),'within_1.5mm_of_clamped_base':xyz[:,2]<xyz[:,2].min()+1.5}
zones['everything_above_base_zone']=~zones['within_1.5mm_of_clamped_base']
res={}
for inp in sorted(d.glob('*.inp')):
 case=inp.stem
 if not (d/f'{case}.frd').exists():continue
 r=frd(d/f'{case}.frd');u=np.linalg.norm(r['DISP'],axis=1);vm=vmises(r['STRESS']);ev=vm[conn].mean(1);order=np.argsort(ev);cum=np.cumsum(vol[order])/vol.sum()
 item={'max_displacement_mm':float(u.max()),'max_displacement_at_mm':xyz[u.argmax()].round(1).tolist(),'peak_von_mises_MPa':float(vm.max()),'peak_at_mm':xyz[vm.argmax()].round(1).tolist(),'volume_weighted_p95_MPa':float(ev[order[np.searchsorted(cum,.95)]]),'volume_weighted_p99.9_MPa':float(ev[order[np.searchsorted(cum,.999)]]),'volume_above_2MPa_mm3':float(vol[ev>2].sum()),'zones':{}}
 for z,k in zones.items():item['zones'][z]={'peak_MPa':float(vm[k].max()),'at_mm':xyz[np.where(k)[0][vm[k].argmax()]].round(1).tolist()}
 pk=item['zones']['everything_above_base_zone']['peak_MPa'];item['safety_factor_vs_48MPa_XY']=48/pk;item['safety_factor_vs_42MPa_Z']=42/pk
 dat=(d/f'{case}.dat').read_text().split('\n');tot=[l for l in dat if len(l.split())==3 and 'E' in l]
 if tot:item['base_reaction_N']=[float(x) for x in tot[-1].split()]
 cv=d/f'{case}.cvg'
 if cv.exists():item['solver_iterations']=sum(1 for l in cv.read_text().split('\n') if l.strip() and l.split()[0].isdigit())
 res[case]=item;np.savez_compressed(d/f'{case}_fields.npz',u=r['DISP'],vm=vm)
 print(case,'U %.4f'%item['max_displacement_mm'],'peak %.2f at'%item['peak_von_mises_MPa'],item['peak_at_mm'],'p95 %.3f p99.9 %.2f'%(item['volume_weighted_p95_MPa'],item['volume_weighted_p99.9_MPa']),{z:round(v['peak_MPa'],2) for z,v in item['zones'].items()},'R',item.get('base_reaction_N'),flush=True)
info['results']=res;(d/'results.json').write_text(json.dumps(info,indent=2))
if len(sys.argv)>2:
 import trimesh;from PIL import Image,ImageDraw,ImageFont
 root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src'));from render_mesh import render
 stops=np.array([[.16,.33,.79],[.13,.78,.83],[.94,.88,.34],[.93,.30,.24]])
 def cmap(val,limit):
  t=np.clip(np.asarray(val)/limit,0,.999999)*3;i=t.astype(int);return stops[i]*(1-(t-i)[:,None])+stops[i+1]*(t-i)[:,None]
 font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
 bf=M['bfaces'];keep=~M['padtop'] if False else np.ones(len(bf),bool);surf=trimesh.Trimesh(xyz,bf[:,[0,2,1]],process=False)
 for case,item in res.items():
  vm=np.load(d/f'{case}_fields.npz')['vm'];fv=vm[M['bmid']].mean(1);limit=1.0
  im=Image.new('RGB',(1500,1020),(14,17,22));im.paste(render(surf,(290,-340,230),(8,0,20),W=1170,H=750,color=cmap(fv,limit),smooth=False),(0,110));dr=ImageDraw.Draw(im)
  dr.text((35,24),'VEIL v14 / CalculiX, second-order tetrahedra / PA 2200',font=font,fill='white');dr.text((35,64),f'{d.name} / {case} / undeformed shape',font=small,fill='#bdc9dc')
  for i in range(400):dr.line((1220,230+i,1260,230+i),fill=tuple(np.uint8(cmap([(1-i/399)*limit],limit)[0]*255)))
  dr.text((1190,180),'Von Mises / MPa',font=small,fill='white')
  for j in range(5):dr.text((1275,220+j*100),f'{limit*(1-j/4):.2f}',font=small,fill='white')
  pk=item['zones']['everything_above_base_zone']['peak_MPa']
  for i,line in enumerate([f'{info["tets"]:,} tetrahedra, {info["nodes"]:,} nodes | max displacement {item["max_displacement_mm"]:.3f} mm | peak {pk:.1f} MPa (above the clamped base)',
   f'Colour scale 0–1 MPa, higher values saturate red. Datasheet tensile strength 48 MPa (42 MPa in Z): safety factor {48/pk:.1f} / {42/pk:.1f}.',
   'E = 1650 MPa (EOS data sheet), Poisson ratio 0.40 (Faes et al. 2015). Clamped base, console weight 31.392 N'+(' as rigid plate on the pads.' if info['mode']=='contact' else ' as uniform pad pressure.'),
   'Simulation surface, not the print STL. Short-term room-temperature values: creep and warm-air softening are not included.']):dr.text((35,858+i*36),line,font=small,fill='#cbd5e2')
  out=d.parents[1]/'output'/f'ccx_{d.name}_{case}_stress.png';im.save(out);print(out.name)
