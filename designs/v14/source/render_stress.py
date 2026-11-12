"""Actual boundary-triangle rendering of solved cell stress; no invented fields."""
from pathlib import Path
import sys,json
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
from skfem import MeshTet
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root.parents[1]/'src'))
from render_mesh import render
arg=sys.argv[1] if len(sys.argv)>1 else 'v14_fine_result'
a=np.load(root/'analysis'/f'{arg}.npz');r=json.loads((root/'analysis'/f'{arg}.json').read_text());m=MeshTet(a['nodes'].T,a['elements'].T);bf=m.boundary_facets();f=m.facets[:,bf].T
surface=trimesh.Trimesh(a['nodes'],f,process=False);surface.fix_normals()
stops=np.array([[.16,.33,.79],[.13,.78,.83],[.94,.88,.34],[.93,.30,.24]])
def cmap(val,limit):
 t=np.clip(np.asarray(val)/limit,0,.999999)*3;i=t.astype(int);return stops[i]*(1-(t-i)[:,None])+stops[i+1]*(t-i)[:,None]
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
except OSError:font=ImageFont.load_default(size=23);small=ImageFont.load_default(size=18)
for case in ['vertical_1g','eccentric_1g','rim_side_10N']:
 if case not in r['results']: continue
 metrics=r['results'][case];vm=a[case+'_vm'][m.f2t[0,bf]];limit=.6
 im=Image.new('RGB',(1500,1020),(14,17,22));im.paste(render(surface,(290,-340,230),(8,0,20),W=1170,H=750,color=cmap(vm,limit),smooth=False),(0,110));d=ImageDraw.Draw(im)
 d.text((35,24),'VEIL v14 / COMPUTED 3D STRESS',font=font,fill='white');d.text((35,64),arg+' / '+case+' / undeformed shape',font=small,fill='#bdc9dc')
 for i in range(400):d.line((1220,230+i,1260,230+i),fill=tuple(np.uint8(cmap([(1-i/399)*limit],limit)[0]*255)))
 d.text((1190,180),'Von Mises / MPa',font=small,fill='white')
 for j in range(5):d.text((1275,220+j*100),f'{limit*(1-j/4):.3f}',font=small,fill='white')
 lines=[f'{r["tets"]:,} tetrahedra | peak {metrics['peak_von_mises_MPa']:.4f} MPa | max displacement {metrics["max_displacement_mm"]:.5f} mm',
 'Common scale 0–0.6 MPa; higher stresses saturate red. E=1200 MPa, nu=0.35 assumed; clamped base. 31.392 N console load.',
 'Simulation-only regularized surface; printed layers, true contact, creep, impact and tipping not qualified.',
 'First-order tetrahedra: consult mesh-sensitivity report. Stress colors are not temperature or safety margins.']
 for i,line in enumerate(lines):d.text((35,858+i*36),line,font=small,fill='#cbd5e2')
 im.save(root/'output'/f'{arg}_{case}_stress.png')
print('Rendered actual FE boundary triangles',arg)
