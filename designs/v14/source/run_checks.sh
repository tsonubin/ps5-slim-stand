#!/bin/zsh
# Rebuild-independent rerun of the in-house stress (scikit-fem) and airflow (lattice-Boltzmann) screens for v14.
# Usage: designs/v14/source/run_checks.sh   (from the repository root; needs VEIL_LBM pointing at the compiled lbm.cpp)
cd "$(dirname "$0")/../../.."
P=$PWD/.venv-cad/bin/python A=designs/v14/analysis S=designs/v14/source
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 FEA_COARSE_SOLVER=splu
$P $S/voxel_surface.py designs/v14/output/veil_v14_prototype.stl .45 $A/regularized.stl > $A/regularized.log 2>&1 || exit 1
(FEA_NO_OPT=2 $P $S/mesh_fea.py $A/regularized.stl 2 $A/v14_coarse_mesh.npz > $A/coarse_mesh.log 2>&1 && $P $S/solve_fea.py $A/v14_coarse_mesh.npz $A/v14_coarse_result > $A/coarse_solve.log 2>&1) &
(FEA_NO_OPT=3 $P $S/mesh_fea.py $A/regularized.stl .4 $A/v14_fine_mesh.npz > $A/fine_mesh.log 2>&1 && $P $S/solve_fea.py $A/v14_fine_mesh.npz $A/v14_fine_result > $A/fine_solve.log 2>&1) &
($P $S/mesh_fea.py $A/regularized.stl .4 $A/v14_quality_mesh.npz > $A/quality_mesh.log 2>&1 && FEA_CASE=vertical_1g $P $S/solve_fea.py $A/v14_quality_mesh.npz $A/v14_quality_result > $A/quality_solve.log 2>&1) &
(cd designs/v14/airflow && for a in "3" "2" "1.5" "3 60" "3 core" "2 core" "1.5 core"; do $P run_screen.py ${=a} > /dev/null 2>&1; done; $P summarize.py > summarize.log 2>&1; $P render_sealed.py 1p5mm) &
wait
$P $S/review_fea.py > $A/fea_review.log 2>&1
for t in coarse fine quality; do $P $S/render_stress.py v14_${t}_result > /dev/null 2>&1; done
$P $S/review_seat.py > $A/seat_review.log 2>&1; $P $S/review_geometry.py > $A/geometry_review.log 2>&1; $P $S/review_wall.py > $A/wall_review.log 2>&1
$P $S/render_clean.py > /dev/null 2>&1; $P $S/render_turntable.py > /dev/null 2>&1
grep -l Traceback $A/*.log designs/v14/airflow/*.log; echo checks-done
