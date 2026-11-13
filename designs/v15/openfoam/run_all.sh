#!/bin/zsh
# usage: designs/v15/openfoam/run_all.sh [processes per case=8] [cases side by side=2]
# Builds, meshes, solves and summarises every case of the vent-slot study, then runs compare.py.
here=${0:A:h}; P=$here/../../../.venv-cad/bin/python; np=${1:-8}; par=${2:-2}; cd $here; mkdir -p cases
one() { # name kind flow cell [step]
  [[ -f cases/$1/summary.json ]] && return
  $P make_case.py cases/$1 $2 $3 $4 2 1000 ${5:-2.5} > /dev/null && ./run_case.sh cases/$1 both $np && $P post_case.py cases/$1
}
list=(); for q in 0.03 0.06 0.12; do for k in desk hover stand; do list+=("${k}_q$q $k $q 2.5"); done; done
for k in desk stand; do for s in 2.0 3.5; do list+=("${k}_q0.06_s$s $k 0.06 2.5 $s"); done; done
for k in desk hover stand; do list+=("${k}_q0.06_h1.8 $k 0.06 1.8"); done
i=0; for row in $list; do one ${=row} & (( ++i % par == 0 )) && wait; done; wait
$P compare.py > compare.log 2>&1; tail -1 compare.log
