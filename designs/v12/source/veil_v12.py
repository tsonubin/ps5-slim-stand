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
landmarks=[(8,108,35),(-40,104,42),(-39,68,49),(-34,0,42),(-27,-66,43),(0,-108,33),(55,-92,40),(55,-66,45),(52,0,42),(45,76,46),(39,104,41)]
a=np.array(sorted([(np.arctan2(yy,xx-8),h) for xx,yy,h in landmarks]));height=smooth(PchipInterpolator(np.r_[a[:,0]-2*np.pi,a[:,0],a[:,0]+2*np.pi],np.tile(a[:,1],3))(TH),15)
ref=np.maximum(smooth(raw,8),R_C+2.4);yc=(CENTER+ref[:,None]*U)[:,1];tt=np.clip((104-np.abs(yc))/45,0,1);flare=4.8+(21.8-4.8)*tt*tt*(3-2*tt);flare=smooth(np.minimum(flare,.75*height/1.35),5.33)
b=smooth(ref+flare,17.33)+2*(1+np.cos(TH-.6));base=smooth(ref+np.maximum(b-ref,5)+2,2.67)
front_angle=np.arctan2(np.sin(TH+np.pi/2),np.cos(TH+np.pi/2))
base-=3.5*np.exp(-(front_angle/.50)**2)
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

def flow_warp(coords):
    """One shared periodic, smooth chart deformation for every aperture."""
    u,y=np.asarray(coords).T;phase=2*np.pi*u/PERIMETER
    x=u+(.75+.12*np.sin(phase-.4))*(y-24)+1.5*np.sin(np.pi*(y-24)/24)
    yy=y+1.0*np.sin(phase+.2)
    return np.c_[x,yy]

def aperture_polygons(growth=0.):
    """Periodic weighted blue-noise cells, shrunk after one common flow warp."""
    from scipy.spatial import Voronoi
    from shapely.geometry import Polygon,box
    from shapely.geometry.polygon import orient
    rng=np.random.default_rng(1204);N=72
    candidates=np.c_[rng.uniform(0,PERIMETER,7000),rng.uniform(5.,43.,7000)]
    spacing=1+.16*np.sin(2*np.pi*candidates[:,0]/PERIMETER-.5)+.07*np.cos(4*np.pi*candidates[:,0]/PERIMETER)
    selected=[np.array([.08*PERIMETER,24.])];distance=np.full(len(candidates),np.inf)
    for _ in range(N-1):
        delta=np.abs(candidates-selected[-1]);delta[:,0]=np.minimum(delta[:,0],PERIMETER-delta[:,0])
        distance=np.minimum(distance,np.linalg.norm(delta,axis=1))
        selected.append(candidates[np.argmax(distance/spacing)].copy())
    seeds=np.asarray(selected);sites=[];central=[]
    for shift in [-PERIMETER,0,PERIMETER]:
        for variant in [0,1,2]:
            q=seeds.copy();q[:,0]+=shift
            if variant==1:q[:,1]=6-q[:,1]
            if variant==2:q[:,1]=90-q[:,1]
            if shift==0 and variant==0:central=list(range(len(sites),len(sites)+N))
            sites.extend(q.tolist())
    diagram=Voronoi(np.asarray(sites));result=[]
    for index in central:
        ids=diagram.regions[diagram.point_region[index]];assert -1 not in ids
        cell=Polygon(diagram.vertices[ids]).intersection(box(-PERIMETER,3,2*PERIMETER,45))
        assert cell.is_valid and cell.geom_type=='Polygon'
        line=cell.exterior;n=max(80,int(np.ceil(line.length/.45)))
        points=np.array([line.interpolate(j*line.length/n).coords[0] for j in range(n)])
        warped=Polygon(flow_warp(points));assert warped.is_valid
        # Erosion is applied AFTER warping, so the ligaments belong to one field.
        # Corner opening removes three-way pointy foam-like cusps.
        allowed=warped.buffer(-2.35,quad_segs=8)
        rounding=3.0
        while rounding>1.1:
            core=allowed.buffer(-rounding,quad_segs=8)
            if not core.is_empty and core.geom_type=='Polygon' and core.area>1.:break
            rounding-=.2
        opening=allowed.buffer(-rounding,quad_segs=8).buffer(rounding,quad_segs=8)
        assert opening.geom_type=='Polygon' and opening.is_valid and opening.area>20
        polygon=orient(opening,sign=1.)
        if growth:polygon=orient(polygon.buffer(growth,quad_segs=5),sign=1.)
        result.append(polygon)
    return result

def apertures():
    from shapely.geometry import Point
    from shapely.geometry.polygon import orient
    pieces=[]
    for polygon in aperture_polygons():
        anchor=Point(polygon.exterior.coords[0]);rings=[];flat=[];samples=160
        for depth,growth in [(8.,.35),(.15,.35),(-.1,.25),(-.45,.08),(-.75,0),(-2.05,0),(-2.35,.08),(-2.7,.25),(-2.95,.35),(-9.,.35)]:
            grown=orient(polygon.buffer(growth,quad_segs=5),sign=1.);line=grown.exterior;start=line.project(anchor)
            coords=np.array([line.interpolate((start+j*line.length/samples)%line.length).coords[0] for j in range(samples)])
            th=angle(coords[:,0]);z=coords[:,1]/48*SH(th)
            rings.append(shell_point(th,z,depth));flat.append(coords)
        vertices=np.asarray(rings);faces=[]
        for j in range(len(rings)-1):
            for k0 in range(samples):
                k1=(k0+1)%samples;a=j*samples+k0;b=j*samples+k1;c=b+samples;d=a+samples;faces.extend([[a,b,c],[a,c,d]])
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
 gauge=export_mesh(Manifold.extrude(CAV.offset(4)-CAV,1.6));gauge.export(OUT/'GAUGE_v12_cavity_1.6mm.stl')
 clip=Manifold.cube((58,36,80)).translate((22,34,0));coupon=max((body^clip).decompose(),key=lambda p:p.volume())
 test=export_mesh(coupon);test.apply_translation(-test.bounds[0]);test.export(OUT/'PRINT_TEST_v12_section.stl')
 print('Final dimensions',mesh.extents,'volume cm3',mesh.volume/1000,'faces',len(mesh.faces),flush=True)
