"""Measure the real console underside from a textured phone scan (console standing base-up).
usage: underside_from_scan.py <scan.glb, z up, metres> <registration.json from register_scan.py> <out_dir>
The registration places the scan in the reference model's frame at a scale set by the published 216 mm depth.
Output frame = design frame seen from above through the console: +x disc-drive side, +y rear, mm.
Writes underside.json, underside_texture.png, underside_map.png. The raw scan is not kept in the repository."""
import sys,json
from pathlib import Path
import numpy as np,trimesh
from PIL import Image
from scipy import ndimage as ndi
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
src=sys.argv[1];REG=json.loads(Path(sys.argv[2]).read_text());T=np.array(REG['scan_m_to_design_mm']);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
m=trimesh.load(src,force='mesh',process=False);v=np.c_[m.vertices,np.ones(len(m.vertices))]@T.T[:,:3];cen=v[m.faces].mean(1)
fm=(np.abs(cen[:,0]-8)<62)&(np.abs(cen[:,1])<125)&(cen[:,2]<16)
tex=np.asarray(m.visual.material.baseColorTexture.convert('RGB'));H,W=tex.shape[:2];uv=m.visual.uv;tri=m.faces[fm];ar=trimesh.triangles.area(v[tri])
g=np.random.default_rng(0);N=16_000_000;fi=g.choice(len(tri),N,p=ar/ar.sum());r=g.random((N,2));s=r.sum(1)>1;r[s]=1-r[s];w=np.c_[1-r.sum(1),r]
P=(v[tri[fi]]*w[:,:,None]).sum(1);U=(uv[tri[fi]]*w[:,:,None]).sum(1);col=tex[((1-U[:,1])*(H-1)).astype(int).clip(0,H-1),(U[:,0]*(W-1)).astype(int).clip(0,W-1)]
h=.25;xs_mm=np.arange(-52,68,h)+h/2;ys_mm=np.arange(-118,118,h)+h/2;ix=((P[:,0]+52)/h).astype(int);iy=((P[:,1]+118)/h).astype(int);ok=(ix>=0)&(ix<len(xs_mm))&(iy>=0)&(iy<len(ys_mm))
o=np.argsort(-P[ok,2]);I=np.zeros((len(ys_mm),len(xs_mm),3),np.uint8);Z=np.full(I.shape[:2],np.nan);I[iy[ok][o],ix[ok][o]]=col[ok][o];Z[iy[ok][o],ix[ok][o]]=-P[ok,2][o]   # seen from below; height positive toward the desk
mask=ndi.binary_opening(ndi.binary_fill_holes(ndi.binary_closing(~np.isnan(Z),iterations=3)),iterations=8);Z=np.where(mask,Z,np.nan)
for k in range(3):I[...,k]=np.where(mask&(I.sum(2)==0),ndi.median_filter(I[...,k],5),I[...,k])
Z=np.where(mask&np.isnan(Z),ndi.generic_filter(Z,np.nanmedian,5),Z)
lum=I.astype(float).mean(2)
white=mask&(lum>110)
ext=[xs_mm[0],xs_mm[-1],ys_mm[0],ys_mm[-1]];XX,YY=np.meshgrid(xs_mm,ys_mm)
black=mask&~ndi.binary_dilation(white,iterations=4)
# Boundaries per 2 mm station along y: drive-cover edge (first white going +x from the middle) and the -x rim edge.
st=[];
for yv in np.arange(-100,100.1,4):
 row=np.abs(ys_mm-yv)<2;wb=white[row].mean(0)>.5;mk=mask[row].mean(0)>.5;xi=xs_mm[mk]
 if not mk.any():continue
 j0=np.argmin(np.abs(xs_mm-(-12-.08*yv)));jd=next((j for j in range(j0,len(xs_mm)) if wb[j] and wb[j:j+12].all()),None);jl=next((j for j in range(j0,0,-1) if wb[j] and wb[max(j-6,0):j+1].all()),None)
 st.append([float(yv),float(xi.min()),float(xs_mm[jl]) if jl else None,float(xs_mm[jd]) if jd else None,float(xi.max())])
st=np.array(st,object);yy=st[:,0].astype(float);dd=np.array([q if q is not None else np.nan for q in st[:,3]],float);ll=np.array([q if q is not None else np.nan for q in st[:,2]],float)
okd=~np.isnan(dd);pd=np.polyfit(yy[okd],dd[okd],1);okl=~np.isnan(ll);pl=np.polyfit(yy[okl],ll[okl],2)
# Vent slots: dark blobs in the black face, darker than the local face level.
bl=np.where(black,lum,np.nan);loc=ndi.generic_filter(np.where(black,lum,np.nanmedian(bl)),np.median,size=61);dark=black&(lum<loc*.72)&(XX>np.polyval(pd,YY)-22)&(XX<np.polyval(pd,YY)-1.5)
dark=ndi.binary_opening(dark,iterations=2);lab,nl=ndi.label(dark);slots=[]
for i in range(1,nl+1):
 q=lab==i;ax_=XX[q];ay=YY[q];area=q.sum()*h*h
 if area<15 or area>60 or ax_.max()-ax_.min()<4 or ay.max()>92:continue   # slivers and the rear edge shadow are not slots
 slots.append({'x':[float(ax_.min()),float(ax_.max())],'y':[float(ay.min()),float(ay.max())],'area_mm2':float(area)})
slots.sort(key=lambda s:s['y'][0])
# Step height of the covers above the black face (toward the desk), from bands either side of each boundary.
def step(side):
 res=[]
 for yv in np.arange(-90,90.1,10):
  row=np.abs(YY-yv)<5
  if side=='drive':e=np.polyval(pd,yv);hi=row&white&(XX>e+3)&(XX<e+11);lw=row&black&(XX<e-12)&(XX>e-22)
  else:e=np.polyval(pl,yv);hi=row&mask&(XX<e-.5);lw=row&black&(XX>e+3)&(XX<e+13)
  if hi.sum()>40 and lw.sum()>40:res.append([float(yv),float(np.nanmedian(Z[hi])-np.nanmedian(Z[lw]))])
 return res
sd,sl=step('drive'),step('left')
data={'source':'phone LiDAR/photo scan of a CFI-2009 disc model standing base-up, registered to the reference model outline by rigid ICP','registration':{'scale':REG['scale'],'trimmed_rms_mm':REG['trimmed_rms_mm']},
 'frame':'design frame, mm, seen from above through the console: +x disc-drive side, +y rear',
 'drive_cover_edge_x_of_y':{'poly_deg1':[float(q) for q in pd],'rms_mm':float(np.sqrt(np.mean((np.polyval(pd,yy[okd])-dd[okd])**2)))},
 'left_rim_inner_edge_x_of_y':{'poly_deg2':[float(q) for q in pl]},
 'stations_y_xmin_leftrim_driveedge_xmax':[[None if q is None else round(float(q),2) for q in r] for r in st.tolist()],
 'vent_slots':slots,'vent_slot_count':len(slots),'vent_open_area_mm2':float(sum(s['area_mm2'] for s in slots)),
 'drive_cover_proud_of_black_face_mm':sd,'left_rim_proud_of_black_face_mm':sl}
(out/'underside.json').write_text(json.dumps(data,indent=1));Image.fromarray(I[::-1]).save(out/'underside_texture.png')
np.savez_compressed(out/'underside_grid.npz',x=xs_mm,y=ys_mm,height_mm=np.float32(Z-np.nanmedian(Z[black])),cover=white,black=black,mask=mask)
fig,ax=plt.subplots(1,2,figsize=(14,13))
ax[0].imshow(I,origin='lower',extent=ext);ax[0].plot(np.polyval(pd,yy),yy,'c-',lw=1);ax[0].plot(np.polyval(pl,yy),yy,'c-',lw=1)
for s in slots:ax[0].add_patch(plt.Rectangle((s['x'][0],s['y'][0]),s['x'][1]-s['x'][0],s['y'][1]-s['y'][0],fill=False,ec='#ffb000',lw=1))
im=ax[1].imshow(Z-np.nanmedian(Z[black]),origin='lower',extent=ext,cmap='turbo',vmin=-3,vmax=6);plt.colorbar(im,ax=ax[1],shrink=.6,label='mm toward the desk, relative to the black face median')
for a_ in ax:a_.set_xticks(range(-50,61,10));a_.set_yticks(range(-110,111,10));a_.grid(lw=.3,color='#888');a_.set_xlabel('x / mm (+x disc-drive side)');a_.set_ylabel('y / mm (+y rear)')
ax[0].set_title('Scan texture; cyan = cover edges, orange = detected vent slots');ax[1].set_title('Scan height');fig.savefig(out/'underside_map.png',dpi=80,bbox_inches='tight')
print([ (round(s['x'][0],1),round(s['x'][1],1),round(s['y'][0],1),round(s['y'][1],1)) for s in slots])
