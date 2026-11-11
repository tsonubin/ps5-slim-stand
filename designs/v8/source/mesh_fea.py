from pathlib import Path
import sys,time,json,os
import numpy as np,trimesh,tetgen
p=Path(sys.argv[1]);vol=float(sys.argv[2]);out=Path(sys.argv[3]);out.parent.mkdir(parents=True,exist_ok=True)
m=trimesh.load(p);assert m.is_watertight and m.body_count==1
print('Input',len(m.vertices),len(m.faces),'volume',m.volume,flush=True)
t=time.time();gen=tetgen.TetGen(np.asarray(m.vertices),np.int32(m.faces))
if os.environ.get('FEA_NO_OPT')=='1':
 nodes,elements,_,_=gen.tetrahedralize(order=1,quality=False,nobisect=True,opt_scheme=0,opt_iterations=0,steinerleft=60000,quiet=True)
elif os.environ.get('FEA_NO_OPT')=='3':
 nodes,elements,_,_=gen.tetrahedralize(order=1,quality=True,nobisect=True,minratio=1.4,maxvolume=vol,fixedvolume=True,opt_scheme=0,opt_iterations=0,steinerleft=180000,quiet=True)
elif os.environ.get('FEA_NO_OPT')=='2':
 nodes,elements,_,_=gen.tetrahedralize(order=1,quality=True,nobisect=True,minratio=2.,maxvolume=vol,fixedvolume=True,opt_scheme=0,opt_iterations=0,steinerleft=90000,quiet=True)
else:
 nodes,elements,_,_=gen.tetrahedralize(order=1,minratio=2.,mindihedral=0,maxvolume=vol,fixedvolume=True,steinerleft=60000,quiet=True)
a=nodes[elements];volumes=np.abs(np.linalg.det(a[:,1:]-a[:,:1]))/6
print('TetGen',len(nodes),len(elements),'volume',volumes.sum(),'time',time.time()-t,flush=True)
assert abs(volumes.sum()/m.volume-1)<.002
np.savez_compressed(out,nodes=nodes,elements=elements,volumes=volumes)
