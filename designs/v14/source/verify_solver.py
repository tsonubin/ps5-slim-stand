"""Analytical uniaxial-compression check for the same solid FE formulation."""
import numpy as np,json
from pathlib import Path
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm,condense,solve
from skfem.models.elasticity import linear_elasticity,lame_parameters
m=MeshTet.init_tensor(np.linspace(0,10,5),np.linspace(0,10,5),np.linspace(0,30,9));b=Basis(m,ElementVector(ElementTetP1()),intorder=1)
lam,mu=lame_parameters(1200.,.35);K=asm(linear_elasticity(lam,mu),b)
facets=m.facets[:,m.boundary_facets()].T;tri=m.p.T[facets];top=np.all(abs(tri[:,:,2]-30)<1e-6,axis=1)
area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
f=np.zeros(b.N);nodal=np.zeros(m.nvertices);np.add.at(nodal,facets[top].ravel(),np.repeat(-31.392/100*area[top]/3,3));f[b.nodal_dofs[2]]=nodal
D=np.concatenate([b.nodal_dofs[j,np.where(abs(m.p[j])<1e-8)[0]] for j in range(3)])
u=solve(*condense(K,f,D=D));uz=u[b.nodal_dofs[2,np.where(abs(m.p[2]-30)<1e-8)[0]]]
expected=-31.392*30/(1200*100);err=float(np.max(abs(uz-expected))/abs(expected));assert err<1e-8
r={'test':'10x10x30mm block, uniaxial compression, traction0.31392MPa, lateral symmetry constraints','E_MPa':1200,'analytical_top_z_mm':expected,'FE_top_z_range_mm':[float(uz.min()),float(uz.max())],'relative_error':err,'passed':True}
(Path(__file__).resolve().parents[1]/'analysis/solver_benchmark.json').write_text(json.dumps(r,indent=2));print(r)
