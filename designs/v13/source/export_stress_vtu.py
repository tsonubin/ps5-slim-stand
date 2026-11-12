from pathlib import Path
import sys,json
import numpy as np,pyvista as pv
root=Path(__file__).resolve().parents[1];tag=sys.argv[1] if len(sys.argv)>1 else 'full_star_result'
a=np.load(root/'analysis'/f'{tag}.npz');r=json.loads((root/'analysis'/f'{tag}.json').read_text())
nodes=a['nodes'];elements=a['elements'];cells=np.c_[np.full(len(elements),4),elements]
grid=pv.UnstructuredGrid(cells,np.full(len(elements),pv.CellType.TETRA,dtype=np.uint8),nodes)
for case in ['vertical_1g','eccentric_1g','rim_side_10N']:
 if case+'_vm' not in a:continue
 grid.cell_data[case+'_von_Mises_MPa']=a[case+'_vm'];grid.point_data[case+'_displacement_mm']=a[case+'_u']
grid.save(root/'output'/f'{tag}.vtu')
print('Saved VTU',tag,flush=True)
