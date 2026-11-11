import numpy as np,json
from run_screen import run,ROOT
nx,ny,nz=42,22,12
t=np.ones((nz,ny,nx),np.uint8);t[[0,-1]]=0;t[:,[0,-1]]=0;t[1:-1,1:-1,0]=2;t[1:-1,1:-1,-1]=3
z,y,x=np.indices(t.shape);ref=np.ravel_multi_index((np.clip(z,1,nz-2),np.clip(y,1,ny-2),np.clip(x,1,nx-2)),t.shape)
r=run('duct_benchmark',t,ref,(np.arange(nx),np.arange(ny),np.arange(nz)),1,6500)
w,h,L=20,10,41
n=np.arange(1,1000,2);factor=1-192*h/(np.pi**5*w)*np.sum(np.tanh(n*np.pi*w/(2*h))/n**5)
Q=w*h**3/(12*.1*L)*(1e-5/3)*factor
r['analytical_rectangular_duct_flux']=float(Q);r['relative_flux_error']=abs(r['qout_lattice']/Q-1);(ROOT/'duct_benchmark.json').write_text(json.dumps(r,indent=2));print(r)
