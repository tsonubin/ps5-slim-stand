"""Linear-elastic solid FE screening; assumed isotropic material and clamped feet."""
from pathlib import Path
import sys,os,json,time
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np,trimesh
from scipy.sparse.linalg import cg
import pyamg
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from shapely.geometry import Polygon
from shapely import contains_xy
p=Path(sys.argv[1]);dest=Path(sys.argv[2]);a=np.load(p);nodes=a['nodes'];elements=a['elements'];vol=a['volumes']
mesh=MeshTet(nodes.T,elements.T);basis=Basis(mesh,ElementVector(ElementTetP1()),intorder=1)
E=1200.;nu=.35;lam,mu=lame_parameters(E,nu)
print('Assemble',len(nodes),len(elements),'DOFs',basis.N,flush=True)
t=time.time();K=asm(linear_elasticity(lam,mu),basis).tocsr();print('K',K.shape,K.nnz,'sec',time.time()-t,flush=True)
regularized=True
bottom=np.where(nodes[:,2]<(nodes[:,2].min()+.2 if regularized else 1e-4))[0];fixed=basis.nodal_dofs[:,bottom].ravel();free=np.setdiff1d(np.arange(basis.N),fixed)
A=K[free][:,free].tocsr()
# Six near-nullspace rigid-body modes for elasticity multigrid.
B=np.zeros((basis.N,6));xyz=nodes-nodes.mean(axis=0)
for j in range(3):B[basis.nodal_dofs[j],j]=1
for j,axis in enumerate(np.eye(3)):
 B[basis.nodal_dofs.ravel(order='F'),j+3]=np.cross(np.broadcast_to(axis,xyz.shape),xyz).ravel()
print('Preconditioner',flush=True);t=time.time()
ml=pyamg.smoothed_aggregation_solver(A,B=B[free],symmetry='symmetric',max_coarse=300)
M=ml.aspreconditioner();print('AMG sec',time.time()-t,flush=True)
root=Path(__file__).resolve().parents[3]
scene=trimesh.load(root/'references/console-model/PS5_Slim.glb');core=scene.geometry['unnamed_6'].section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
poly=max((Polygon(c[:,:2]) for c in core.discrete if np.linalg.norm(c[0]-c[-1])<.01),key=lambda p:p.area)
facets=mesh.facets[:,mesh.boundary_facets()].T;tri=nodes[facets];cent=tri.mean(axis=1)
areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); nz=abs(normals[:,2])/np.maximum(2*areas,1e-12)
seat=(np.max(abs(tri[:,:,2]-30),axis=1)<(.3 if regularized else 1e-4))&(nz>.9)&contains_xy(poly,cent[:,0],cent[:,1])
assert seat.any();print('Seat area',areas[seat].sum(),'bottom nodes',len(bottom),flush=True)
results={};fields={};centroid=nodes[elements].mean(axis=1)
cases=[('vertical_1g',seat),('eccentric_1g',seat&(cent[:,0]>8))]
if nodes[:,2].max()>35:cases.append(('rim_side_10N',seat))
if os.environ.get('FEA_CASE'): cases=[(c,m) for c,m in cases if c==os.environ['FEA_CASE']]
for case,mask in cases:
 weights=np.zeros(len(nodes));np.add.at(weights,facets[mask].ravel(),np.repeat(areas[mask]/3,3));weights/=weights.sum()
 load_centroid=(weights[:,None]*nodes).sum(axis=0)
 f=np.zeros(basis.N);f[basis.nodal_dofs[2]]=-3.2*9.81*weights
 if case=='rim_side_10N':
  rim=(cent[:,0]>40)&(cent[:,1]>15)&(cent[:,1]<100)&(cent[:,2]>36)
  assert rim.any();wx=np.zeros(len(nodes));np.add.at(wx,facets[rim].ravel(),np.repeat(areas[rim]/3,3));wx/=wx.sum()
  f[basis.nodal_dofs[0]]=10*wx
 rhs=f[free];count=[0]
 def callback(_):count[0]+=1
 print('Solve',case,flush=True);t=time.time();sol,info=cg(A,rhs,M=M,rtol=1e-8,atol=0,maxiter=2000,callback=callback)
 u=np.zeros(basis.N);u[free]=sol;res=float(np.linalg.norm(A@sol-rhs)/np.linalg.norm(rhs))
 assert info==0 and res<1e-6,(info,res)
 du=basis.interpolate(u).grad.mean(axis=3);eps=(du+du.swapaxes(0,1))/2
 stress=2*mu*eps+lam*np.einsum('iik->k',eps)[None,None,:]*np.eye(3)[:,:,None]
 dev=stress-np.einsum('iik->k',stress)[None,None,:]/3*np.eye(3)[:,:,None]
 vm=np.sqrt(1.5*np.sum(dev*dev,axis=(0,1)));displ=u[basis.nodal_dofs].T
 reaction=K@u-f;R=np.array([reaction[np.intersect1d(fixed,basis.nodal_dofs[j])].sum() for j in range(3)])
 order=np.argsort(vm);p95=float(vm[order[np.searchsorted(np.cumsum(vol[order]),.95*vol.sum())]])
 peak=int(vm.argmax())
 results[case]={'iterations':count[0],'relative_residual':res,'max_displacement_mm':float(np.linalg.norm(displ,axis=1).max()),'max_seat_down_mm':float(-displ[weights>0,2].min()),'peak_von_mises_MPa':float(vm.max()),'volume_weighted_p95_von_mises_MPa':p95,'peak_element_center_mm':centroid[peak].tolist(),'support_reaction_N':R.tolist(),'support_reaction_moment_Nmm':np.cross(nodes,reaction[basis.nodal_dofs].T).sum(axis=0).tolist(),'applied_force_N':[10 if case=='rim_side_10N' else 0,0,-31.392],'seat_pressure_area_mm2':float(areas[mask].sum()),'vertical_load_centroid_mm':load_centroid.tolist(),'load_moment_about_origin_Nmm':np.cross(nodes,f[basis.nodal_dofs].T).sum(axis=0).tolist(),'side_patch_area_mm2':float(areas[rim].sum()) if case=='rim_side_10N' else 0.,'side_patch_centroid_mm':(wx[:,None]*nodes).sum(axis=0).tolist() if case=='rim_side_10N' else None,'compliance_Nmm':float(f@u),'solve_seconds':time.time()-t}
 print(case,results[case],flush=True);fields[case+'_u']=displ;fields[case+'_vm']=vm
if 'vertical_1g' in results: results['vertical_3g_linear_scaling']={k:results['vertical_1g'][k]*3 for k in ['max_displacement_mm','max_seat_down_mm','peak_von_mises_MPa','volume_weighted_p95_von_mises_MPa']}
report={'surface_mesh':str(p),'nodes':len(nodes),'tets':len(elements),'solid_volume_mm3':float(vol.sum()),'fixed_node_count':len(bottom),'regularized_contact_tolerance_mm':.3,'upper_shell_patch_rule':'x > 40, 15 < y < 100, z > 36 mm; local stand push, not console-top force','material_assumption':{'E_MPa':E,'nu':nu,'model':'Isotropic homogeneous linear elastic. Not measured printed properties.'},'boundary':('Complete stand on a regularized geometry: feet within0.2mm of minimum Z are clamped; seat faces within0.3mm of Z30, nearly horizontal and inside reference core, carry pressure. Isotropic small-displacement screen; no slip/lift-off or material failure.'),'seat_area_mm2':float(areas[seat].sum()),'results':results}
dest.parent.mkdir(parents=True,exist_ok=True);dest.with_suffix('.json').write_text(json.dumps(report,indent=2));np.savez_compressed(dest.with_suffix('.npz'),nodes=nodes,elements=elements,volumes=vol,**fields)
