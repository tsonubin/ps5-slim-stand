"""Veil v10 development prototype. Units mm. No physical fit or thermal certification.
Continuous mapped mesh surfaces replace v5 stacked slabs. Source outline retained.
Run from any folder: python veil_v10.py OUTPUT_DIRECTORY
"""
import sys, os, math, json
import numpy as np
import manifold3d as m3
from manifold3d import CrossSection as CS, Manifold
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
HERE = os.path.dirname(os.path.abspath(__file__))
OL = json.load(open(os.path.join(HERE, "outline.json")))
OY = np.array(OL["y"])[::-1]; O_PLAIN = np.array(OL["plain"])[::-1]; O_DISC = np.array(OL["disc"])[::-1]
def hwL(y): return float(np.interp(y, OY, O_PLAIN))
def hwR(y): return float(np.interp(y, OY, O_DISC))

CLEAR  = 1.5            # loose fit around the console
H0     = 30.0           # lift: console base above desk
RIM_T  = 3.6            # rim thickness at the top edge
SKIN_T = 2.4
RIB_T  = 3.2
SUPPORT = "sleek"
P_FLARE, FLARE_SIDE, FLARE_END, LEAN_MAX = 1.35, 21.8, 4.8, 0.75
N_ROWS, KAPPA, STRUT_W = 2.6, 0.30, 3.8       # diamond rows, cell width / rim height, strut width
RIM_BAND, BASE_BAND = 4.0, 4.8
CENTER = np.array([8.0, 0.0])
M = 1080
# rim height above the desk at landmarks around the console (x, y, height)
LANDMARKS = [(8,108,34),(-40,104,44),(-39,68,55),(-34,0,40),(-27,-66,43),(0,-108,33),
             (55,-92,38),(55,-66,46),(52,0,42),(45,76,49),(39,104,40)]
m3.set_circular_segments(48)

def console_plan():
    ys = np.arange(-108, 108.01, 1.5)
    return CS([[(hwR(y), y) for y in ys] + [(-hwL(y), y) for y in ys[::-1]]])
PLAN = console_plan(); CAV = PLAN.offset(CLEAR)
TH = np.linspace(-np.pi, np.pi, M, endpoint=False); U = np.c_[np.cos(TH), np.sin(TH)]

def radial(cs):
    poly = max(cs.to_polygons(), key=len) - CENTER; A = poly; E = np.roll(poly, -1, 0) - poly
    den = U[:, None, 0] * E[None, :, 1] - U[:, None, 1] * E[None, :, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (A[None, :, 0] * E[None, :, 1] - A[None, :, 1] * E[None, :, 0]) / den
        u = (A[None, :, 0] * U[:, None, 1] - A[None, :, 1] * U[:, None, 0]) / den
    ok = (u >= 0) & (u <= 1) & (t > 0)
    assert (ok.sum(1) <= 2).all() and ok.any(1).all(), "outline not star-shaped about CENTER"
    return np.where(ok, t, -1).max(1)
def smooth(a, sig): return gaussian_filter1d(a, sig, mode="wrap")
def arc(r):
    P = CENTER + r[:, None] * U; return np.linalg.norm(np.roll(P, -1, 0) - P, axis=1)

R_C = radial(CAV); R_RIM = np.maximum(smooth(radial(PLAN.offset(CLEAR + RIM_T)), 12), R_C + 2.4)
# rim height R(theta)
lm = sorted((math.atan2(y - CENTER[1], x - CENTER[0]), h) for x, y, h in LANDMARKS)
la = np.array([a for a, _ in lm]); lh = np.array([h for _, h in lm])
RIMH = smooth(PchipInterpolator(np.r_[la - 2 * np.pi, la, la + 2 * np.pi], np.r_[lh, lh, lh])(TH), 22)
# flare
ycoord = (CENTER + R_RIM[:, None] * U)[:, 1]
tt = np.clip((104 - np.abs(ycoord)) / 45, 0, 1); FL = FLARE_END + (FLARE_SIDE - FLARE_END) * tt * tt * (3 - 2 * tt)
FL = smooth(np.minimum(FL, LEAN_MAX * RIMH / P_FLARE), 8)
# A broad, smooth asymmetrical envelope; inner fit outline stays untouched.
R_BASE = smooth(R_RIM + FL, 26) + 2.0*(1+np.cos(TH-0.6))
FL = np.maximum(R_BASE-R_RIM, 5.0)
R_BASE = R_RIM+FL
COSA = R_RIM / np.sqrt(R_RIM ** 2 + (np.gradient(R_RIM, TH)) ** 2)
# lattice coordinate: cells scale with the local rim height
ds = arc(R_BASE); sig = np.cumsum(ds / (KAPPA * RIMH)); NCELL = 28; SIG = sig * NCELL / sig[-1]
CELLW = KAPPA * RIMH * sig[-1] / NCELL

def r_out(z):
    zeta = np.clip(z / RIMH, 0, 1); return R_RIM + FL * (1 - zeta) ** P_FLARE

from pathlib import Path
import trimesh

def interp(a, th):
    return np.interp((th + np.pi) % (2*np.pi) - np.pi, np.r_[TH, np.pi], np.r_[a,a[0]])

def solid_rings(rings, closed=False):
    """Loft rectangular cross sections without Z terraces; consistently closed manifold."""
    rings=np.asarray(rings); ns,nv,_=rings.shape; faces=[]
    for i in range(ns if closed else ns-1):
        j=(i+1)%ns
        for k in range(nv):
            l=(k+1)%nv; a=i*nv+k; b=i*nv+l; c=j*nv+l; d=j*nv+k
            faces.extend([[a,b,c],[a,c,d]])
    if not closed:
        for k in range(1,nv-1):
            faces.extend([[0,k+1,k],[(ns-1)*nv,(ns-1)*nv+k,(ns-1)*nv+k+1]])
    tm=trimesh.Trimesh(rings.reshape(-1,3), faces,process=True)
    tm.fix_normals()
    man=Manifold(m3.Mesh64(np.asarray(tm.vertices,dtype=np.float64),np.asarray(tm.faces,dtype=np.uint64)))
    assert man.status()==m3.Error.NoError, man.status()
    return man

def xyz(th,z,inner=False):
    h=interp(RIMH,th); r=interp(R_RIM,th)+interp(FL,th)*(1-np.clip(z/h,0,1))**P_FLARE
    if inner: r-=SKIN_T/np.maximum(interp(COSA,th),0.3)
    return [CENTER[0]+r*np.cos(th), CENTER[1]+r*np.sin(th),z]

def band(top=False):
    rings=[]
    for th in TH:
        h=interp(RIMH,th); lo=h-RIM_BAND if top else 0; hi=h if top else BASE_BAND
        if top:
            # Inner lip follows original clearance envelope; bottom tapered to shell.
            ri=interp(R_C,th)
            rings.append([xyz(th,lo),xyz(th,hi),[CENTER[0]+ri*np.cos(th),CENTER[1]+ri*np.sin(th),hi],xyz(th,lo,True)])
        else:
            radial=np.array([np.cos(th),np.sin(th),0.])
            rings.append([np.array(xyz(th,lo))+2*radial,np.array(xyz(th,hi))+radial,
                          np.array(xyz(th,hi))-5*radial,np.array(xyz(th,lo))-5.4*radial])
    return solid_rings(rings,True)

def wire_profiles():
    """A unified round filament; user rejected symbol-profile wires."""
    return [np.c_[np.cos(np.linspace(0,2*np.pi,24,endpoint=False)),np.sin(np.linspace(0,2*np.pi,24,endpoint=False))]*1.65]

def sweep_wire(points,profile):
    points=np.asarray(points);t=np.gradient(points,axis=0);t/=np.linalg.norm(t,axis=1)[:,None]
    radial=np.c_[points[:,:2]-CENTER,np.zeros(len(points))]
    radial-=np.sum(radial*t,axis=1)[:,None]*t;radial/=np.linalg.norm(radial,axis=1)[:,None]
    tangent=np.cross(t,radial)
    scale=np.ones(len(points))
    return solid_rings(points[:,None,:]+scale[:,None,None]*(profile[None,:,0,None]*radial[:,None,:]+profile[None,:,1,None]*tangent[:,None,:]))

def lattice():
    # Dense organically flowing web. Long curves share a unified round section,
    # with nonuniform spacing and changing sweep lengths instead of a cell grid.
    profile=wire_profiles()[0];pieces=[]
    for bandindex,fraction in enumerate([.36,.69]):
        points=[]
        for th in np.linspace(-np.pi,np.pi,721):
            h=interp(RIMH,th)
            z=4+(h-7)*(fraction+.12*np.sin(th+bandindex*1.7)+.065*np.cos(2*th-.4))
            q=np.array(xyz(th,z));q[:2]-=.8*np.array([np.cos(th),np.sin(th)])
            points.append(q)
        pieces.append(sweep_wire(points,profile))
    for direction,count in [(1,37),(-1,29)]:
        for k in range(count):
            phase=2*np.pi*k/count+.07*np.sin(k*2.39996)+(0.11 if direction<0 else 0);points=[]
            for v in np.linspace(0,1,221):
                sweep=.72+.32*np.sin(phase-.5)**2
                th=phase+direction*sweep*(v-.5)+.14*np.sin(np.pi*v)*np.cos(phase)+.055*np.sin(2*np.pi*v+phase)
                h=interp(RIMH,th);z=3.4+v*(h-5.0)
                q=np.array(xyz(th,z));q[:2]-=.8*np.array([np.cos(th),np.sin(th)])
                q[:2]+=.3*np.sin(np.pi*v)**2*np.sin(phase+2*np.pi*v)*np.array([np.cos(th),np.sin(th)])
                points.append(q)
            pieces.append(sweep_wire(points,profile))
    return pieces

def curved_wall(points,width=RIB_T,closed=False):
    points=np.asarray(points);d=(np.roll(points,-1,axis=0)-np.roll(points,1,axis=0)) if closed else np.gradient(points,axis=0)
    d/=np.linalg.norm(d,axis=1)[:,None];normal=np.c_[-d[:,1],d[:,0]]*width/2
    dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    length=dist[-1]+(np.linalg.norm(points[-1]-points[0]) if closed else 0)
    count=max(1,round(length/100));period=length/count
    # Broad smooth arch openings under the top chords; exterior base supplies a continuous foot.
    lower=14.0*np.sin(np.pi*dist/period)**2
    rings=[]
    for p,n,z in zip(points,normal,lower):rings.append([[*(p-n),z],[*(p+n),z],[*(p+n),H0],[*(p-n),H0]])
    return solid_rings(rings,closed)

def undercroft():
    pieces=[]
    # Three long swept rails plus two shallow transverse ties: no star hub.
    for offset in [-25.,0.,25.]:
        y=np.linspace(-130,130,261)
        x=8+offset+8*np.sin(np.pi*y/125)+3*np.sin(2*np.pi*y/250+offset/20)
        pieces.append(curved_wall(np.c_[x,y]))
    for y0 in [-48.,48.]:
        x=np.linspace(-90,105,196)
        y=y0+10*np.sin(np.pi*(x-8)/120)
        pieces.append(curved_wall(np.c_[x,y]))
    walls=Manifold.batch_boolean(pieces,m3.OpType.Add)
    # Trim supports to the shell envelope.
    sections=[]
    for z in np.linspace(0,H0,61):
        rr=r_out(z)-0.4
        sections.append(CENTER+rr[:,None]*U)
    # solid envelope as loft of perimeter rings via mesh vertices and triangle fans
    verts=np.array([np.c_[s,np.full(M,z)] for s,z in zip(sections,np.linspace(0,H0,61))])
    faces=[]
    for j in range(60):
        for k in range(M):
            a=j*M+k;b=j*M+(k+1)%M;c=b+M;d=a+M;faces.extend([[a,b,c],[a,c,d]])
    for k in range(1,M-1): faces.extend([[0,k+1,k],[60*M,60*M+k,60*M+k+1]])
    tm=trimesh.Trimesh(verts.reshape(-1,3),faces);tm.fix_normals()
    env=Manifold(m3.Mesh(np.float32(tm.vertices),np.uint32(tm.faces)))
    assert env.status()==m3.Error.NoError
    return walls^env

def to_trimesh(man,tol=0.008):
    mesh=man.as_original().set_tolerance(tol).simplify(tol).to_mesh64(); V=np.asarray(mesh.vert_properties)[:,:3];F=np.asarray(mesh.tri_verts)
    remap=np.arange(len(V));remap[np.asarray(mesh.merge_from_vert,dtype=int)]=np.asarray(mesh.merge_to_vert,dtype=int)
    # STL uses float32. Validate the actual quantized topology, not only CAD's
    # higher precision topology. Remove only zero-index-area and duplicate faces.
    tm=trimesh.Trimesh(np.float32(V),remap[F],process=True)
    good=~np.any(np.diff(np.sort(tm.faces,axis=1),axis=1)==0,axis=1)
    tm.update_faces(good);tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices()
    if not tm.is_watertight: np.savez_compressed(Path(__file__).resolve().parents[1]/'analysis/export_issue.npz',V=tm.vertices,F=tm.faces)
    assert tm.is_watertight and tm.is_winding_consistent, 'Quantized export is not closed'
    return tm

def build():
    print('Building dense unified round-filament web',flush=True)
    skin=Manifold.batch_boolean([band(),band(True)]+lattice(),m3.OpType.Add)
    print('Building curved undercroft',flush=True)
    supports=undercroft()
    if __name__=='__main__':to_trimesh(supports,.002).export(Path(OUT)/f'undercroft_{SUPPORT}.stl')
    body=skin+supports
    # No material may enter the reference-derived cavity above seating level.
    body=body-Manifold.extrude(CAV,100).translate((0,0,H0))
    return body ^ Manifold.cube((400,400,100)).translate((-200,-200,0))

if __name__=='__main__':
    out=Path(OUT);out.mkdir(parents=True,exist_ok=True)
    body=build().as_original().set_tolerance(0.015);parts=body.decompose()
    print('Connected bodies:',len(parts), 'volumes:',[round(p.volume(),2) for p in parts],flush=True)
    if len(parts)>1:
        main=max(parts,key=lambda p:p.volume()); debris=[p for p in parts if p is not main]
        residue=sum(abs(p.volume()) for p in debris)
        print('Filled sealed microvoids / removed sub-resolution residue, mm3:',residue,flush=True)
        assert residue<1.0 and all(p.volume()<0.01 for p in debris), 'Unexpected separated geometry'
        body=main
    assert len(body.decompose())==1
    tm=to_trimesh(body); assert tm.is_watertight and tm.is_winding_consistent
    for suffix in ('stl','3mf'): tm.export(out/f'veil_v10_prototype.{suffix}')
    gauge=to_trimesh(Manifold.extrude(CAV.offset(4)-CAV,1.6));gauge.export(out/'GAUGE_v10_cavity_1.6mm.stl')
    # Print a small real section before the full model, containing crossing struts,
    # curved base. Keep only the largest connected clipped piece; cut-off tips
    # are not part of this print test. This is not a structural test coupon.
    clip=Manifold.cube((58,36,80)).translate((22,34,0))
    coupon=max((body^clip).decompose(),key=lambda m:m.volume())
    test=to_trimesh(coupon);test.apply_translation(-test.bounds[0]);test.export(out/'PRINT_TEST_v10_section.stl')
    np.savez_compressed(out/'mesh.npz',V=tm.vertices,F=tm.faces)
    print('Bounds',tm.bounds,'volume cm3',tm.volume/1000,'triangles',len(tm.faces),flush=True)
