# v14 handoff — state on 2026-11-12

Work moved off a low-powered Mac mid-task. This file lists what is finished, what is half-done and what is still to run. Results and method are in [README.md](README.md).

## Setup on a new machine

```sh
python3.13 -m venv .venv-cad
.venv-cad/bin/pip install -r designs/v14/source/requirements-fea.txt -r designs/v14/source/requirements-solvers.txt
clang++ -O3 -std=c++17 designs/v14/airflow/lbm.cpp -o /tmp/veil-lbm      # in-house airflow screen
docker compose -f designs/v14/docker/compose.yaml build ccx              # CalculiX 2.20
docker compose -f designs/v14/docker/compose.yaml pull openfoam          # OpenFOAM v2412 (arm64 and amd64)
```

- `designs/v14/docker/Dockerfile.tools` (Python toolchain in a container) is written but **has never been built**; the native venv above is what was actually used.
- Large solver files are git-ignored and must be regenerated: `analysis/regularized.stl`, `analysis/*.npz`, `ccx/*.msh`, `ccx/surf_*.stl`, `ccx/*/*.inp|frd|npz`, `openfoam/cases/`. The README "Reproduce" block gives the commands; `source/run_checks.sh` rebuilds `analysis/`.
- The fan-made console model in `references/console-model/` is needed by most scripts.

## Finished

- Geometry: convex wall, four seat pads, 3.5 mm long-side wall, wider rib arch. Exports in `output/`.
- Wall smoothness, seat contact and geometry reviews (README sections 1–2).
- In-house stress and airflow screens on the final geometry (sections 3–4).
- PA 2200 data-sheet values, with source (section 5).
- Gmsh + CalculiX, uniform pressure, three load cases on three meshes; solver cross-check against scikit-fem (section 5).
- Rigid-plate contact on the **coarse** mesh only.
- OpenFOAM case generator and runner; a no-stand case meshes and starts solving.

## Half-done

1. **CalculiX contact on the fine mesh.** Was running (three cases side by side, about 9 min each on the coarse mesh; the fine mesh had run 12 min without finishing) and was stopped. Rerun:
   `cd designs/v14/ccx && $P ../source/build_ccx.py mesh_fine.msh fine_contact contact && ../source/run_ccx.sh fine_contact && $P ../source/post_ccx.py fine_contact render`
   Then add the fine column to the contact table in README section 5 and say whether contact results converge. Extract pad-by-pad loads from the `CSTR` contact output in the `.frd` (not parsed yet).
2. **OpenFOAM.** `openfoam/make_case.py` and `run_case.sh` are untested past iteration 86 of one no-stand case. Not yet checked: that the solve converges, that the `outletP` and `sidesPhi` function objects write usable histories, and that the stand case meshes (snappyHexMesh on the print STL, refinement level 2).

## Still to run (from the request)

**Airflow, OpenFOAM** — same table-sealed setup as README section 3:
- Flow sweep at assumed 0.25, 0.5, 1.0 and 1.5 m³/min, with and without the stand; report pressure drop in Pa for each. State clearly the flows are assumptions.
  `for q in 0.25 0.5 1.0 1.5; do $P make_case.py cases/stand_q$q stand $q 2.5; ./run_case.sh cases/stand_q$q; done` (and `empty` likewise).
- Pressure drop = 0 (inlet total pressure) minus the area-average total pressure at the outlet patch, times ρ = 1.204 kg/m³. `p` in the case is kinematic (m²/s²).
- Mesh-refinement check on one flow rate (for example base cell 2.5 mm against 1.8 mm, or stand refinement level 2 against 3).
- Compare with the lattice-Boltzmann "flow kept" result: do they agree on how restrictive the stand is and on where the air goes? Needs a post-processing script (not written): read cell centres, volumes and `U` from the last time folder, bin to a plan-view grid, and compare with `airflow/stand_1p5mm_portcore.npz`; also split inflow by side.
- An airflow figure from OpenFOAM for the README.

**Stress**
- A fillet at the rib feet where the cross ribs meet the wall near the floor, around (−51.4, −38.7, 5.5) mm and its mirror positions. The peak there does not converge (11.3, 11.2, 15.5 MPa); it is the governing stress. Refilleting changes the geometry, so every check must be rerun afterwards.
- Safety factors are reported against 48 MPa (X/Y) and 42 MPa (Z); creep and warm-air softening are noted as missing, not estimated.

**Documents**
- Print brief for v14 (`PRINT_SERVICE.md`, English and Chinese like v13's) with the chosen process and material. Decision made in the session: **final part in SLS plain nylon (PA12), white, bead-blasted, from the UnionTech service; first a fit check of the gauge and coupon in PETG on the Bambu H2D.** MJF HP Nylon only if a black part is wanted. Ask the SLS service which PA12 powder they run, because it may not be EOS PA 2200.
- PETG numbers for the fit-check print alongside PA 2200 (linear results scale with 1/E for displacement; stress is unchanged). Needs a sourced PETG data sheet.
- Top-level `README.md`: present v14 as the main version (requested, not started).
- Regenerate the review package zip if one is wanted for v14.

## Known problems and decisions

- CalculiX with a multi-threaded SPOOLES solver gave wrong answers. Keep `CCX_NPROC_EQUATION_SOLVER=1` (set in the compose file) and check the base reaction equals 31.392 N.
- Three extra-fine CalculiX cases at once ran out of memory in a 16 GB Docker VM; run them one at a time (`CCX_PARALLEL=1 ../source/run_ccx.sh xfine_pressure`).
- Neither Gmsh nor TetGen can mesh the print STL directly (self-intersecting facets reported), so all stress work uses the smoothed simulation surface.
- The generator only exports cleanly at certain rib heights: `VEIL_RIB_TOP` of 24 or 24.5 fails the watertight check, 25 and 29 work.
- Lowering the ribs to open a gap over them was tried and rejected (less flow, more stress).
- Real console vent positions, fan flow, and air temperature near the stand are unmeasured. Nothing here guarantees intake.
