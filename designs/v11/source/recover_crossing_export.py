"""Recover cached, independently checked sub-resolution weld; never rebuild patches."""
from pathlib import Path
import json,numpy as np,trimesh,manifold3d as m3
import veil_v11 as v
out=Path(__file__).resolve().parents[1]/'output';analysis=out.parent/'analysis'
cache=analysis/'crossing_repaired_full.npz'
if not cache.exists():
    from export_repair import bounded_sliver_weld
    failed=analysis/'recovery_candidate.npz'
    if not failed.exists():failed=analysis/'export_issue.npz'
    original=np.load(failed);candidate=trimesh.Trimesh(original['V'],original['F'],process=False)
    candidate,repair=bounded_sliver_weld(candidate)
    (out/'export_recovery_weld.json').write_text(json.dumps(repair,indent=2))
    np.savez_compressed(cache,V=candidate.vertices,F=candidate.faces)
a=np.load(cache);print('Load repaired cache',a['F'].shape,flush=True)
body=m3.Manifold(m3.Mesh64(np.asarray(a['V'],np.float64),np.asarray(a['F'],np.uint64)));assert body.status()==m3.Error.NoError
print('Simplify/export recovered union',flush=True);mesh=v.to_trimesh(body,.004);assert mesh.body_count==1
for suffix in ['stl','3mf']:mesh.export(out/f'veil_v11_prototype.{suffix}')
np.savez_compressed(out/'mesh.npz',V=mesh.vertices,F=mesh.faces)
print('Full body exported',mesh.extents,mesh.volume/1000,len(mesh.faces),flush=True)
clip=m3.Manifold.cube((58,36,80)).translate((22,34,0));coupon=max((body^clip).decompose(),key=lambda x:x.volume())
test=v.to_trimesh(coupon,.008);test.apply_translation(-test.bounds[0]);test.export(out/'PRINT_TEST_v11_section.stl')
print('Coupon exported',test.extents,test.volume/1000,flush=True)
# Recover measured metadata from the normal build checkpoint. An already
# completed delivery report is an explicit fallback for historical recovery.
checkpoint=out/'crossing_union_checkpoint.json'
if not checkpoint.exists():checkpoint=out/'crossing_blend.json'
if not checkpoint.exists():raise RuntimeError('Measured crossing checkpoint is missing; do not invent volume/count data')
report=json.loads(checkpoint.read_text())
report.update({'method':'Localized polynomial smooth-min additions at middle-web crossings; recovered from a bounded sliver-weld cache after export precision failure','metadata_source':checkpoint.name,'zero_blend_boundary_margin_mm':.5,'blend_taper_width_mm':1.2,'maximum_implicit_distance_offset_mm':report['smooth_min_k_mm']/4,'limitations':'Sampled distance/isosurface approximation; no exact G1 claim. See measured export-repair reports.'})
(out/'crossing_blend.json').write_text(json.dumps(report,indent=2))
import gzip,shutil
with (out/'veil_v11_prototype.stl').open('rb') as src,gzip.open(out/'veil_v11_prototype.stl.gz','wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst)
