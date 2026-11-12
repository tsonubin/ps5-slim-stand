"""Actual exported CAD, triangle rasterization; flat-shaded comparison for junction review."""
from pathlib import Path
import sys,json
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src'))
from render_mesh import render
out=root/'designs/v11/output';out.mkdir(exist_ok=True,parents=True)
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23);small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
except OSError:font=ImageFont.load_default(size=23);small=ImageFont.load_default(size=18)
WHITE=(.94,.95,.97);BLUE=(.18,.39,.74)
# Identical world-space cameras across versions; no deformation or image-generated geometry.
CLOSEUPS=[('TOP RIM / DRIVE SIDE',(180,-175,105),(51,-68,39),28),('BASE RING / DRIVE SIDE',(155,-155,42),(61,-67,6),27),('WEB INTERSECTION',(165,-145,92),(59,-47,25),25)]
if '--baseline-only' in sys.argv:
 m=trimesh.load(root/'designs/v10/output/veil_v10_prototype.stl')
 for i,(label,eye,target,fov) in enumerate(CLOSEUPS):render(m,eye,target,W=800,H=600,fov=fov,ss=2,color=WHITE,smooth=False).save(out/f'v10_junction_{i}_flat.png')
 print('Baseline flat junctions rendered');raise SystemExit
m=trimesh.load(out/'veil_v11_prototype.stl')
crossing_report=out/'crossing_blend.json'
if crossing_report.exists() and (out/'root_only.stl').exists():
 report=json.loads(crossing_report.read_text());centers=np.array([p['center_mm'] for p in report['patches']])
 target=centers[np.argmin(np.linalg.norm(centers-np.array([62,-50,23]),axis=1))]
 eye=target+np.array([45,-45,30]);before=trimesh.load(out/'root_only.stl')
 panel=Image.new('RGB',(1600,800),(14,17,22));pd=ImageDraw.Draw(panel)
 pd.text((24,20),'V11 WEB CROSSING / LOCAL FILLET DETAIL',font=font,fill='white')
 for i,(geom,label) in enumerate([(before,'ROOTS BLENDED / CROSSING BEFORE'),(m,'FINAL / CROSSING BLENDED')]):
  image=render(geom,eye,target,W=800,H=650,fov=18,ss=3,color=WHITE,smooth=False);panel.paste(image,(800*i,90));pd.text((24+800*i,105),label,font=small,fill='white')
 pd.text((24,760),'Flat face shading; same view and lighting. Center (mm): '+', '.join(f'{x:.2f}' for x in target),font=small,fill=(185,199,216))
 panel.save(out/'crossing_blend_process_flat.png')

views=[('WHITE / FRONT + DRIVE SIDE',(390,-470,280),(8,0,28),WHITE),('BLUE / PLAIN SIDE',(-390,-470,280),(8,0,28),BLUE),('UNDERSIDE / CURVED SUPPORT',(330,-420,-330),(8,0,20),WHITE),('TOP / OPEN CORE SUPPORT',(8,-10,690),(8,0,0),BLUE)]
canvas=Image.new('RGB',(1600,1260),(14,17,22));d=ImageDraw.Draw(canvas)
for i,(label,eye,target,color) in enumerate(views):
 xy=((i%2)*800,70+(i//2)*580);canvas.paste(render(m,eye,target,W=800,H=580,fov=22,ss=2,color=color,smooth=True),xy);d.text((xy[0]+24,xy[1]+12),label,font=small,fill=(210,220,233))
d.text((24,20),'VEIL v11 / ACTUAL EXPORTED CAD',font=font,fill='white');d.text((24,1220),'Triangle rasterization; crease-limited shading. Geometry, fit and physical qualification are separate checks.',font=small,fill=(185,199,216));canvas.save(out/'preview_v11_clean.png')
baseline=trimesh.load(root/'designs/v10/output/veil_v10_prototype.stl')
preblend_path=out/'preblend_skin.stl'
if preblend_path.exists():
 pre=trimesh.load(preblend_path);panel=Image.new('RGB',(1600,1380),(14,17,22));pd=ImageDraw.Draw(panel)
 pd.text((24,20),'V11 JUNCTION PROCESS / BEFORE AND AFTER LOCAL BLENDING',font=font,fill='white')
 for j,(label,eye,target,fov) in enumerate(CLOSEUPS[:2]):
  for i,(geom,tag) in enumerate([(pre,'BEFORE LOCAL BLEND'),(m,'FINAL EXPORTED CAD')]):
   image=render(geom,eye,target,W=800,H=600,fov=fov,ss=2,color=WHITE,smooth=False);xy=(i*800,100+j*610);panel.paste(image,xy)
   pd.text((xy[0]+24,xy[1]+15),tag+' / '+label,font=small,fill='white')
 pd.text((24,1335),'Flat face normals, matched camera/light. Before view is exterior only; final also includes internal supports.',font=small,fill=(185,199,216))
 panel.save(out/'junction_blend_process_flat.png')

canvas=Image.new('RGB',(1600,1980),(14,17,22));d=ImageDraw.Draw(canvas)
d.text((25,20),'JUNCTION GEOMETRY / MATCHED CAMERAS + FLAT FACE SHADING',font=font,fill='white')
for j,(label,eye,target,fov) in enumerate(CLOSEUPS):
 for i,(model,tag) in enumerate([(baseline,'v10'),(m,'v11')]):
  im=render(model,eye,target,W=800,H=600,fov=fov,ss=2,color=WHITE,smooth=False);xy=(i*800,100+j*610);canvas.paste(im,xy);d.text((xy[0]+24,xy[1]+15),f'{tag.upper()} / {label}',font=small,fill='white')
d.text((25,1940),'No vertex-normal smoothing in these close-ups. Same lighting and world-space view; no geometric morphing.',font=small,fill=(185,199,216));canvas.save(out/'junction_comparison_flat.png')
# Assembly uses supplied reference mesh; ignore its stock ring stand.
scene=trimesh.load(root/'references/console-model/PS5_Slim.glb');parts=[m];colors=[np.tile(WHITE,(len(m.faces),1))]
for name,g in scene.geometry.items():
 if name=='unnamed_7':continue
 g=g.copy();g.apply_translation([0,0,30]);parts.append(g)
 colors.append(np.tile((.9,.91,.94) if name in ('unnamed_4','unnamed_5') else (.11,.13,.17),(len(g.faces),1)))
assembly=trimesh.util.concatenate(parts);im=render(assembly,(550,-750,400),(0,0,185),W=1000,H=1100,fov=31,ss=2,color=np.concatenate(colors),smooth=True);d=ImageDraw.Draw(im)
d.text((24,22),'VEIL v11 / REFERENCE ASSEMBLY',font=font,fill='white');d.text((24,1040),'Fan-made console reference at 30 mm lift; original ring omitted.',font=small,fill=(190,205,223));d.text((24,1072),'Visual placement only; physical fit is unverified.',font=small,fill=(190,205,223));im.save(out/'reference_assembly_clean.png')
(out/'render_method.json').write_text(json.dumps({'geometry':'Exported manufacturing STL, unchanged','projection':'Perspective-correct CPU triangle rasterization with z-buffer','overview_shading':'Vertex averaging only where average is within 20 degrees of face normal; other corners retain face normal','junction_shading':'Flat face normals, no normal smoothing; matched camera and lighting','antialiasing':'2x supersampling with Lanczos reduction','cad_modification':False},indent=2))
print('Clean overview, assembly and flat-shaded junction comparison complete')
