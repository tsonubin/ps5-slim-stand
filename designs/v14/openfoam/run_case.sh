#!/bin/zsh
# usage: run_case.sh <case_dir under designs/v14/openfoam> [mesh|solve|both] [processes=8]
# Runs blockMesh + snappyHexMesh and/or simpleFoam in the compose service "openfoam" (OpenFOAM v2412).
here=${0:A:h}; v14=${here:h}; c=$(cd $1 && pwd); rel=${c#$v14/}; what=${2:-both}; np=${3:-8}
sed -i '' "s/numberOfSubdomains [0-9]*;/numberOfSubdomains $np;/" $c/system/decomposeParDict
docker compose -f $v14/docker/compose.yaml run --rm -T -w /work/$rel openfoam -lc "
source /usr/lib/openfoam/openfoam2412/etc/bashrc
set -e
if [ $what != solve ]; then
  blockMesh > log.blockMesh 2>&1
  decomposePar -force > log.decomposePar0 2>&1
  mpirun -np $np --oversubscribe snappyHexMesh -overwrite -parallel > log.snappyHexMesh 2>&1
  reconstructParMesh -constant > log.reconstructParMesh 2>&1
  rm -rf processor*
  checkMesh -constant > log.checkMesh 2>&1 || true
fi
if [ $what != mesh ]; then
  decomposePar -force > log.decomposePar 2>&1
  mpirun -np $np --oversubscribe simpleFoam -parallel > log.simpleFoam 2>&1
  reconstructPar -latestTime > log.reconstructPar 2>&1
  postProcess -func writeCellCentres -latestTime > log.cellCentres 2>&1
  postProcess -func writeCellVolumes -latestTime > log.cellVolumes 2>&1
  rm -rf processor*
fi
"
