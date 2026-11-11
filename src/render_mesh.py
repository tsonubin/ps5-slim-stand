"""Actual triangle rasterization, perspective-correct z-buffer, no geometry changes.
Flat shading is the default for honest junction inspection. Optional crease-limited
vertex normals improve overview rendering without bridging sharp normal changes.
Requires Python numpy/trimesh/Pillow and a local C++ compiler; binary cached in /tmp.
"""
from pathlib import Path
import hashlib,subprocess,tempfile
import numpy as np
from PIL import Image

def look_at(eye,target):
    back=np.asarray(eye,float)-target;back/=np.linalg.norm(back)
    up=np.array([0.,0.,1.])
    if abs(back@up)>.99:up=np.array([0.,1.,0.])
    right=np.cross(up,back);right/=np.linalg.norm(right)
    up=np.cross(back,right)
    return np.array([right,up,back])

def render(mesh,eye,target,W=1000,H=800,fov=26,ss=2,color=(.92,.94,.97),smooth=False):
    cpp=Path(__file__).with_name('raster_mesh.cpp');digest=hashlib.sha256(cpp.read_bytes()).hexdigest()[:14]
    binary=Path(tempfile.gettempdir())/f'veil-raster-{digest}'
    if not binary.exists():subprocess.run(['clang++','-O3','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    eye=np.asarray(eye,float);target=np.asarray(target,float);R=look_at(eye,target)
    V=np.asarray(mesh.vertices);F=np.asarray(mesh.faces,dtype=np.uint32);Q=(V-eye)@R.T
    foc=.5*H*ss/np.tan(np.radians(fov)/2);z=-Q[:,2]
    screen=np.c_[W*ss/2+foc*Q[:,0]/z,H*ss/2-foc*Q[:,1]/z,1/z].astype(np.float32)
    normal=np.broadcast_to(mesh.face_normals[:,None,:],(len(F),3,3)).copy()
    if smooth:
        avg=mesh.vertex_normals[F]
        # Never smooth a corner whose averaged normal differs > 20 degrees.
        mask=np.sum(avg*normal,axis=2)>np.cos(np.radians(20))
        normal[mask]=avg[mask]
    normal=(normal@R.T).astype(np.float32)
    colors=np.broadcast_to(np.asarray(color,np.float32),(len(F),3)).copy()
    payload=np.array([W*ss,H*ss,len(V),len(F)],np.uint32).tobytes()+np.array([.055,.066,.085],np.float32).tobytes()+colors.tobytes()+screen.tobytes()+F.tobytes()+normal.tobytes()
    run=subprocess.run([str(binary)],input=payload,stdout=subprocess.PIPE,check=True)
    im=Image.fromarray(np.frombuffer(run.stdout,np.uint8).reshape(H*ss,W*ss,3))
    return im.resize((W,H),Image.Resampling.LANCZOS) if ss!=1 else im
