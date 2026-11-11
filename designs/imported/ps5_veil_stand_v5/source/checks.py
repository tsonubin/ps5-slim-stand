"""Stability and strength checks for the v5 one-piece stand (rigid-body tipping + hand-calculated wall bending)."""
import numpy as np, math
from scipy.spatial import ConvexHull
import ps5_veil_stand as B
G, M, CON_H, STAND = 9.81, 3.2, 358.0, 0.20
W = M * G; fp = np.load("out/footprint.npy"); hull = fp[ConvexHull(fp).vertices]
cg = np.array([(B.hwR(0) - B.hwL(0)) / 4, 0.0]); cgz = (M * (B.H0 + CON_H / 2) + STAND * 22) / (M + STAND)
def lever(direction):
    best = 1e9
    for a, b in zip(hull, np.roll(hull, -1, 0)):
        e = b - a; n = np.array([e[1], -e[0]]); n /= np.linalg.norm(n)
        if n @ direction > 0.7: best = min(best, (a - cg) @ n)
    return best
def tip(l, h, m): return math.degrees(math.atan2(l, h)), m * G * (math.hypot(l, h) - h)
print("== TIPPING ==")
for name, d, bare, sony in (("left (plain side)", (-1, 0), 27.6 + cg[0], 74.3 + cg[0]), ("right (drive side)", (1, 0), 27.6 - cg[0], 74.3 - cg[0]), ("forward", (0, -1), 67, 74.3), ("backward", (0, 1), 67, 74.3)):
    l = lever(np.array(d, float)); a, e = tip(l, cgz, M + STAND); ab, eb = tip(bare, CON_H / 2, M); asn, es = tip(sony, CON_H / 2 + 3, M)
    print(f" {name:<19} lever {l:5.1f} mm | this stand {a:4.1f} deg, {(W + STAND * G) * l / (CON_H + B.H0):4.1f} N, {e:4.0f} mJ | no stand {ab:4.1f} deg, {W * bare / CON_H:4.1f} N | Sony ring {asn:4.1f} deg, {W * sony / CON_H:4.1f} N")
print("\n== WALL STRENGTH (hand calculation, not FEA) ==")
for side, d in (("left", (-1, 0)), ("right", (1, 0))):
    l = lever(np.array(d, float)); F = (W + STAND * G) * l / (CON_H + B.H0); lb = 27.6 + (cg[0] if d[0] < 0 else -cg[0])
    for label, h, R in (("rear peak", 72 - B.H0, 72.0), ("mid rim", 46 - B.H0, 46.0)):
        P = (F * CON_H - W * lb) / h; Mb = P * h; width = 60.0
        zeta = B.H0 / R; depth = B.RIM_T + 28 * (1 - zeta) ** B.P_FLARE
        A_liner, A_skin = B.RIB_T * width, B.SKIN_T * width * 0.38
        s = Mb / (min(A_liner, A_skin) * depth)
        print(f" knock toward {side:<5}, console leaning on {label:<9}: {P:4.0f} N on rim -> {s:4.1f} MPa in the wall (across layers, allow 20) -> safety factor {20 / s:4.1f}")
