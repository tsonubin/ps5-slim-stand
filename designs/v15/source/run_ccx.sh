#!/bin/zsh
# usage: run_ccx.sh <deck_dir under designs/v15>   Runs every .inp in the directory with CalculiX 2.20 (compose service "ccx").
# The SPOOLES equation solver runs on ONE thread: with several threads it returned unbalanced, wrong
# solutions on the fine mesh. Cases run side by side instead; set CCX_PARALLEL=1 on a small machine.
here=${0:A:h}; v15=${here:h}; d=$(cd $1 && pwd); rel=${d#$v15/}; compose=(docker compose -f $v15/docker/compose.yaml)
for f in $d/*.inp; do n=${f:t:r}
  ( $compose run --rm -T -w /work/$rel ccx $n > $d/$n.log 2>&1; echo $n $(grep -E "Total CalculiX Time|ERROR" $d/$n.log | head -2) ) &
  [[ -n $CCX_PARALLEL && $CCX_PARALLEL == 1 ]] && wait
done; wait
find $d -name "*.12d" -delete; find $d -name spooles.out -delete
