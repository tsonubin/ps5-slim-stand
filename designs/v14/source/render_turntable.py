"""Twelve-azimuth turntable of the exported STL, alternating high and low eye height.
v13 is rendered the same way for comparison. (Zebra stripes were tried and dropped:
the openings break the bands up too much to read.)"""
from pathlib import Path
import sys
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src'))
from render_mesh import render
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
except OSError:font=ImageFont.load_default(size=22);small=ImageFont.load_default(size=16)
def sheet(ver):
 m=trimesh.load(root/('designs/v14/output/veil_v14_prototype.stl' if ver=='v14' else 'designs/v14/baseline_v13/veil_v13_prototype.stl'));W,H=560,400
 canvas=Image.new('RGB',(4*W,3*H+70),(14,17,22));d=ImageDraw.Draw(canvas)
 for i,az in enumerate(range(0,360,30)):
  a=np.radians(az);eye=(8+640*np.cos(a),640*np.sin(a),150 if i%2==0 else 40)
  im=render(m,eye,(8,0,20),W=W,H=H,fov=24,ss=2,color=(.94,.95,.97),smooth=True)
  canvas.paste(im,((i%4)*W,60+(i//4)*H))
  d.text(((i%4)*W+14,66+(i//4)*H),f'{az} deg / {"high" if i%2==0 else "low"} eye',font=small,fill=(205,215,230))
 d.text((20,16),f'VEIL {ver} / TURNTABLE, 12 AZIMUTHS / actual exported STL',font=font,fill='white')
 out=root/f'designs/v14/output/turntable_{ver}.png';canvas.save(out);print(out.name)
sheet('v14');sheet('v13')
