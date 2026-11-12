from pathlib import Path
import json,hashlib
import numpy as np,trimesh,manifold3d as m3
from scipy.ndimage import label
R=Path(__file__).resolve().parent;cad=R.parent/'output/veil_v13_prototype.stl';m=trimesh.load(cad);b=m3.Manifold(m3.Mesh(np.float32(m.vertices),np.uint32(m.faces)));v=(b^m3.Manifold.cube([400,400,30]).translate([-200,-200,0])).volume()
cases=[]
for h in ['3','2','1p5']:
 e=json.loads((R/f'empty_{h}mm_port0.json').read_text());s=json.loads((R/f'stand_{h}mm_port0.json').read_text());d=np.load(R/f'stand_{h}mm_port0.npz');t=d['t'];pitch=s['pitch_mm'];l,n=label(t>0);sizes=np.bincount(l.ravel());sizes[0]=0
 vv=(e['fluid_nodes']-s['fluid_nodes'])*pitch**3
 cases.append(dict(pitch_mm=pitch,conductance_reduction_percent=100*(1-s['qout_lattice']/e['qout_lattice']),stand_conductance_scaled=s['conductance_scaled'],empty_conductance_scaled=e['conductance_scaled'],voxel_stand_volume_under30_mm3=vv,CAD_volume_under30_mm3=v,voxel_volume_error_percent=100*(vv/v-1),fluid_components=n,largest_fluid_fraction=float(sizes.max()/np.count_nonzero(t)),max_mass_imbalance_fraction=max(e['mass_imbalance_fraction'],s['mass_imbalance_fraction']),velocity_change=max(e['relative_change'],s['relative_change']),port_area_mm2=s['port_area_mm2']))
e=json.loads((R/'empty_3mm_port60.json').read_text());s=json.loads((R/'stand_3mm_port60.json').read_text());reverse=json.loads((R/'stand_3mm_port0_reverse.json').read_text());forward=json.loads((R/'stand_3mm_port0.json').read_text());benchmark=json.loads((R/'duct_benchmark.json').read_text())
summary={'CAD_sha256':hashlib.sha256(cad.read_bytes()).hexdigest(),'scope':'Hypothetical capped undercroft channel, not actual PS5 cooling CFD','central_port_grid_sensitivity':cases,'offset_port_60mm':{'grid_mm':3,'nominal_sampled_area_mm2':e['port_area_mm2'],'unblocked_area_mm2':s['port_area_mm2'],'conductance_reduction_percent':100*(1-s['qout_lattice']/e['qout_lattice']),'mass_imbalance_fraction':s['mass_imbalance_fraction']},'pressure_reversal_flux_magnitude_change_percent':100*(abs(reverse['qout_lattice']/forward['qout_lattice'])-1),'duct_benchmark_relative_error':benchmark['relative_flux_error'],'spatial_convergence_established':False,'actual_console_port_map_verified':False,'actual_fan_operating_point_or_temperature_predicted':False}
(R/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
