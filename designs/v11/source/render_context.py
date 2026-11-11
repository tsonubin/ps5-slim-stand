from pathlib import Path
import trimesh,numpy as np
from PIL import Image,ImageDraw,ImageFont
from splat import render
root=Path(__file__).resolve().parents[3];out=root/'designs/v11/output'
s=trimesh.load(root/'references/console-model/PS5_Slim.glb');m=trimesh.load(out/'veil_v11_prototype.stl')
items=[(m.vertices,m.faces,(.92,.94,.98),1)]
for name,g in s.geometry.items():
 if name=='unnamed_7':continue # supplied ring stand, excluded from assembly
 color=(.9,.91,.94) if name in ('unnamed_4','unnamed_5') else (.10,.12,.16)
 items.append((g.vertices+np.array([0,0,30]),g.faces,color,1))
im=Image.fromarray(render(items,(550,-750,400),(0,0,185),W=1000,H=1100,fov=31,ss=2))
d=ImageDraw.Draw(im)
try: font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
except OSError: font=ImageFont.load_default(size=22)
d.text((24,20),'VEIL v11 / REFERENCE ASSEMBLY',font=font,fill='white')
d.text((24,1040),'Fan-made console mesh at 30 mm lift; original ring removed.',font=font,fill=(200,210,220))
d.text((24,1070),'Visual placement only. Does not establish physical fit.',font=font,fill=(200,210,220));im.save(out/'reference_assembly.png')
