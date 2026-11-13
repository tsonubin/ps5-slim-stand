#!/bin/zsh
# usage: designs/v15/source/run_stress.sh   Full CalculiX study of the current STL: simulation surface, three meshes,
# pressure cases on all three and rigid-plate contact on coarse and fine, then results.json and heatmaps.
here=${0:A:h}; v=${here:h}; P=$v/../../.venv-cad/bin/python; cd $v/ccx || exit 1
$P $here/voxel_surface.py $v/output/veil_v15_prototype.stl .45 $v/analysis/regularized.stl > $v/analysis/regularized.log 2>&1 || exit 1
for row in "coarse 3.0 0.6" "fine 2.2 0.35" "xfine 2.2 0.2"; do set -- ${=row}
  ( $P $here/remesh_surface.py $v/analysis/regularized.stl $2 surf_$1.stl $3 > surf_$1.log 2>&1 && $P $here/mesh_gmsh.py surf_$1.stl $2 mesh_$1.msh direct > mesh_$1.log 2>&1 \
    && $P $here/build_ccx.py mesh_$1.msh ${1}_pressure pressure > ${1}_pressure.build.log 2>&1 \
    && { [[ $1 == xfine ]] || $P $here/build_ccx.py mesh_$1.msh ${1}_contact contact > ${1}_contact.build.log 2>&1 } ) &
done; wait
for d in coarse_pressure coarse_contact fine_pressure; do $here/run_ccx.sh $d; done
CCX_PARALLEL=1 $here/run_ccx.sh xfine_pressure; $here/run_ccx.sh fine_contact
for d in coarse_pressure coarse_contact fine_pressure fine_contact xfine_pressure; do $P $here/post_ccx.py $d render > $d.post.log 2>&1; done
echo stress-done
