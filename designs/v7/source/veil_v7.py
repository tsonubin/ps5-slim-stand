"""Veil v7 development prototype. Units mm. No physical fit or thermal certification.
Continuous mapped mesh surfaces replace v5 stacked slabs. Source outline retained.
Run from any folder: python veil_v7.py OUTPUT_DIRECTORY
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
SUPPORT = os.environ.get("VEIL_SUPPORT", "star")
REINFORCE = os.environ.get("VEIL_REINFORCE", "1")=="1"
P_FLARE, FLARE_SIDE, FLARE_END, LEAN_MAX = 1.35, 30.0, 9.0, 0.75
N_ROWS, KAPPA, STRUT_W = 2.1, 0.30, 3.8       # diamond rows, cell width / rim height, strut width
RIM_BAND, BASE_BAND = 4.0, 4.8
CENTER = np.array([8.0, 0.0])
M = 1080
# rim height above the desk at landmarks around the console (x, y, height)
LANDMARKS = [(8, 108, 27), (-40, 104, 42), (-39, 68, 69), (-34, 0, 40), (-27, -66, 48), (0, -108, 27),
             (55, -92, 43), (55, -66, 57), (52, 0, 46), (45, 76, 59), (39, 104, 42)]
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

R_C = radial(CAV); R_RIM = radial(PLAN.offset(CLEAR + RIM_T))
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
ds = arc(R_BASE); sig = np.cumsum(ds / (KAPPA * RIMH)); NCELL = int(round(sig[-1])); SIG = sig * NCELL / sig[-1]
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
    """Positive solid wire cross-sections, not glyph-shaped holes or cells."""
    from shapely.geometry import Polygon
    circle=np.c_[np.cos(np.linspace(0,2*np.pi,24,endpoint=False)),np.sin(np.linspace(0,2*np.pi,24,endpoint=False))]*1.9
    triangle=np.c_[np.cos(np.linspace(np.pi/2,2*np.pi+np.pi/2,3,endpoint=False)),np.sin(np.linspace(np.pi/2,2*np.pi+np.pi/2,3,endpoint=False))]*3.0
    square=np.array([[-1.75,-1.75],[1.75,-1.75],[1.75,1.75],[-1.75,1.75]])
    # Solid X = two intersecting bars; its arms are not hollow outlines.
    plus=np.array([[-.8,-2.5],[.8,-2.5],[.8,-.8],[2.5,-.8],[2.5,.8],[.8,.8],[.8,2.5],[-.8,2.5],[-.8,.8],[-2.5,.8],[-2.5,-.8],[-.8,-.8]])
    rot=np.array([[1,-1],[1,1]])/np.sqrt(2); cross=plus@rot.T
    profiles=[]
    for shape in (triangle,circle,cross,square):
        poly=Polygon(shape)
        # Small corner relief retains each silhouette and reduces sharp notches.
        if len(shape)!=24:poly=poly.buffer(.2,quad_segs=2).buffer(-.4,quad_segs=2).buffer(.2,quad_segs=2)
        profiles.append(np.asarray(poly.exterior.coords)[:-1])
    return profiles

def sweep_wire(points,profile):
    points=np.asarray(points);t=np.gradient(points,axis=0);t/=np.linalg.norm(t,axis=1)[:,None]
    radial=np.c_[points[:,:2]-CENTER,np.zeros(len(points))]
    radial-=np.sum(radial*t,axis=1)[:,None]*t;radial/=np.linalg.norm(radial,axis=1)[:,None]
    tangent=np.cross(t,radial)
    scale=np.ones(len(points))
    if REINFORCE:
        # Local collar at the lower drive/rear wire-to-rib junction identified by
        # the baseline side-load FE map, preserving the glyph cross-section shape.
        distance=np.sum(((points-np.array([57.7,67.6,30.3]))/np.array([12.,12.,9.]))**2,axis=1)
        scale+=.30*np.exp(-distance)
    return solid_rings(points[:,None,:]+scale[:,None,None]*(profile[None,:,0,None]*radial[:,None,:]+profile[None,:,1,None]*tangent[:,None,:]))

def lattice():
    grid=np.r_[0,np.cumsum(arc(R_BASE))];grid=grid/grid[-1]*NCELL
    angles=np.r_[TH,np.pi]
    def angle(u):return np.interp(u%NCELL,grid,angles)
    profiles=wire_profiles();pieces=[]
    for direction in (-1,1):
        for k in range(NCELL):
            phase=2*np.pi*k/NCELL;points=[]
            for v in np.linspace(0,1,165):
                progression=v+.075*np.sin(2*np.pi*v)
                drift=.55*np.sin(np.pi*v)*np.cos(phase-.4)+.16*np.sin(2*np.pi*v)*np.sin(2*phase)
                th=angle(k+(0.31 if direction==1 else 0)+direction*N_ROWS*progression+drift)
                h=interp(RIMH,th);z=3.4+v*(h-5.0)
                q=np.array(xyz(th,z));q[:2]-=1.2*np.array([np.cos(th),np.sin(th)])
                q[:2]+=.7*np.sin(np.pi*v)**2*np.sin(phase+direction*2*np.pi*v)*np.array([np.cos(th),np.sin(th)])
                points.append(q)
            pieces.append(sweep_wire(points,profiles[(k+(direction==1))%4]))
    return pieces

def curved_wall(points,width=RIB_T,closed=False):
    points=np.asarray(points);d=(np.roll(points,-1,axis=0)-np.roll(points,1,axis=0)) if closed else np.gradient(points,axis=0)
    d/=np.linalg.norm(d,axis=1)[:,None];normal=np.c_[-d[:,1],d[:,0]]*width/2
    dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    length=dist[-1]+(np.linalg.norm(points[-1]-points[0]) if closed else 0)
    count=max(1,round(length/24));period=length/count
    # Pointed arch openings below every wall retain flat feet and top chords.
    lower=np.maximum(0, min(12,period*.45)-1.5*np.abs((dist%period)-period/2))
    rings=[]
    for p,n,z in zip(points,normal,lower):rings.append([[*(p-n),z],[*(p+n),z],[*(p+n),H0],[*(p-n),H0]])
    return solid_rings(rings,closed)

def undercroft():
    pieces=[]
    if SUPPORT=='star':
        for i in range(14):
            th=2*np.pi*i/14;u=np.array([np.cos(th),np.sin(th)]);n=np.array([-u[1],u[0]])
            end=CENTER+interp(R_BASE,th)*u
            ts=np.linspace(0,1,120);start=CENTER+8*u
            points=start+ts[:,None]*(end-start)+5*np.sin(np.pi*ts)[:,None]*n
            pieces.append(curved_wall(points))
        a=np.linspace(0,2*np.pi,360,endpoint=False)
        pieces.append(curved_wall(CENTER+np.c_[24*np.cos(a),53*np.sin(a)],closed=True))
        hub=CS.circle(11,48)-CS.circle(7.8,48)
        pieces.append(Manifold.extrude(hub,30).translate((*CENTER,0)))
    elif SUPPORT=='honeycomb':
        # Regular hexagon network, shared edges deduplicated before sweeping.
        radius=22.; edges={}
        for col in range(-4,5):
            for row in range(-5,6):
                c=np.array([8+1.5*radius*col,np.sqrt(3)*radius*(row+.5*(col%2))])
                pts=c+radius*np.c_[np.cos(np.arange(6)*np.pi/3),np.sin(np.arange(6)*np.pi/3)]
                for p,q in zip(pts,np.roll(pts,-1,axis=0)):
                    key=tuple(sorted((tuple(np.round(p,5)),tuple(np.round(q,5)))))
                    edges[key]=(p,q)
        for p,q in edges.values():pieces.append(curved_wall(np.linspace(p,q,50)))
    else:raise ValueError(SUPPORT)
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

def to_trimesh(man,tol=0.02):
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
    print('Building continuous X lattice',NCELL,'cells',flush=True)
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
    for suffix in ('stl','3mf'): tm.export(out/f'veil_v7_prototype.{suffix}')
    gauge=to_trimesh(Manifold.extrude(CAV.offset(4)-CAV,1.6));gauge.export(out/'GAUGE_v7_cavity_1.6mm.stl')
    # Print a small real section before the full model, containing crossing struts,
    # curved base. Keep only the largest connected clipped piece; cut-off tips
    # are not part of this print test. This is not a structural test coupon.
    clip=Manifold.cube((50,32,80)).translate((45,-16,0))
    coupon=max((body^clip).decompose(),key=lambda m:m.volume())
    test=to_trimesh(coupon);test.apply_translation(-test.bounds[0]);test.export(out/'PRINT_TEST_v7_section.stl')
    np.savez_compressed(out/'mesh.npz',V=tm.vertices,F=tm.faces)
    print('Bounds',tm.bounds,'volume cm3',tm.volume/1000,'triangles',len(tm.faces),flush=True)
