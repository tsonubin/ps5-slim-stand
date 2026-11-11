"""
PS5 Slim (disc drive) "Veil" stand — v5, ONE piece, prints upright with no supports.
A smooth flared skin (diamond lattice that grows and shrinks with the rim height) wraps a hidden
triangulated rib structure; the console drops into the cavity and stands on the rib tops.
Usage: python3 ps5_veil_stand.py [outdir] [dz]
Units mm. X across (disc-drive side = +X), Y front(-) to back(+), Z up.
"""
import sys, os, math, json
import numpy as np
import manifold3d as m3
from manifold3d import CrossSection as CS, Manifold
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
DZ = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
HERE = os.path.dirname(os.path.abspath(__file__))
OL = json.load(open(os.path.join(HERE, "outline.json")))
OY = np.array(OL["y"])[::-1]; O_PLAIN = np.array(OL["plain"])[::-1]; O_DISC = np.array(OL["disc"])[::-1]
def hwL(y): return float(np.interp(y, OY, O_PLAIN))
def hwR(y): return float(np.interp(y, OY, O_DISC))

CLEAR  = 1.5            # loose fit around the console
H0     = 30.0           # lift: console base above desk
RIM_T  = 3.6            # rim thickness at the top edge
SKIN_T = 1.8
RIB_T  = 1.2
P_FLARE, FLARE_SIDE, FLARE_END, LEAN_MAX = 1.35, 30.0, 9.0, 0.75
N_ROWS, KAPPA, STRUT_W = 3, 0.19, 2.0       # diamond rows, cell width / rim height, strut width
RIM_BAND, BASE_BAND = 3.0, 1.6
CENTER = np.array([8.0, 0.0])
M = 1440
# rim height above the desk at landmarks around the console (x, y, height)
LANDMARKS = [(8, 108, 40), (-40, 104, 58), (-39, 76, 72), (-34, 0, 46), (-27, -66, 60), (0, -108, 38),
             (55, -92, 50), (55, -66, 60), (52, 0, 46), (45, 76, 72), (39, 104, 58)]
N_RAD = 32
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
RIMH = smooth(PchipInterpolator(np.r_[la - 2 * np.pi, la, la + 2 * np.pi], np.r_[lh, lh, lh])(TH), 6)
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
def strips(mask, r_in, r_o):
    """Polygons for each run of True in a circular mask, between two radial curves."""
    if not mask.any(): return []
    if mask.all():
        outer = CENTER + r_o[:, None] * U; inner = CENTER + r_in[:, None] * U
        return [outer.tolist(), inner[::-1].tolist()]
    k0 = int(np.argmin(mask)); mk = np.roll(mask, -k0); idx = (np.arange(M) + k0) % M
    d = np.diff(np.r_[0, mk.astype(int), 0]); starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    polys = []
    for a, b in zip(starts, ends):
        ii = idx[np.arange(a - 1, b + 1) % M] if b - a < M - 2 else idx[a:b]
        outer = CENTER + r_o[ii][:, None] * U[ii]; inner = CENTER + np.minimum(r_in, r_o - 0.05)[ii][:, None] * U[ii]
        polys.append(np.vstack([outer, inner[::-1]]).tolist())
    return polys

# ---------- hidden rib network ----------
def rib_edges():
    s = np.cumsum(arc(R_C)); tgt = (np.arange(N_RAD) + 0.5) * s[-1] / N_RAD; ks = np.searchsorted(s, tgt)
    ring_r = [0.5 * R_C, R_C + RIB_T / 2, R_BASE - 1.0]
    node = lambda j, i: CENTER + ring_r[j][ks[i % N_RAD]] * U[ks[i % N_RAD]]
    E = []
    def add(p, q, kind): E.append((np.array(p, float), np.array(q, float), kind))
    for i in range(0, N_RAD, 2):
        add(node(0, i), node(0, i + 2), "deck"); add(CENTER, node(0, i), "deck")      # inner ring + spokes
        add(node(0, i), node(1, i), "deck"); add(node(0, i), node(1, i + 1), "deck")  # fan out to the liner
        add(node(0, i + 2), node(1, i + 1), "deck")
    for i in range(N_RAD):
        add(node(1, i), node(1, i + 1), "deck")                                       # ring under the liner
        if i % 2 == 0: add(node(1, i), node(2, i + 1), "wedge")                       # zig-zag buttresses behind the skin
        else: add(node(1, i + 1), node(2, i), "wedge")
    return E
EDGES = rib_edges()
TAN = math.tan(math.radians(50))
def rib_layer(z):
    rects = []
    for p, q, kind in EDGES:
        L = np.linalg.norm(q - p)
        if L < 3: continue
        u = (q - p) / L; n = np.array([-u[1], u[0]]) * RIB_T / 2
        a0 = min(L / 2 - 2.2, (H0 - 6) / TAN); arch_h = TAN * a0; gaps = []
        if z < arch_h: gaps.append(a0 - z / TAN)                                  # pointed arch standing on the desk
        elif kind == "deck":
            wd = min(L / 2 - 4.0, (H0 - 6 - arch_h) / (2 * TAN)); hd = TAN * wd; zc = arch_h + 3 + hd                  # diamond window above it
            if wd > 2 and zc + hd <= H0 - 3 and abs(z - zc) < hd: gaps.append(wd * (1 - abs(z - zc) / hd))
        spans = [(0, L)] if not gaps else [(0, L / 2 - gaps[0]), (L / 2 + gaps[0], L)]
        for a, b in spans:
            if b - a > 0.2: rects.append([tuple(p + u * a - n), tuple(p + u * b - n), tuple(p + u * b + n), tuple(p + u * a + n)])
    return CS(rects, m3.FillRule.Positive)

def build(dz=DZ):
    layers = []; z = 0.0; ztop = RIMH.max()
    while z < ztop - 1e-6:
        zc = z + dz / 2; active = zc < RIMH; zeta = zc / RIMH; ro = r_out(zc)
        a, b = SIG + N_ROWS * zeta, SIG - N_ROWS * zeta
        dlt = (STRUT_W / 2) / (CELLW * 0.85)
        pat = np.minimum(np.abs(a - np.round(a)), np.abs(b - np.round(b))) < dlt
        rim = zc > RIMH - RIM_BAND
        polys = strips(active & (pat | (zc < BASE_BAND)) & ~rim, ro - SKIN_T / COSA, ro)
        polys += strips(active & rim, R_C, ro)
        if zc >= H0 - 4: polys += strips(active, R_C, R_C + RIB_T / COSA)             # smooth inner liner
        cs = CS(polys, m3.FillRule.Positive) if polys else CS()
        if zc < H0 or active.any():
            region = CS([(CENTER + np.where(active, ro - 0.4, R_C - 1.0)[:, None] * U).tolist()])
            if zc >= H0: region = region - CAV
            cs = cs + (rib_layer(zc) ^ region)
        if zc >= H0: cs = cs - CAV
        layers.append(Manifold.extrude(cs.simplify(0.02), dz + 1e-3).translate((0, 0, z))); z += dz
    return Manifold.batch_boolean(layers, m3.OpType.Add)

def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    V = np.asarray(mesh.vert_properties)[:, :3].astype(float); F = np.asarray(mesh.tri_verts).copy()
    remap = np.arange(len(V)); mf, mt = np.asarray(mesh.merge_from_vert), np.asarray(mesh.merge_to_vert)
    if len(mf): remap[mf] = mt
    tm = trimesh.Trimesh(V, remap[F], process=False); tm.remove_unreferenced_vertices(); return tm

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dRds = np.abs(np.gradient(RIMH)) / arc(R_RIM)
    lean = FL * P_FLARE / RIMH
    roof = np.degrees(np.arctan(1 / (N_ROWS * KAPPA) - dRds))
    bar = np.degrees(np.arctan(1 / np.sqrt((N_ROWS * KAPPA) ** 2 + lean ** 2)))
    print(f"rim {RIMH.min():.0f}-{RIMH.max():.0f} mm, max rim slope {dRds.max():.2f}, cells {NCELL} x {N_ROWS} rows, cell width {CELLW.min():.1f}-{CELLW.max():.1f} mm")
    print(f"skin lean max {np.degrees(np.arctan(lean.max())):.0f} deg from vertical; lattice opening roofs >= {roof.min():.0f} deg; steepest-leaning strut {bar.min():.0f} deg from horizontal")
    body = build()
    parts = body.decompose(); body = max(parts, key=lambda p: p.volume())
    print("bodies:", len(parts), "discarded volume mm3:", round(sum(p.volume() for p in parts) - body.volume(), 2))
    ghost = Manifold.extrude(PLAN, 200).translate((0, 0, H0))
    print("console interference mm3:", round((body ^ ghost).volume(), 3))
    slim = body.simplify(0.06)
    tm = to_trimesh(slim); print("faces", len(to_trimesh(body).faces), "->", len(tm.faces), "watertight", tm.is_watertight)
    tm.export(f"{OUT}/ps5_slim_disc_veil_stand.3mf"); tm.export(f"{OUT}/ps5_slim_disc_veil_stand.stl")
    np.save(f"{OUT}/V.npy", tm.vertices); np.save(f"{OUT}/F.npy", tm.faces)
    to_trimesh(ghost).export(f"{OUT}/console_ghost.stl")
    foot = CS([(CENTER + R_BASE[:, None] * U).tolist()]); np.save(f"{OUT}/footprint.npy", CENTER + R_BASE[:, None] * U)
    to_trimesh(Manifold.extrude((CAV.offset(4) - CAV), 1.6)).export(f"{OUT}/GAUGE_cavity_outline_1.6mm.stl")
    print(f"size {np.round(tm.extents,1)} mm, {tm.volume/1000:.0f} cm3 = {tm.volume/1000*1.24:.0f} g PLA")
