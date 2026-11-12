"""Localized additive polynomial smooth unions of round ring and strand roots.
Only the small root neighborhoods are sampled; the main CAD remains analytic sweeps.
"""
import numpy as np
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
import trimesh,time

def distance(points,curve,radius):
    tree=cKDTree(curve);_,nearest=tree.query(points,workers=1)
    best=np.full(len(points),np.inf)
    for delta in [-1,0]:
        j=np.clip(nearest+delta,0,len(curve)-2);a=curve[j];b=curve[j+1];ab=b-a
        t=np.clip(np.sum((points-a)*ab,axis=1)/np.sum(ab*ab,axis=1),0,1)
        r=radius[j]*(1-t)+radius[j+1]*t
        best=np.minimum(best,np.linalg.norm(points-(a+t[:,None]*ab),axis=1)-r)
    return best

def junction_patches(wires,ring_curve,Manifold,m3,pitch=.20,blend=.85):
    patches=[];records=[];start=time.time()
    for wi,w in enumerate(wires):
        for top in (False,True):
            sl=slice(-121,None) if top else slice(0,121)
            curve=w['points'][sl];radius=w['radius'][sl];th0=w['theta'][-1 if top else 0]
            th=np.linspace(th0-.43,th0+.43,601);ring=ring_curve(th,top);rr=2.4 if top else 3.
            # Intersection of expanded tube bounds limits every implicit patch.
            lo=np.maximum(curve.min(0)-radius.max()-blend,ring.min(0)-rr-blend)
            hi=np.minimum(curve.max(0)+radius.max()+blend,ring.max(0)+rr+blend)
            lo=np.floor(lo/pitch)*pitch;hi=np.ceil(hi/pitch)*pitch
            axes=[np.arange(lo[j],hi[j]+pitch*.5,pitch) for j in range(3)]
            shape=tuple(len(a) for a in axes);p=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
            d1=distance(p,curve,radius);d2=distance(p,ring,np.full(len(ring),rr))
            # Blend tapers smoothly to zero before each patch boundary.
            edge=np.min(np.minimum(p-lo,hi-p),axis=1);q=np.clip((edge-.5)/1.2,0,1);q=q*q*(3-2*q);k=blend*q
            h=np.clip(.5+.5*(d2-d1)/np.maximum(k,1e-9),0,1)
            f=(1-h)*d2+h*d1-k*h*(1-h)
            f=np.maximum(f,.5*pitch-edge).reshape(shape).astype(np.float32)
            vv,ff,_,_=marching_cubes(f,0,spacing=(pitch,)*3,allow_degenerate=False)
            tm=trimesh.Trimesh(vv+lo,ff,process=True);tm.fix_normals()
            assert tm.is_watertight
            patch=Manifold(m3.Mesh64(np.asarray(tm.vertices,np.float64),np.asarray(tm.faces,np.uint64)))
            assert patch.status()==m3.Error.NoError
            patches.append(patch);records.append({'wire':wi,'top':top,'bounds_mm':[lo.tolist(),hi.tolist()],'faces':len(ff),'grid_shape':list(shape)})
        if wi%10==0:print('Root fillets',wi+1,'/',len(wires),'seconds',round(time.time()-start,1),flush=True)
    return patches,{'method':'Local polynomial smooth-min round-tube distance fields; additive union with exact swept CAD. Blend tapers over 1.2mm and is exactly zero throughout the outer 0.5mm of each patch. No global voxelization.','pitch_mm':pitch,'smooth_min_k_mm':blend,'maximum_implicit_distance_offset_mm':blend/4,'patches':records,'limitations':'Tube distances use nearest sampled polyline segments; marching-cubes patches approximate surfaces. Centerline tangency is not proof of exact G1 continuity of final Boolean/triangulated junctions.'}
