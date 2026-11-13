"""v15 seat layout shared by the generator and the analysis scripts (mm, design frame: +x disc-drive side, +y rear).
Positions come from the scanned underside in references/console-scan/underside.json."""
from pathlib import Path
import numpy as np
# Four coplanar lands at seat height, all under the white covers: [-x rear, +x rear, -x front, +x front].
PADS=[(-36.5,60.6),(41.4,62.4),(-23.5,-62.5),(38.6,-62.7)]
VENT_ROW={'x':(12.,20.),'y':(-43.,87.)}
FOOTPRINT_CENTRE=(8.,0.)
def under_cover(x,y):
 """True where the scanned console shows a white cover (the part that touches a flat surface)."""
 g=np.load(Path(__file__).resolve().parents[3]/'references/console-scan/underside_grid.npz');gx,gy,c=g['x'],g['y'],g['cover']
 i=np.clip(np.round((np.asarray(y)-gy[0])/(gy[1]-gy[0])).astype(int),0,len(gy)-1);j=np.clip(np.round((np.asarray(x)-gx[0])/(gx[1]-gx[0])).astype(int),0,len(gx)-1);return c[i,j]
