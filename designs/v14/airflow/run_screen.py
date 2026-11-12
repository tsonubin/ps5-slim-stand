from pathlib import Path
import sys,json,subprocess,hashlib,os
import numpy as np,trimesh,manifold3d as m3
from skimage.draw import polygon
ROOT=Path(__file__).resolve().parent; REVERSE='--reverse' in sys.argv; CAD=Path(os.environ['VEIL_CAD']) if os.environ.get('VEIL_CAD') else ROOT.parent/'output/veil_v14_prototype.stl';PREFIX=os.environ.get('VEIL_PREFIX','')
def run(name,t,ref,xyz,h,maxit=6500):
 name=name.replace('.','p');name+=('_reverse' if REVERSE else ''); p=ROOT/name; shape=t.shape;nx,ny,nz=shape[::-1]
 with p.with_suffix('.bin').open('wb') as f:
  np.array([nx,ny,nz],np.int32).tofile(f);t.tofile(f);ref.astype(np.int32).tofile(f)
 with p.with_suffix('.log').open('w') as log:
  r=subprocess.run([os.environ.get('VEIL_LBM','/tmp/veil-lbm'),str(p.with_suffix('.bin')),str(p.with_suffix('.field')),str(maxit),str(-1e-5 if REVERSE else 1e-5)],stdout=subprocess.PIPE,stderr=log,text=True,check=True)
 a=np.fromfile(p.with_suffix('.field'),np.float32).reshape(*shape,4);v=a[...,1:];rho=a[...,0]; fluid=t==1
 # Flux through first interior layer adjacent to each reservoir; port uses vertical face.
 port=t[-1]==3;qout=float((v[-2,:,:,2]*rho[-2])[port].sum());qin=0
 for axis in [1,2]:
  for edge,inner,sg in [(0,1,1),(-1,-2,-1)]:
   sel=[slice(None)]*3;sel[axis]=inner;boundary=[slice(None)]*3;boundary[axis]=edge
   mask=t[tuple(boundary)]==2; vv=v[tuple(sel)][...,2-axis];rr=rho[tuple(sel)];qin+=float((vv*rr)[mask].sum()*sg)
 result=json.loads(r.stdout);qout=result['link_flux_out'];qin=result['link_flux_in'];result.update(name=name,pitch_mm=h,shape=list(shape),fluid_nodes=int(fluid.sum()),port_area_mm2=float(port.sum()*h*h),qout_lattice=qout,qin_lattice=qin,mass_imbalance_fraction=abs(qin-qout)/max(abs(qout),1e-20),max_speed_lattice=float(np.linalg.norm(v[fluid],axis=1).max()),tau=.8,kinematic_viscosity_lattice=.1,density_difference=(-1e-5 if REVERSE else 1e-5))
 result['conductance_scaled']=qout*.1*h**3/(1e-5/3)
 np.savez_compressed(p.with_suffix('.npz'),t=t,field=a,x=xyz[0],y=xyz[1],z=xyz[2]);p.with_suffix('.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
 p.with_suffix('.bin').unlink();p.with_suffix('.field').unlink();return result

def main(h,loc=0):
 x=np.arange(-90+h/2,101,h);y=np.arange(-140+h/2,141,h);z=np.arange(-h/2,30+h,h)
 # first and last layers are boundary reservoirs/walls, halfway solid desk is z=0.
 shape=(len(z),len(y),len(x));base=np.ones(shape,np.uint8);base[0]=0;base[-1]=0
 XX,YY=np.meshgrid(x,y)
 if loc=='core':
  # Suction over the whole flat underside of the reference console core (vent map unknown).
  from shapely.geometry import Polygon
  from shapely import contains_xy
  sec=trimesh.load(ROOT.parents[2]/'references/console-model/PS5_Slim.glb').geometry['unnamed_6'].section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
  poly=max((Polygon(c[:,:2]) for c in sec.discrete if np.linalg.norm(c[0]-c[-1])<.01),key=lambda q:q.area);port=contains_xy(poly,XX,YY)
 else:port=(XX**2+(YY-loc)**2<15**2)
 base[-1,port]=3
 base[1:-1,:,0]=2;base[1:-1,:,-1]=2;base[1:-1,0,:]=2;base[1:-1,-1,:]=2
 zz,yy,xx=np.indices(shape);refs=np.ravel_multi_index((np.clip(zz,1,len(z)-2),np.clip(yy,1,len(y)-2),np.clip(xx,1,len(x)-2)),shape)
 mesh=trimesh.load(CAD);body=m3.Manifold(m3.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)));assert body.status()==m3.Error.NoError
 solid=np.zeros(shape,bool)
 for k,hh in enumerate(z):
  loops=body.slice(float(hh)).to_polygons();signed=lambda q:np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))/2
  for q in sorted(loops,key=lambda a:abs(signed(a)),reverse=True):
   rr,cc=polygon((q[:,1]-y[0])/h,(q[:,0]-x[0])/h,shape=shape[1:]);solid[k,rr,cc]=signed(q)>0
 for key in (['stand'] if REVERSE else ['empty','stand']):
  t=base.copy()
  if key=='stand':
   t[solid]=0
   t[-1][(t[-1]==3)&(t[-2]==0)]=0
  assert np.all(t.ravel()[refs[t>=2]]==1), 'Boundary needs fluid extrapolation neighbor'
  run(PREFIX+f'{key}_{h:g}mm_port'+(loc if loc=='core' else f'{loc:g}'),t,refs,(x,y,z),h)
if __name__=='__main__':main(float(sys.argv[1]),(sys.argv[2] if sys.argv[2]=='core' else float(sys.argv[2])) if len(sys.argv)>2 else 0)
