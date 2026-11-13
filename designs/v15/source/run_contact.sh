#!/bin/zsh
# usage: designs/v15/source/run_contact.sh   Rebuild and rerun only the rigid-plate contact cases (coarse and fine).
here=${0:A:h}; v=${here:h}; P=$v/../../.venv-cad/bin/python; cd $v/ccx || exit 1
for m in coarse fine; do rm -rf ${m}_contact; $P $here/build_ccx.py mesh_$m.msh ${m}_contact contact > ${m}_contact.build.log 2>&1; done
$here/run_ccx.sh coarse_contact; $here/run_ccx.sh fine_contact
for m in coarse fine; do $P $here/post_ccx.py ${m}_contact render > ${m}_contact.post.log 2>&1; done; echo contact-done
