"""Veil v6 development prototype. Units mm. No physical fit or thermal certification.
Continuous mapped mesh surfaces replace v5 stacked slabs. Source outline retained.
Run from any folder: python veil_v6.py OUTPUT_DIRECTORY
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
P_FLARE, FLARE_SIDE, FLARE_END, LEAN_MAX = 1.35, 30.0, 9.0, 0.75
N_ROWS, KAPPA, STRUT_W = 2, 0.26, 2.6       # diamond rows, cell width / rim height, strut width
RIM_BAND, BASE_BAND = 4.0, 2.4
CENTER = np.array([8.0, 0.0])
M = 1080
# rim height above the desk at landmarks around the console (x, y, height)
LANDMARKS = [(8, 108, 27), (-40, 104, 42), (-39, 76, 66), (-34, 0, 43), (-27, -66, 54), (0, -108, 27),
             (55, -92, 43), (55, -66, 54), (52, 0, 43), (45, 76, 66), (39, 104, 42)]
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
R_BASE = R_RIM + FL
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
    man=Manifold(m3.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32)))
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
        else: rings.append([xyz(th,lo),xyz(th,hi),xyz(th,hi,True),xyz(th,lo,True)])
    return solid_rings(rings,True)

def lattice():
    # Arc-weighted u coordinate creates X/rotated square motifs. Every ribbon runs
    # continuously from base to rim; no horizontal seams or separate floating cells.
    grid=np.r_[0,np.cumsum(arc(R_BASE))]; grid=grid/grid[-1]*NCELL
    angles=np.r_[TH, np.pi]
    def angle(u): return np.interp(u%NCELL,grid,angles)
    pieces=[]
    for direction in (-1,1):
        for k in range(NCELL):
            rings=[]
            for v in np.linspace(0,1,145):
                u=k+direction*N_ROWS*v
                th=angle(u); width=STRUT_W/interp(CELLW,th)
                ta,tb=angle(u-width/2),angle(u+width/2)
                za,zb=1.2+v*(interp(RIMH,ta)-2.4),1.2+v*(interp(RIMH,tb)-2.4)
                rings.append([xyz(ta,za),xyz(tb,zb),xyz(tb,zb,True),xyz(ta,za,True)])
            pieces.append(solid_rings(rings))
    return pieces

def curved_wall(points,width=RIB_T,closed=False):
    points=np.asarray(points); d=(np.roll(points,-1,axis=0)-np.roll(points,1,axis=0)) if closed else np.gradient(points,axis=0); d/=np.linalg.norm(d,axis=1)[:,None]
    normal=np.c_[-d[:,1],d[:,0]]*width/2; rings=[]
    for p,n in zip(points,normal):
        rings.append([[*(p-n),0],[*(p+n),0],[*(p+n),H0],[*(p-n),H0]])
    return solid_rings(rings,closed)

def undercroft():
    # Oval core ribbon and four swept transverse ribs: no radial starburst.
    angle=np.linspace(0,2*np.pi,600,endpoint=False)
    longitudinal=curved_wall(np.c_[8+20*np.cos(angle),103*np.sin(angle)],closed=True)
    pieces=[]
    for y0 in (-72,-36,36,72):
        xs=np.linspace(-85,92,250); yy=y0+np.sign(y0)*9*np.sin(np.pi*(xs+85)/177)
        pieces.append(curved_wall(np.c_[xs,yy]))
    transverse=Manifold.batch_boolean(pieces,m3.OpType.Add)
    # Trim to continuously flared envelope, avoiding disconnected tips.
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
    # Circle-derived, rotated-square and triangle openings. Their roofs rise at
    # >=45 degrees in the cutter plane. Each family is cut separately so cutters
    # cannot tunnel lengthwise into the other rib family at intersections.
    tear=[(6*np.cos(a),6*np.sin(a)) for a in np.linspace(3*np.pi/4,9*np.pi/4,42)]
    tear.append((0,6*np.sqrt(2)))
    diamond=[(-6,0),(0,-6),(6,0),(0,6)]
    triangle=[(-6,-5),(6,-5),(0,7)]
    cutters=[Manifold.extrude(CS([p]),220).rotate((90,0,0)).translate((0,110,12))
             for p in (tear,diamond,triangle)]
    holes_x=[cutters[i%3].rotate((0,0,90)).translate((0,y+0.7,0)) for i,y in enumerate(range(-90,91,18))]
    holes_y=[cutters[i%3].translate((x+0.4,0,0)) for i,x in enumerate(range(-63,82,18))]
    longitudinal=longitudinal-Manifold.batch_boolean(holes_x,m3.OpType.Add)
    transverse=transverse-Manifold.batch_boolean(holes_y,m3.OpType.Add)
    return (longitudinal+transverse)^env

def to_trimesh(man):
    mesh=man.as_original().set_tolerance(0.05).simplify(0.05).to_mesh64(); V=np.asarray(mesh.vert_properties)[:,:3];F=np.asarray(mesh.tri_verts)
    remap=np.arange(len(V));remap[np.asarray(mesh.merge_from_vert,dtype=int)]=np.asarray(mesh.merge_to_vert,dtype=int)
    # STL uses float32. Validate the actual quantized topology, not only CAD's
    # higher precision topology. Remove only zero-index-area and duplicate faces.
    tm=trimesh.Trimesh(np.float32(V),remap[F],process=True)
    good=~np.any(np.diff(np.sort(tm.faces,axis=1),axis=1)==0,axis=1)
    tm.update_faces(good);tm.update_faces(tm.unique_faces());tm.remove_unreferenced_vertices()
    assert tm.is_watertight and tm.is_winding_consistent, 'Quantized export is not closed'
    return tm

def build():
    print('Building continuous X lattice',NCELL,'cells',flush=True)
    skin=Manifold.batch_boolean([band(),band(True)]+lattice(),m3.OpType.Add)
    print('Building curved undercroft',flush=True)
    body=skin+undercroft()
    # No material may enter the reference-derived cavity above seating level.
    body=body-Manifold.extrude(CAV,100).translate((0,0,H0))
    return body

if __name__=='__main__':
    out=Path(OUT);out.mkdir(parents=True,exist_ok=True)
    body=build();parts=body.decompose()
    print('Connected bodies:',len(parts), 'volumes:',[round(p.volume(),2) for p in parts],flush=True)
    assert len(parts)==1,'Disconnected geometry: do not silently discard it'
    tm=to_trimesh(body); assert tm.is_watertight and tm.is_winding_consistent
    for suffix in ('stl','3mf'): tm.export(out/f'veil_v6_prototype.{suffix}')
    gauge=to_trimesh(Manifold.extrude(CAV.offset(4)-CAV,1.6));gauge.export(out/'GAUGE_v6_cavity_1.6mm.stl')
    # Print a small real section before the full model, containing crossing struts,
    # curved base. Keep only the largest connected clipped piece; cut-off tips
    # are not part of this print test. This is not a structural test coupon.
    clip=Manifold.cube((50,32,80)).translate((45,-16,0))
    coupon=max((body^clip).decompose(),key=lambda m:m.volume())
    test=to_trimesh(coupon);test.apply_translation(-test.bounds[0]);test.export(out/'PRINT_TEST_v6_section.stl')
    np.savez_compressed(out/'mesh.npz',V=tm.vertices,F=tm.faces)
    print('Bounds',tm.bounds,'volume cm3',tm.volume/1000,'triangles',len(tm.faces),flush=True)
