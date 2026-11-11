import numpy as np, trimesh, sys
from PIL import Image, ImageDraw, ImageFont
from splat import render
V, F = np.load("out/V.npy"), np.load("out/F.npy"); g = trimesh.load("out/console_ghost.stl"); CV, CF = np.asarray(g.vertices), np.asarray(g.faces)
WHITE, BLUE = (0.93, 0.94, 0.96), (0.12, 0.34, 0.88); cx = 8
def shot(color, eye, tgt, ghost=False, W=900, H=640, fov=24, floor=True):
    return Image.fromarray(render([(V, F, color, 1.0)] + ([(CV, CF, (0.6, 0.66, 0.8), 0.16)] if ghost else []), eye, tgt, W, H, fov, floor=floor))
cv = Image.new("RGB", (1800, 1920), (14, 15, 19))
cv.paste(shot(WHITE, (cx + 380, -430, 250), (cx, 0, 26)), (0, 0)); cv.paste(shot(BLUE, (cx - 380, -430, 250), (cx, 0, 26)), (900, 0))
cv.paste(shot(WHITE, (cx + 700, 0, 60), (cx, 0, 32), False, 900, 380, 16), (0, 640)); cv.paste(shot(BLUE, (cx, -700, 60), (cx, 0, 32), True, 900, 380, 16), (900, 640))
cv.paste(shot(WHITE, (cx, -30, 820), (cx, 0, 0), False, 900, 900, 21, False), (0, 1020)); cv.paste(shot(BLUE, (cx + 330, 430, 230), (cx, 0, 26), True, 900, 900, 24), (900, 1020))
d = ImageDraw.Draw(cv); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
for t, xy in (("White — front, drive side", (30, 20)), ("Blue — front, plain side", (930, 20)), ("Side (front is left)", (30, 650)), ("Front, with console outline", (930, 650)),
              ("From above (front at bottom)", (30, 1030)), ("Rear, with console outline", (930, 1030))): d.text(xy, t, fill=(200, 205, 215), font=f)
cv.save("preview.png")
