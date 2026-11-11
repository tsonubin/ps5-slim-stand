"""Veil v12: one perforated sculpted shell, not a basket of swept wires.
Development CAD; millimetres. No physical fit/strength/thermal qualification.
"""
from pathlib import Path
import sys,json
import numpy as np,trimesh,manifold3d as m3
from scipy.interpolate import CubicSpline,PchipInterpolator
from scipy.ndimage import gaussian_filter1d
CS=m3.CrossSection;Manifold=m3.Manifold
m3.set_circular_segments(48)
HERE=Path(__file__).resolve().parent;OUT=Path(sys.argv[1]) if len(sys.argv)>1 else HERE.parent/'output'
OL=json.loads((HERE/'outline.json').read_text());OY=np.array(OL['y'])[::-1];PL=np.array(OL['plain'])[::-1];DI=np.array(OL['disc'])[::-1]
CENTER=np.array([8.,0.]);H0=30.;CLEAR=1.5;RIB_T=2.8;RIM_BAND=2.;BASE_BAND=3.8;WALL=2.8
M=720;TH=np.linspace(-np.pi,np.pi,M,endpoint=False);U=np.c_[np.cos(TH),np.sin(TH)]
def smooth(a,s):return gaussian_filter1d(a,s,mode='wrap')
y=np.arange(-108,108.01,1.5)
PLAN=CS([np.vstack([np.c_[np.interp(y,OY,DI),y],np.c_[-np.interp(y[::-1],OY,PL),y[::-1]]])]);CAV=PLAN.offset(CLEAR)
def radial(cs):
 p=max(cs.to_polygons(),key=len)-CENTER;e=np.roll(p,-1,axis=0)-p
 den=U[:,None,0]*e[None,:,1]-U[:,None,1]*e[None,:,0]
 with np.errstate(divide='ignore',invalid='ignore'):
  t=(p[None,:,0]*e[None,:,1]-p[None,:,1]*e[None,:,0])/den
  v=(p[None,:,0]*U[:,None,1]-p[None,:,1]*U[:,None,0])/den
 return np.where((v>=0)&(v<=1)&(t>0),t,-1).max(1)
def spline(a):return CubicSpline(np.r_[TH,np.pi],np.r_[a,a[0]],bc_type='periodic')
R_C=radial(CAV);raw=radial(PLAN.offset(CLEAR+3.6));rim=smooth(raw,8)
target=radial(CAV.offset(3.8))
for _ in range(80):
 d=np.maximum(target-rim,0)
 if d.max()<.001:break
 rim+=1.6*smooth(d,4)
rim+=max(0.,(target-rim).max())+.02
landmarks=[(8,108,35),(-40,104,42),(-39,68,49),(-34,0,42),(-27,-66,43),(0,-108,35),(55,-92,40),(55,-66,45),(52,0,42),(45,76,46),(39,104,41)]
a=np.array(sorted([(np.arctan2(yy,xx-8),h) for xx,yy,h in landmarks]));height=smooth(PchipInterpolator(np.r_[a[:,0]-2*np.pi,a[:,0],a[:,0]+2*np.pi],np.tile(a[:,1],3))(TH),15)
ref=np.maximum(smooth(raw,8),R_C+2.4);yc=(CENTER+ref[:,None]*U)[:,1];tt=np.clip((104-np.abs(yc))/45,0,1);flare=4.8+(21.8-4.8)*tt*tt*(3-2*tt);flare=smooth(np.minimum(flare,.75*height/1.35),5.33)
b=smooth(ref+flare,17.33)+2*(1+np.cos(TH-.6));base=smooth(ref+np.maximum(b-ref,5)+2,2.67)
SR,SB,SH=spline(rim),spline(base),spline(height)
RIMH=height

def radial_at(th,z):
 h=SH(th);q=1-z/h
 return SR(th)+(SB(th)-SR(th))*q*q

def shell_point(th,z,depth=0.):
 h=SH(th);q=1-z/h;delta=SB(th)-SR(th);r=SR(th)+delta*q*q
 drth=SR(th,1)+(SB(th,1)-SR(th,1))*q*q+2*delta*q*z*SH(th,1)/(h*h)
 drz=-2*delta*q/h
 normal_factor=np.sqrt(1+(drth/r)**2+drz**2)
 rr=r+depth*normal_factor
 return np.stack([CENTER[0]+rr*np.cos(th),CENTER[1]+rr*np.sin(th),z],axis=-1)

def solid_rings(rings,closed=False):
 rings=np.asarray(rings);ns,nv,_=rings.shape;faces=[]
 for i in range(ns if closed else ns-1):
  j=(i+1)%ns
  for k in range(nv):
   l=(k+1)%nv;a=i*nv+k;b=i*nv+l;c=j*nv+l;d=j*nv+k;faces.extend([[a,b,c],[a,c,d]])
 if not closed:
  for k in range(1,nv-1):faces.extend([[0,k+1,k],[(ns-1)*nv,(ns-1)*nv+k,(ns-1)*nv+k+1]])
 tm=trimesh.Trimesh(rings.reshape(-1,3),faces,process=True);tm.update_faces(tm.nondegenerate_faces());tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices();assert tm.is_watertight;tm.fix_normals();assert tm.volume>0;man=Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)))
 assert man.status()==m3.Error.NoError
 return man

def shell():
 rings=[];bevel=.6
 for th in TH:
  h=float(SH(th));profile=[]
  # A single thin section with quarter-round top/bottom edges; no added rings.
  for z in np.linspace(bevel,h-bevel,100):profile.append((z,0.))
  for a in np.linspace(0,np.pi/2,7)[1:]:profile.append((h-bevel+bevel*np.sin(a),-bevel+bevel*np.cos(a)))
  profile.append((h,-WALL+bevel))
  for a in np.linspace(np.pi/2,np.pi,7)[1:]:profile.append((h-bevel+bevel*np.sin(a),-WALL+bevel+bevel*np.cos(a)))
  for z in np.linspace(h-bevel,bevel,100)[1:]:profile.append((z,-WALL))
  for a in np.linspace(np.pi,3*np.pi/2,7)[1:]:profile.append((bevel+bevel*np.sin(a),-WALL+bevel+bevel*np.cos(a)))
  profile.append((0,-bevel))
  for a in np.linspace(3*np.pi/2,2*np.pi,7)[1:]:profile.append((bevel+bevel*np.sin(a),-bevel+bevel*np.cos(a)))
  rings.append([shell_point(th,z,d) for z,d in profile[:-1]])
 return solid_rings(rings,True)
# Arc-length parameter makes openings respond to the console footprint, not polar crowding.
pts=CENTER+((rim+base)/2)[:,None]*U;ds=np.linalg.norm(np.roll(pts,-1,axis=0)-pts,axis=1);arc=np.r_[0,np.cumsum(ds)];PERIMETER=arc[-1]
def angle(u):return np.interp(np.asarray(u)%PERIMETER,arc,np.r_[TH,np.pi])

def apertures():
    from shapely.geometry import Polygon,Point
    from shapely.geometry.polygon import orient
    pieces=[];N=34
    for band,(cy,span,shift) in enumerate([(10.5,16.5,0.),(24.,23.,.48),(37.5,16.5,.14)]):
        for k in range(N):
            phase=2*np.pi*k/N
            u=(k+shift)*PERIMETER/N+2.1*np.sin(phase-.3)
            center_y=cy+(1.4 if band!=1 else 3.7)*np.sin(phase+band*.7)
            length=span*(1+.11*np.sin(phase-.4))
            q=np.linspace(0,1,81);dy=length*(q-.5)
            shear=1.25+.30*np.cos(phase-.5)
            bend=(1.5+.6*np.sin(phase))*np.sin(2*np.pi*q)
            x=u+shear*dy+bend;y=center_y+dy
            curve=np.c_[x,y];d=np.gradient(curve,axis=0);d/=np.linalg.norm(d,axis=1)[:,None]
            normal=np.c_[-d[:,1],d[:,0]]
            width=(2.4+.45*np.sin(phase+band*.8))*(np.sin(np.pi*q)**.72)*(1+.16*(q-.5))
            polygon=Polygon(np.vstack([curve+normal*width[:,None],(curve-normal*width[:,None])[::-1]]))
            # A genuine rounded tapered S-shaped channel, not a scaled oval.
            polygon=polygon.buffer(-.32,quad_segs=4).buffer(.32,quad_segs=4)
            assert polygon.is_valid and polygon.geom_type=='Polygon'
            # Reserve an uninterrupted lip and foot despite the drifting bands.
            from shapely.geometry import box
            polygon=orient(polygon.intersection(box(u-60,3.8,u+60,44.2)),sign=1.)
            assert polygon.geom_type=='Polygon' and polygon.area>10
            anchor=Point(polygon.exterior.coords[0]);rings=[];flat=[];samples=128
            for depth,growth in [(1.5,.42),(.15,.42),(-.1,.30),(-.45,.10),(-.75,0),(-2.05,0),(-2.35,.10),(-2.7,.30),(-2.95,.42),(-4.4,.42)]:
                grown=orient(polygon.buffer(growth,quad_segs=4),sign=1.);line=grown.exterior;start=line.project(anchor)
                coords=np.array([line.interpolate((start+j*line.length/samples)%line.length).coords[0] for j in range(samples)])
                th=angle(coords[:,0]);z=coords[:,1]/48*SH(th)
                rings.append(shell_point(th,z,depth));flat.append(coords)
            vertices=np.asarray(rings);faces=[]
            for j in range(len(rings)-1):
                for k0 in range(samples):
                    k1=(k0+1)%samples;a=j*samples+k0;b=j*samples+k1;c=b+samples;d=a+samples
                    faces.extend([[a,b,c],[a,c,d]])
            # Ear-clipped 2D caps handle concave curved channels correctly.
            faces.extend(np.asarray(m3.triangulate([flat[0]],allow_convex=False))[:,::-1].tolist())
            faces.extend((np.asarray(m3.triangulate([flat[-1]],allow_convex=False))+(len(rings)-1)*samples).tolist())
            tm=trimesh.Trimesh(vertices.reshape(-1,3),faces,process=True);tm.update_faces(tm.nondegenerate_faces());tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices();assert tm.is_watertight
            tm.fix_normals();assert tm.volume>0
            cutter=Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)));assert cutter.status()==m3.Error.NoError
            pieces.append(cutter)
    return Manifold.batch_boolean(pieces,m3.OpType.Add)

def support_wall(points,width=2.8):
 points=np.asarray(points);d=np.gradient(points,axis=0);d/=np.linalg.norm(d,axis=1)[:,None];n=np.c_[-d[:,1],d[:,0]]*width/2
 length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];q=length/length[-1]
 lower=22*np.sin(np.pi*q)**2
 rings=[]
 for p,nn,z in zip(points,n,lower):
  # Narrow, softly chamfered top contact, broad flowing arch below.
  rings.append([[*(p-nn),z],[*(p+nn),z],[*(p+nn),28.8],[*(p+.55*nn),30],[*(p-.55*nn),30],[*(p-nn),28.8]])
 return solid_rings(rings)

def supports():
 pieces=[]
 # Two continuous bowed load paths with a central crossing: no star or three slabs.
 y=np.linspace(-125,125,251)
 for sign in [-1,1]:
  x=8+sign*(18+10*np.cos(np.pi*y/250))+8*np.sin(np.pi*y/250)
  pieces.append(support_wall(np.c_[x,y]))
 for sign in [-1,1]:
  t=np.linspace(-1,1,181);x=8+62*t;y=sign*(35+16*np.cos(np.pi*t/2))
  pieces.append(support_wall(np.c_[x,y]))
 walls=Manifold.batch_boolean(pieces,m3.OpType.Add)
 # Clip support ends to the inside of the shell; they stay under its quiet rim.
 verts=[]
 for z in np.linspace(0,30,61):verts.append(shell_point(TH,np.full(M,z),-1.6))
 verts=np.array(verts);faces=[]
 for j in range(60):
  for k in range(M):a=j*M+k;b=j*M+(k+1)%M;c=b+M;d=a+M;faces.extend([[a,b,c],[a,c,d]])
 for k in range(1,M-1):faces.extend([[0,k+1,k],[60*M,60*M+k,60*M+k+1]])
 tm=trimesh.Trimesh(verts.reshape(-1,3),faces);tm.fix_normals();env=Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)))
 return walls^env

def export_mesh(body,tol=.008):
 mm=body.as_original().set_tolerance(tol).simplify(tol).to_mesh64();vv=np.asarray(mm.vert_properties)[:,:3];ff=np.asarray(mm.tri_verts);remap=np.arange(len(vv));remap[np.asarray(mm.merge_from_vert,int)]=np.asarray(mm.merge_to_vert,int)
 while np.any(remap[remap]!=remap):remap=remap[remap]
 tm=trimesh.Trimesh(np.float32(vv),remap[ff],process=True);tm.update_faces(tm.nondegenerate_faces());tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices()
 assert tm.is_watertight and tm.is_winding_consistent
 return tm

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);print('Building continuous perforated shell',flush=True)
 skin=shell()-apertures();print('Building concealed flowing support paths',flush=True);body=skin+supports();body=body-Manifold.extrude(CAV,100).translate((0,0,30));body=body^Manifold.cube((400,400,100)).translate((-200,-200,0))
 parts=body.decompose();print('Bodies',len(parts),[p.volume() for p in parts],flush=True);assert len(parts)==1
 mesh=export_mesh(body)
 for ext in ['stl','3mf']:mesh.export(OUT/f'veil_v12_prototype.{ext}')
 np.savez_compressed(OUT/'mesh.npz',V=mesh.vertices,F=mesh.faces)
 print('Final dimensions',mesh.extents,'volume cm3',mesh.volume/1000,'faces',len(mesh.faces),flush=True)
