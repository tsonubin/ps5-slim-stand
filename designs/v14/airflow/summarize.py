"""Compare v14 with v13 in the same hypothetical capped-channel screen (see v13 AIRFLOW_REVIEW.md)."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'v13/airflow'
def reduction(folder,tag):
 e=json.loads((folder/f'empty_{tag}.json').read_text());s=json.loads((folder/f'stand_{tag}.json').read_text())
 return {'conductance_reduction_percent':100*(1-s['qout_lattice']/e['qout_lattice']),'unblocked_port_area_mm2':s['port_area_mm2'],'nominal_port_area_mm2':e['port_area_mm2'],'max_mass_imbalance_fraction':max(e['mass_imbalance_fraction'],s['mass_imbalance_fraction']),'velocity_change':max(e['relative_change'],s['relative_change'])}
cases={}
for label,tag in [('central port, 3 mm grid','3mm_port0'),('central port, 2 mm grid','2mm_port0'),('central port, 1.5 mm grid','1p5mm_port0'),('port offset to y=60, 3 mm grid','3mm_port60')]:
 a=reduction(OLD,tag);b=reduction(R,tag);cases[label]={'v13':a,'v14':b,'v14_minus_v13_percentage_points':b['conductance_reduction_percent']-a['conductance_reduction_percent']}
out={'scope':'Hypothetical capped undercroft channel with an ASSUMED 30 mm suction port; relative v13/v14 comparison only. Not PS5 cooling CFD; real vent map and fan operating point unknown.','CAD_sha256':hashlib.sha256((R.parent/'output/veil_v14_prototype.stl').read_bytes()).hexdigest(),'cases':cases}
(R/'summary.json').write_text(json.dumps(out,indent=2))
for k,c in cases.items():print(f"{k}: v13 {c['v13']['conductance_reduction_percent']:.2f}%  v14 {c['v14']['conductance_reduction_percent']:.2f}%  (port open area v13 {c['v13']['unblocked_port_area_mm2']:.0f} / v14 {c['v14']['unblocked_port_area_mm2']:.0f} mm2)")
