"""Render the exported v13 shell directly; no subdivision or invented surface details."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src'))
from render_mesh import render
out=root/'designs/v13/output';out.mkdir(exist_ok=True,parents=True)
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
except OSError:font=ImageFont.load_default(size=23);small=ImageFont.load_default(size=18)
WHITE=(.94,.95,.97);BG=(14,17,22)
p=out/'veil_v13_prototype.stl';m=trimesh.load(p)
# Primary design review image at ordinary product-view distance.
hero=render(m,(390,-470,230),(8,0,24),W=1400,H=1000,fov=22,ss=2,color=WHITE,smooth=True)
d=ImageDraw.Draw(hero);d.text((30,24),'VEIL v13 / CONTINUOUS SHELL',font=font,fill='white');d.text((30,950),'Actual exported CAD. Sculpted surface with flowing openings; physical qualification pending.',font=small,fill=(190,205,223));hero.save(out/'hero_v13.png')
views=[('THREE-QUARTER / WHITE',(390,-470,230),(8,0,24),22),('SIDE PROFILE / DRIVE SIDE',(650,0,55),(8,0,25),24),('UNDERSIDE / SUPPORT STRUCTURE',(330,-420,-330),(8,0,20),22),('TOP / CONSOLE CAVITY',(8,-10,690),(8,0,0),22)]
canvas=Image.new('RGB',(1600,1260),BG);d=ImageDraw.Draw(canvas)
for i,(label,eye,target,fov) in enumerate(views):
 xy=((i%2)*800,70+(i//2)*580);canvas.paste(render(m,eye,target,W=800,H=580,fov=fov,ss=2,color=WHITE,smooth=True),xy)
 d.text((xy[0]+24,xy[1]+12),label,font=small,fill=(210,220,233))
d.text((24,20),'VEIL v13 / ACTUAL EXPORTED CAD',font=font,fill='white');d.text((24,1220),'Triangle rasterization; crease-limited shading. Surface design review, not physical fit or strength validation.',font=small,fill=(185,199,216));canvas.save(out/'preview_v13_clean.png')
# Separate flat-shaded side profile exposes real edges and small tessellation artifacts.
side=render(m,(650,0,55),(8,0,25),W=1400,H=700,fov=24,ss=2,color=WHITE,smooth=False)
d=ImageDraw.Draw(side);d.text((25,22),'VEIL v13 / SIDE PROFILE / FLAT FACE SHADING',font=font,fill='white');d.text((25,660),'No normal smoothing; same exported mesh used for the hero and manufacturing files.',font=small,fill=(190,205,223));side.save(out/'side_profile_flat.png')
scene=trimesh.load(root/'references/console-model/PS5_Slim.glb');parts=[m];colors=[np.tile(WHITE,(len(m.faces),1))]
for name,g in scene.geometry.items():
 if name=='unnamed_7':continue
 g=g.copy();g.apply_translation([0,0,30]);parts.append(g)
 colors.append(np.tile((.9,.91,.94) if name in ('unnamed_4','unnamed_5') else (.11,.13,.17),(len(g.faces),1)))
assembly=trimesh.util.concatenate(parts);im=render(assembly,(550,-750,400),(0,0,185),W=1000,H=1100,fov=31,ss=2,color=np.concatenate(colors),smooth=True);d=ImageDraw.Draw(im)
d.text((24,22),'VEIL v13 / REFERENCE ASSEMBLY',font=font,fill='white');d.text((24,1040),'Fan-made console reference at 30 mm lift; original ring omitted.',font=small,fill=(190,205,223));d.text((24,1072),'Visual placement only; physical fit is unverified.',font=small,fill=(190,205,223));im.save(out/'reference_assembly_clean.png')
detail=render(assembly,(280,-360,160),(8,0,45),W=1400,H=1000,fov=27,ss=2,color=np.concatenate(colors),smooth=True);dd=ImageDraw.Draw(detail)
dd.text((28,24),'VEIL v13 / CONSOLE–SHELL TRANSITION',font=font,fill='white');dd.text((28,955),'Actual stand with fan-made console reference; visual placement does not establish physical fit.',font=small,fill=(190,205,223));detail.save(out/'assembly_base_detail.png')
(out/'render_method.json').write_text(json.dumps({'geometry':'Exported manufacturing STL, unchanged','stl_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'projection':'Perspective-correct CPU triangle rasterization with z-buffer','overview_shading':'Vertex averaging only where average is within 20 degrees of face normal; other corners retain face normal','side_profile_shading':'Flat face normals, no smoothing','antialiasing':'2x supersampling with Lanczos reduction','cad_modification':False},indent=2))
print('v13 hero, assembly, overview and flat side profile complete')
