"""Fast point-splat renderer (numpy) for dense meshes."""
import numpy as np
def look_at(eye, target, up=(0, 0, 1)):
    f = np.array(target, float) - eye; f /= np.linalg.norm(f); r = np.cross(f, up); r /= np.linalg.norm(r); return np.array([r, np.cross(r, f), -f])
def sample(V, F, spacing, rng):
    tri = V[F]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); area = np.linalg.norm(n, axis=1) / 2
    n = n / (2 * area[:, None] + 1e-12); cnt = np.maximum(1, np.ceil(area / spacing ** 2).astype(int)); idx = np.repeat(np.arange(len(F)), cnt)
    a, b = rng.random(len(idx)), rng.random(len(idx)); fl = a + b > 1; a[fl], b[fl] = 1 - a[fl], 1 - b[fl]
    P = tri[idx, 0] + a[:, None] * (tri[idx, 1] - tri[idx, 0]) + b[:, None] * (tri[idx, 2] - tri[idx, 0])
    return P, n[idx]
def render(items, eye, target, W=900, H=640, fov=24, bg=(14, 15, 19), ss=2, floor=True, spacing=0.22):
    """items: list of (V, F, rgb, alpha). Opaque first, then translucent overlays."""
    rng = np.random.default_rng(0); w, h = W * ss, H * ss; eye = np.array(eye, float); R = look_at(eye, target); foc = 0.5 * h / np.tan(np.radians(fov) / 2)
    col = np.zeros((h, w, 3)); col[:] = np.array(bg) / 255; zb = np.full((h, w), np.inf)
    L1 = np.array([0.35, -0.5, 0.8]); L1 /= np.linalg.norm(L1); L2 = np.array([-0.6, 0.3, 0.4]); L2 /= np.linalg.norm(L2)
    def proj(P):
        Q = (P - eye) @ R.T; z = -Q[:, 2]; return (w / 2 + foc * Q[:, 0] / z).astype(int), (h / 2 - foc * Q[:, 1] / z).astype(int), z
    if False:
        g = np.stack(np.meshgrid(np.arange(-420, 420, 0.5), np.arange(-420, 420, 0.5)), -1).reshape(-1, 2); P = np.c_[g, np.zeros(len(g))]
        x, y, z = proj(P); ok = (x >= 0) & (x < w) & (y >= 0) & (y < h) & (z > 1); col[y[ok], x[ok]] = np.array(bg) / 255 * 1.9
    for V, F, rgb, alpha in items:
        dist = np.linalg.norm(V.mean(0) - eye); sp = max(0.55 * dist / foc, 0.09)
        tri = V[F]; area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
        cnt = np.maximum(1, np.ceil(area / sp ** 2)); cuts = np.searchsorted(np.cumsum(cnt), np.arange(1.5e6, cnt.sum(), 1.5e6)); mask = np.zeros((h, w), bool)
        for Fc in np.split(F, cuts):
            if not len(Fc): continue
            P, N = sample(V, Fc, sp, rng)
            view = eye - P; view /= np.linalg.norm(view, axis=1, keepdims=True)
            N = np.where(((N * view).sum(1) < 0)[:, None], -N, N)
            sh = 0.26 + 0.72 * np.clip(N @ L1, 0, 1) + 0.22 * np.clip(N @ L2, 0, 1)
            Hh = L1 + view; Hh /= np.linalg.norm(Hh, axis=1, keepdims=True); sh = sh + 0.2 * np.clip((N * Hh).sum(1), 0, 1) ** 30
            x, y, z = proj(P); ok = (x >= 0) & (x < w) & (y >= 0) & (y < h) & (z > 1); x, y, z, sh = x[ok], y[ok], z[ok], sh[ok]
            if alpha >= 1:
                order = np.argsort(-z); x, y, z, sh = x[order], y[order], z[order], sh[order]
                vis = z < zb[y, x]; x, y, z, sh = x[vis], y[vis], z[vis], sh[vis]
                col[y, x] = np.clip(np.array(rgb)[None, :] * sh[:, None], 0, 1); zb[y, x] = z
            else:
                vis = z < zb[y, x]; mask[y[vis], x[vis]] = True
        if alpha < 1: col[mask] = col[mask] * (1 - alpha) + np.array(rgb) * 0.8 * alpha
    return (np.clip(col.reshape(H, ss, W, ss, 3).mean((1, 3)), 0, 1) * 255).astype(np.uint8)
