from pathlib import Path
import numpy as np,trimesh,sys
from PIL import Image,ImageDraw,ImageFont
from splat import render
out=Path(__file__).resolve().parent.parent/'output'
a=np.load(out/'mesh.npz'); V,F=a['V'],a['F']
white=(.91,.93,.97);blue=(.12,.35,.84)
views=[('WHITE / FRONT + DRIVE SIDE',(390,-470,280),(8,0,28),white),('BLUE / PLAIN SIDE',(-390,-470,280),(8,0,28),blue),('UNDERSIDE / CURVED RIBS',(330,-420,-330),(8,0,20),white),('TOP / OPEN CORE SUPPORT',(8,-10,690),(8,0,0),blue)]
canvas=Image.new('RGB',(1600,1260),(14,15,19));d=ImageDraw.Draw(canvas)
try: font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
except OSError: font=ImageFont.load_default(size=20)
for i,(title,eye,target,color) in enumerate(views):
 im=Image.fromarray(render([(V,F,color,1)],eye,target,W=800,H=580,fov=22,ss=2))
 xy=((i%2)*800,70+(i//2)*580);canvas.paste(im,xy);d.text((xy[0]+24,xy[1]+10),title,font=font,fill=(210,218,230))
d.text((24,18),'VEIL v6  /  PS5 SLIM DISC  /  DEVELOPMENT PROTOTYPE',font=font,fill='white')
d.text((24,1220),'Actual mesh renders. Fit, printer settings, strength and ventilation still need physical validation.',font=font,fill=(190,200,215))
canvas.save(out/'preview_v6.png')
