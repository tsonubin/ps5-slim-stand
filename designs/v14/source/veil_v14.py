"""Veil v14: v13 shell with strictly convex perimeter guides, four seat pads,
lowered/rerouted support ribs and filleted rib crossings.
Development CAD; millimetres. No physical fit/strength/thermal qualification.
"""
from pathlib import Path
import os,sys,json
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
# v13: restraint in elevation, and analytic periodic plan guides.
# Fourier coefficients are tapered smoothly to remove short spatial ripples.
# These finite trigonometric series are C-infinity, including their periodic seam.
class FourierGuide:
 def __init__(self,values,cutoff):
  self.k=np.arange(cutoff+1)
  self.c=np.fft.rfft(values)[:cutoff+1]/len(values)
  taper=np.ones(cutoff+1);start=max(1,int(cutoff*.65));t=np.arange(cutoff-start+1)/(cutoff-start)
  taper[start:]=.5*(1+np.cos(np.pi*t));self.c*=taper
 def __call__(self,theta,nu=0):
  theta=np.asarray(theta);phase=np.exp(1j*np.multiply.outer(theta+np.pi,self.k))
  coeff=self.c*(1j*self.k)**nu
  result=2*np.real(phase@coeff)
  if nu==0:result-=self.c[0].real
  return result
legacy_rim=rim.copy();legacy_base=base.copy();legacy_height=height.copy()
# v14: both plan guides are strictly convex ovals. Each is a Fourier series of the
# SUPPORT FUNCTION p(phi) (phi = outward-normal angle): radius of curvature is p+p'',
# so convexity and clearance are linear constraints and the fit is a small QP.
from scipy.optimize import minimize
PHI=np.linspace(-np.pi,np.pi,720,endpoint=False);KS=24;_k=np.arange(1,KS+1);_a=np.outer(PHI,_k)
SB0=np.c_[np.ones(720),np.cos(_a),np.sin(_a)];SB1=np.c_[np.zeros(720),-_k*np.sin(_a),_k*np.cos(_a)]
SRHO=np.c_[np.ones(720),(1-_k*_k)*np.cos(_a),(1-_k*_k)*np.sin(_a)];SRHO1=np.c_[np.zeros(720),-(1-_k*_k)*_k*np.sin(_a),(1-_k*_k)*_k*np.cos(_a)]
def support_of(radii):return ((radii[:,None]*U)@np.c_[np.cos(PHI),np.sin(PHI)].T).max(0)
def convex_fit(goal,low,rho_min,lam,high=None):
 A=np.vstack([SB0,np.sqrt(lam)*SRHO1]);b=np.r_[goal,np.zeros(720)];c0=np.zeros(2*KS+1);c0[0]=low.max()+5
 cons=[{'type':'ineq','fun':lambda c:SB0@c-low,'jac':lambda c:SB0},{'type':'ineq','fun':lambda c:SRHO@c-rho_min,'jac':lambda c:SRHO}]
 if high is not None:cons.append({'type':'ineq','fun':lambda c:high-SB0@c,'jac':lambda c:-SB0})
 res=minimize(lambda c:np.mean((A@c-b)**2),c0,jac=lambda c:2*A.T@(A@c-b)/len(b),constraints=cons,method='SLSQP',options={'maxiter':3000,'ftol':1e-11})
 # SLSQP may stop on a flat line search; accept only if every constraint is actually met.
 worst=min(float(np.min(f['fun'](res.x))) for f in cons);assert worst>-1e-6,(res.message,worst)
 return res.x
def support_to_polar(c):
 phi=np.linspace(-np.pi,np.pi,14400,endpoint=False);a=np.outer(phi,_k);p=np.c_[np.ones(len(phi)),np.cos(a),np.sin(a)]@c;d=np.c_[np.zeros(len(phi)),-_k*np.sin(a),_k*np.cos(a)]@c
 x=p*np.cos(phi)-d*np.sin(phi);y=p*np.sin(phi)+d*np.cos(phi);ang=np.arctan2(y,x);o=np.argsort(ang);r=np.hypot(x,y)
 return np.interp(TH,np.r_[ang[o]-2*np.pi,ang[o],ang[o]+2*np.pi],np.tile(r[o],3))
H_RIM=support_of(target+.02);C_RIM=convex_fit(H_RIM,H_RIM,12.,3e-5)
P_RIM=SB0@C_RIM;H_BASE=np.maximum(support_of(base),P_RIM+5.)
C_BASE=convex_fit(H_BASE,P_RIM+2.,20.,3e-5,high=P_RIM+26.)
rim=support_to_polar(C_RIM);base=support_to_polar(C_BASE)
SR=FourierGuide(rim,120)
SR.c[0]+=max(0.,float(np.max(target-SR(TH))))+.02
SB=FourierGuide(base,120)
# Quiet, nearly level rim; lowest point remains above the 30 mm seat.
height=39.5+1.2*np.sin(TH+.4)+.35*np.cos(2*TH-.2)
SH=FourierGuide(height,3)
# Do not taper the two purposeful height harmonics.
SH.c=np.fft.rfft(height)[:4]/len(height)
rim=SR(TH);base=SB(TH);height=SH(TH);RIMH=height
# Wall thickness grows inward only, and only where the rim stands well clear of the cavity.
WALL_EXTRA=float(os.environ.get('VEIL_WALL_EXTRA','0.7'))
_gap=rim-R_C;_w=np.clip((_gap-5.)/5.,0,1);_w=_w*_w*(3-2*_w)
WT=spline(WALL+WALL_EXTRA*smooth(_w,10))

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
  h=float(SH(th));wt=float(WT(th));profile=[]
  # A single thin section with quarter-round top/bottom edges; no added rings.
  for z in np.linspace(bevel,h-bevel,100):profile.append((z,0.))
  for a in np.linspace(0,np.pi/2,7)[1:]:profile.append((h-bevel+bevel*np.sin(a),-bevel+bevel*np.cos(a)))
  profile.append((h,-wt+bevel))
  for a in np.linspace(np.pi/2,np.pi,7)[1:]:profile.append((h-bevel+bevel*np.sin(a),-wt+bevel+bevel*np.cos(a)))
  for z in np.linspace(h-bevel,bevel,100)[1:]:profile.append((z,-wt))
  for a in np.linspace(np.pi,3*np.pi/2,7)[1:]:profile.append((bevel+bevel*np.sin(a),-wt+bevel+bevel*np.cos(a)))
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
            rings.append(shell_point(th,z,depth-(WT(th)-WALL if depth<-1.4 else 0.)));flat.append(coords)
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
 lower=(RIB_TOP-RIB_DEPTH)*np.sin(np.pi*q)**ARCH_P
 rings=[]
 for p,nn,z in zip(points,n,lower):
  # v14: rib crest sits 1 mm BELOW the seat; only the pads touch the console.
  rings.append([[*(p-nn),z],[*(p+nn),z],[*(p+nn),RIB_TOP-1.2],[*(p+.55*nn),RIB_TOP],[*(p-.55*nn),RIB_TOP],[*(p-nn),RIB_TOP-1.2]])
 return solid_rings(rings)

RIB_TOP=float(os.environ.get('VEIL_RIB_TOP','29'));RIB_DEPTH=float(os.environ.get('VEIL_RIB_DEPTH','7'));ARCH_P=float(os.environ.get('VEIL_ARCH_P','1'));PAD_AX=6.5;PAD_AY=12.;PAD_EDGE=1.5
# Pad centres sit inside the flat bottom of the reference console core (>=5 mm from its edge).
PADS=[(-16.5,44.),(16.5,44.),(-11.5,-44.),(11.5,-44.)]
def rib_paths():
 paths=[];y=np.linspace(-125,125,251);s0=np.sin(np.pi*y/250);c0=np.cos(np.pi*y/250)
 for sign in [-1,1]:paths.append(np.c_[sign*(14+4.76*s0+4*(c0-np.cos(np.pi*44/250))),y])
 t=np.linspace(-1,1,181)
 for sign in [-1,1]:paths.append(np.c_[8+70*t,sign*(37+8*np.cos(np.pi*t/2))])
 return paths
def pad(cx,cy):
 """Flat-topped landing pad: rolled 1.5 mm edge above, 45 degree self-supporting cone below."""
 t=np.linspace(0,2*np.pi,72,endpoint=False);n=2.5;ux=np.sign(np.cos(t))*np.abs(np.cos(t))**(2/n);uy=np.sign(np.sin(t))*np.abs(np.sin(t))**(2/n)
 levels=[(H0-PAD_EDGE-i,i) for i in np.linspace(PAD_AX-1.,0,12)]
 levels+=[(H0-PAD_EDGE+PAD_EDGE*np.sin(a),PAD_EDGE*(1-np.cos(a))) for a in np.linspace(0,np.pi/2,9)[1:]]
 rings=[[[cx+max(PAD_AX-i,1.)*a,cy+max(PAD_AY-i,1.)*b,z] for a,b in zip(ux,uy)] for z,i in levels]
 return solid_rings(rings)
def crossing_fillets(paths):
 """Fill the vertical reentrant corners where two ribs cross; radius grows at 45 degrees."""
 from shapely.geometry import LineString,Point
 from shapely.geometry.polygon import orient
 from shapely.ops import unary_union
 out=[]
 for a in paths[:2]:
  for b in paths[2:]:
   la,lb=LineString(a),LineString(b);x=la.intersection(lb);assert x.geom_type=='Point'
   z0=max((RIB_TOP-RIB_DEPTH)*np.sin(np.pi*l.project(x)/l.length)**ARCH_P for l in (la,lb))
   web=unary_union([la.buffer(1.4,cap_style=2),lb.buffer(1.4,cap_style=2)]).intersection(x.buffer(10))
   for z in np.arange(z0,RIB_TOP-1.2-.3,.3):
    r=min(3.,z-z0+.3);g=web.buffer(r,quad_segs=8).buffer(-r,quad_segs=8).intersection(x.buffer(7.5,quad_segs=16))
    g=max(getattr(g,'geoms',[g]),key=lambda q:q.area)
    slab=Manifold.extrude(CS([np.asarray(orient(g,sign=1.).exterior.coords)[:-1]]),.3).translate((0,0,float(z)));assert slab.status()==m3.Error.NoError and slab.volume()>0
    out.append(slab)
 return out
FOOT_R=float(os.environ.get('VEIL_FOOT_FILLET','3'));FOOT_PITCH=float(os.environ.get('VEIL_FOOT_PITCH','0.1'));FOOT_LOG=[]
def inner_radius(th,z):
 p=shell_point(th,z,-WT(th));return np.hypot(p[...,0]-CENTER[0],p[...,1]-CENTER[1])
def foot_fillets(solid,paths,R=None,h=None,RW=1.5):
 """Rolling-ball fillet (radius R) of every concave corner where a rib end meets the wall.
 The perforated skin plus ribs is rasterised locally from exact sections, closed with a ball of radius R
 (dilate, then erode), and the closed region is meshed 0.7 voxel shy so it never stands proud of CAD faces.
 Only material within 8 mm of the rib centreline is kept. Inside the wall thickness (where a rib end can cross a
 wall opening and would otherwise touch its rim at a point) the ball radius is RW, small enough not to close openings."""
 from skimage.draw import polygon
 from skimage.measure import marching_cubes
 from scipy.ndimage import distance_transform_edt as edt,gaussian_filter
 from scipy.spatial import cKDTree
 R=FOOT_R if R is None else R;h=FOOT_PITCH if h is None else h;out=[];LAT=8.;pad_=R+6*h
 for pi,path in enumerate(paths):
  L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))];low=(RIB_TOP-RIB_DEPTH)*np.sin(np.pi*L/L[-1])**ARCH_P
  d=path-CENTER;rho=np.hypot(*d.T);th=np.arctan2(d[:,1],d[:,0]);mid=len(path)//2
  for end,idx in enumerate([np.arange(mid,-1,-1),np.arange(mid,len(path))]):
   top=next(i for i in idx if rho[i]>=inner_radius(th[i],RIB_TOP));last=next((i for i in idx if rho[i]>=inner_radius(th[i],0.)+1.),idx[-1])
   seg=path[(L>=min(L[top],L[last])-R-14)&(L<=max(L[top],L[last])+2)]
   lo=np.r_[seg.min(0)-LAT-pad_,-pad_];hi=np.r_[seg.max(0)+LAT+pad_,RIB_TOP+R+1.5+pad_]
   xs=np.arange(lo[0],hi[0],h)+h/2;ys=np.arange(lo[1],hi[1],h)+h/2;zs=np.arange(lo[2],hi[2],h)+h/2
   area=lambda q:np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))/2;cube=Manifold.cube(tuple(hi-lo+2*h)).translate(tuple(lo-h))
   def raster(man):
    local=man^cube;a=np.zeros((len(zs),len(ys),len(xs)),bool)
    for k,z in enumerate(zs):
     if z<=0:continue
     for q in sorted(local.slice(float(z)).to_polygons(),key=lambda q:abs(area(q)),reverse=True):
      rr,cc=polygon((q[:,1]-ys[0])/h,(q[:,0]-xs[0])/h,shape=a.shape[1:]);a[k,rr,cc]=area(q)>0
    return a
   occ=raster(solid)
   d0=edt(~occ,sampling=h);closed=edt(d0<=R,sampling=h)>R;closedw=edt(d0<=RW,sampling=h)>RW
   # Keep-zone as a signed distance (positive inside): lateral band, inside the wall face, below the fillet top.
   XX,YY=np.meshgrid(xs,ys);dlat=cKDTree(np.c_[np.interp(np.arange(0,L[-1],.05),L,path[:,0]),np.interp(np.arange(0,L[-1],.05),L,path[:,1])]).query(np.c_[XX.ravel(),YY.ravel()])[0].reshape(XX.shape)
   tg=np.arctan2(YY-CENTER[1],XX-CENTER[0]);rg=np.hypot(XX-CENTER[0],YY-CENTER[1])
   g0,g1,b0,b1,h0,h1,wt=SR(tg),SR(tg,1),SB(tg),SB(tg,1),SH(tg),SH(tg,1),WT(tg);depth=np.empty(occ.shape,np.float32)
   for k,z in enumerate(np.maximum(zs,0.)):   # inner_radius() with the Fourier guides evaluated once per column
    q=1-z/h0;r=g0+(b0-g0)*q*q;depth[k]=r-wt*np.sqrt(1+((g1+(b1-g1)*q*q+2*(b0-g0)*q*z*h1/(h0*h0))/r)**2+(2*(b0-g0)*q/h0)**2)-rg
   zone=np.minimum(np.minimum(LAT-dlat[None],depth+(wt-1.4)[None]),(RIB_TOP+R+1.5-zs)[:,None,None]).astype(np.float32)
   added=((closed&(depth>0))|(closedw&(depth<=0)))&~occ&(zone>0);
   region=occ|added;sd=gaussian_filter((edt(region,sampling=h)-edt(~region,sampling=h)).astype(np.float32),1.2)
   edge=added&(zone<.25)&(depth>0)&((LAT-dlat[None]<.25)|((RIB_TOP+R+1.5-zs)[:,None,None]<.25))
   FOOT_LOG.append({'rib':pi,'end':end,'near_xy_mm':path[top].round(1).tolist(),'added_volume_mm3':float(added.sum()*h**3),'added_z_range_mm':[float(zs[np.where(added.any((1,2)))[0][[0,-1]]][0]),float(zs[np.where(added.any((1,2)))[0][[0,-1]]][1])] if added.any() else None,'added_volume_cut_by_zone_edge_mm3':float(edge.sum()*h**3)})
   if not added.any():continue
   v,f,_,_=marching_cubes(np.pad(np.minimum(sd-.7*h,zone),1,constant_values=-1.),level=0.,spacing=(h,h,h),allow_degenerate=False)  # padded: closed at the box faces
   tm=trimesh.Trimesh(v[:,[2,1,0]]+[xs[0]-h,ys[0]-h,zs[0]-h],f[:,[0,2,1]],process=True);tm.fix_normals();parts=[q for q in tm.split(only_watertight=True) if q.volume>.5];assert parts
   for part in parts:
    man=Manifold(m3.Mesh64(np.asarray(part.vertices,np.float64),np.asarray(part.faces,np.uint64)));assert man.status()==m3.Error.NoError
    out.append(man.simplify(.02))
 return out
def supports(skin=None):
 paths=rib_paths();pieces=[support_wall(p) for p in paths]+crossing_fillets(paths)
 walls=Manifold.batch_boolean(pieces,m3.OpType.Add)
 if FOOT_R>0 and skin is not None:
  # Fillets are computed against the perforated skin and the same clipped ribs they will join.
  walls=Manifold.batch_boolean([walls]+foot_fillets(skin+_clip(walls),paths),m3.OpType.Add)
 return _clip(walls)+Manifold.batch_boolean([pad(*c) for c in PADS],m3.OpType.Add)
def _inner(depth,ztop=30.):
 """Solid bounded by the shell surface offset by `depth` (negative = inward), from the table to ztop."""
 n=int(round(ztop*2));verts=[]
 for z in np.linspace(0,ztop,n+1):verts.append(shell_point(TH,np.full(M,z),depth))
 verts=np.array(verts);faces=[]
 for j in range(n):
  for k in range(M):a=j*M+k;b=j*M+(k+1)%M;c=b+M;d=a+M;faces.extend([[a,b,c],[a,c,d]])
 for k in range(1,M-1):faces.extend([[0,k+1,k],[n*M,n*M+k,n*M+k+1]])
 tm=trimesh.Trimesh(verts.reshape(-1,3),faces);tm.fix_normals();return Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)))
def _clip(walls):
 # Clip support ends to the inside of the shell; they stay under its quiet rim.
 return walls^_inner(-1.6)

EXPORT_TOL={}
def export_mesh(body,tol=.008,name=None):
 # The float32 STL occasionally loses watertightness at one simplification tolerance; step to a finer one.
 for t in [tol,.006,.005,.004]:
  mm=body.as_original().set_tolerance(t).simplify(t).to_mesh64();vv=np.asarray(mm.vert_properties)[:,:3];ff=np.asarray(mm.tri_verts);remap=np.arange(len(vv));remap[np.asarray(mm.merge_from_vert,int)]=np.asarray(mm.merge_to_vert,int)
  while np.any(remap[remap]!=remap):remap=remap[remap]
  tm=trimesh.Trimesh(np.float32(vv),remap[ff],process=True);tm.update_faces(tm.nondegenerate_faces());tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices()
  if tm.is_watertight and tm.is_winding_consistent and tm.body_count==1:
   if name:EXPORT_TOL[name]=t
   return tm
 raise AssertionError('no watertight export at any tolerance')

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);print('Building continuous perforated shell',flush=True)
 skin=shell()-apertures();print('Building concealed flowing support paths',flush=True);body=skin+supports(skin);body=body-Manifold.extrude(CAV,100).translate((0,0,30));body=body^Manifold.cube((400,400,100)).translate((-200,-200,0))
 parts=sorted(body.decompose(),key=lambda p:-p.volume());print('Bodies',len(parts),[p.volume() for p in parts],flush=True)
 # Booleans against the voxel-derived fillets can leave zero-volume slivers; anything measurable is still an error.
 assert all(abs(p.volume())<1e-3 for p in parts[1:]);body=parts[0]
 mesh=export_mesh(body,name='stand')
 for ext in ['stl','3mf']:mesh.export(OUT/f'veil_v14_prototype.{ext}')
 np.savez_compressed(OUT/'mesh.npz',V=mesh.vertices,F=mesh.faces)
 gauge=export_mesh(Manifold.extrude(CAV.offset(4)-CAV,1.6));gauge.export(OUT/'GAUGE_v14_cavity_1.6mm.stl')
 clip=Manifold.cube((58,36,80)).translate((22,34,0));coupon=max((body^clip).decompose(),key=lambda p:p.volume())
 test=export_mesh(coupon,name='coupon');test.apply_translation(-test.bounds[0]);test.export(OUT/'PRINT_TEST_v14_section.stl')
 ((OUT.parent/'analysis' if (OUT.parent/'analysis').is_dir() else OUT)/'foot_fillets.json').write_text(json.dumps({'radius_mm':FOOT_R,'radius_inside_wall_thickness_mm':1.5,'voxel_pitch_mm':FOOT_PITCH,'export_simplify_tolerance_mm':EXPORT_TOL,'feet':FOOT_LOG},indent=1));print('Foot fillets',json.dumps(FOOT_LOG),flush=True)
 print('Final dimensions',mesh.extents,'volume cm3',mesh.volume/1000,'faces',len(mesh.faces),flush=True)
