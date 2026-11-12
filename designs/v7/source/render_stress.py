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
case='rim_side_10N' if 'rim_side_10N_vm' in a else 'vertical_1g';metrics=r['results'][case];limit=.8 if case=='rim_side_10N' else .08
plot=pv.Plotter(off_screen=True,window_size=(1500,1100));plot.set_background('#101827')
plot.add_mesh(grid.extract_surface(),scalars=case+'_von_Mises_MPa',cmap='turbo',clim=(0,limit),show_edges=False,scalar_bar_args={'title':'Von Mises stress / MPa','color':'white','vertical':False,'position_x':.25,'position_y':.05,'width':.5,'height':.08})
plot.add_text('VEIL / 3D SOLID-FE STRESS',position='upper_left',font_size=18,color='white')
plot.add_text(f'{case} | peak {metrics["peak_von_mises_MPa"]:.3f} MPa | max displacement {metrics["max_displacement_mm"]:.4f} mm\nUndeformed geometry. Colors above {limit:g} MPa saturate. Assumed isotropic material; constrained feet.\nScreening only: geometry approximated, no printed-material or contact validation.',position='lower_left',font_size=10,color='white')
plot.camera_position=[(360,-430,300),(8,0,25),(0,0,1)];plot.camera.parallel_projection=True;plot.camera.parallel_scale=160
plot.show(screenshot=str(root/'output'/f'{tag}_stress.png'),auto_close=True)
