# Veil v14 — convex wall, seat pads, open-arch ribs, stiffened long sides

**Work in progress: see [HANDOFF.md](HANDOFF.md) for what is finished and what is still to run.**

v14 keeps v13's perforated shell and opening pattern, and changes these things: the exterior wall is rebuilt as a strictly convex surface, the console now rests on four flat pads instead of narrow rib crests, the ribs are rerouted under those pads with filleted crossings, the wall is thickened inward by up to 0.7 mm where it stands clear of the console, and each rib's underside is a wider, flatter arch to let more air through. **This is a design and screening prototype, not a qualified stand.** v13 is untouched.

![v14 assembly](output/assembly_base_detail.png)

[Standalone shell](output/hero_v14.png) · [Four views](output/preview_v14_clean.png) · [12-angle turntable](output/turntable_v14.png) · [v13 turntable for comparison](output/turntable_v13.png) · [Flat-shaded side profile](output/side_profile_flat.png)

Overall size is **152.83 × 247.08 × 40.70 mm** (v13: 150.34 × 241.28 × 40.70), volume **78.54 cm³** (v13: 74.61). Seat height 30 mm, 1.5 mm nominal cavity clearance, 72 openings and the rim height guide are inherited; the shell is 2.8 mm at the tight ends and 3.5 mm along the long sides (v13: 2.8 mm throughout). The fit gauge has the same extents as v13's.

| Deliverable | Purpose |
|---|---|
| [3MF](output/veil_v14_prototype.3mf) / [STL](output/veil_v14_prototype.stl) | Prototype geometry, millimetres; no printer settings |
| [Source](source/veil_v14.py) | Editable generator |
| [Fit gauge](output/GAUGE_v14_cavity_1.6mm.stl) / [print coupon](output/PRINT_TEST_v14_section.stl) | Cavity outline check; shell/support crop |

## 1. Exterior wall

v13's rim and base guides were smoothed radial functions; the smoothing left ripples that were not in the console outline (the console's clearance outline is within 1.46 mm of its own convex hull). v14 fits each guide as a Fourier series of the curve's **support function**, where "convex" and "clears the console" are both linear constraints.

| Measure (analytic guide surface) | v13 | v14 |
|---|---:|---:|
| Direction changes in rim outline | 50 | 0 |
| Inward-curving rim length | 242 mm | 0 mm |
| Direction changes at mid-wall / base | 38 / 4 | 0 / 0 |
| Significant curvature peaks and dips around rim | 42 | 8 |
| Tightest rim radius | 6.6 mm | 10.7 mm |
| Silhouette kinks summed over 12 view angles | 67 | 0 |
| Steepest wall lean from vertical | 54.7° | 43.6° |
| Rim-to-cavity gap | 3.95–10.84 mm | 4.08–17.17 mm |

Cost: the rim sits up to 17 mm from the cavity outline at mid-sides (v13: 11 mm), and the footprint grows 2.5 mm × 5.8 mm. These numbers describe the analytic guide surface, not the opening edges or the triangulated mesh. Evidence: [wall_smoothness.json](analysis/wall_smoothness.json), from `source/review_wall.py`.

## 2. Seat contact

Measured against the flat bottom of the fan-made reference core (not a scan of real hardware), assuming 3.2 kg:

| | v13 | v14 |
|---|---:|---:|
| What touches the core | 3 rib crests, each 1.54 mm wide (4th rib misses the core) | 4 pads, each 21.6 × 10.6 mm flat land |
| Nominal contact area | 349 mm² | 771 mm² |
| Mean pressure | 0.090 MPa | 0.041 MPa |
| Closest contact to core edge | 0 mm | 6.6 mm |
| Stand material in the core-to-cover slot | 418 mm³ | 0.5 mm³ |

- Wall thickness follows the radial rim-to-cavity gap: 2.8 mm where the gap is under 5 mm, rising smoothly to 3.5 mm where it exceeds 10 mm (about 80% of the perimeter is above 3.3 mm). It grows inward only.
- Pads are 24 × 13 mm rounded outlines centred at (±16.5, 44) and (±11.5, −44) mm, with a 1.5 mm rolled edge and a 45° self-supporting underside.
- Pad tops are **flat**, not crowned: a crown on a rigid pad would recreate a small contact spot.
- Rib crests are at 29 mm, 1 mm below the seat, so nothing but the pads touches the console. Each rib is a single arch 7 mm deep at mid-span; its underside follows 22·sin(πs) mm along the rib (v13 and earlier v14 builds used sin², which left much less open area near the ends).
- The reference core's centroid lies inside the pad quadrilateral with 15.4 mm margin (v13's contact hull gave 23.0 mm); the pad pair at −y is narrower because the core bottom narrows there.
- Rib crossings carry a plan fillet growing to 3 mm radius, replacing v13's sharp vertical inside corners. Stress results for this geometry are in section 4.

Neither pressure is high enough to damage the console housing; the change is about defined, edge-free, symmetric support. Evidence: [seat_contact.json](analysis/seat_contact.json), from `source/review_seat.py`.

## 3. Airflow (in-house lattice-Boltzmann screen)

**The real CFI-20xx vent positions and fan operating point are still unmeasured, so nothing here shows that the console's intake works.** Both screens are relative comparisons at equal suction ([method and limits](../v13/airflow/AIRFLOW_REVIEW.md)): solid table at z = 0, solid cap at seat height, open sides, creeping-flow lattice-Boltzmann.

### Assumed 30 mm port

| Case | v13 flow reduction | v14 flow reduction |
|---|---:|---:|
| Central port, 3 mm grid | 20.86% | 27.76% |
| Central port, 2 mm grid | 22.95% | 20.89% |
| Central port, 1.5 mm grid | 25.41% | 23.45% |
| Port moved to y = 60 mm, 3 mm grid | 53.73% | 31.24% |

v14 is about 2 points less restrictive than v13 on the two finer grids and 22 points less with the port off-centre. The 3 mm grid is worse because the grid closes 36 mm² of the assumed port (684 of 720 mm² open). Results are not grid-converged.

### Table-sealed, wall-intake case

Air can only arrive sideways through the wall openings, and suction is spread over the **whole flat underside of the reference core** (about 70 cm²). "Flow kept" is flow with the stand divided by flow with no stand at the same suction.

| Grid | v13 flow kept | v14 flow kept |
|---|---:|---:|
| 3 mm | 27.8% | 26.0% |
| 2 mm | 24.9% | 24.6% |
| 1.5 mm | 23.5% | 23.5% |

![Table-sealed flow map](output/airflow_sealed_1p5mm.png)

- The stand removes roughly three quarters of the easy flow in both versions; v14 now matches v13 on the finest grid. The no-stand reference is a console hovering 30 mm above the table with nothing around it, which is a very open baseline.
- The wall alone keeps 38.3% (2 mm grid), so the wall and the seat structure matter about equally.
- Rib shape was explored on the 2 mm grid. Dropping the ribs 4 mm below the console made flow worse (22.4% kept) and tripled peak stress, because the main air path is under the ribs, not over them. The wider arch adopted here raised flow kept from 22.8% to 24.6%. A still thinner, wider arch reached 26.1% but tripled the deflection under weight, so it was not adopted.
- Wall openings total about 112 cm², of which about 92 cm² are below seat height (v13: 116 and 97); that exceeds the underside area being fed.
- Rough scale only, from the pre-arch build: at an *assumed* 1 m³/min the solved creeping-flow resistance gives about 0.2 Pa and an orifice-type estimate through the below-seat openings about 5 Pa. Neither is a prediction for the real console. The OpenFOAM sweep in section 6 is meant to replace this estimate and has not been run yet.

Results: `airflow/summary.json`, `airflow/*_portcore.json`; map from `airflow/render_sealed.py`.

## 4. Stress screen (in-house, first-order elements)

Same method as [v13's structural analysis](../v13/STRUCTURAL_ANALYSIS.md): scikit-fem, first-order tetrahedra on a smoothed simulation-only surface, E = 1,200 MPa and Poisson ratio 0.35 (illustrative), clamped base, 31.392 N as uniform pressure on the pad tops (750 mm²; v13: 265 mm² of rib crest). **Kept for comparison with v13. Section 5 shows these first-order results understate deflection by about half.**

| Case, finer mesh | | v13 | v14 |
|---|---|---:|---:|
| Console weight | Max displacement | 0.157 mm | 0.137 mm |
| | Stress below which 95% of the material sits | 0.42 MPa | 0.44 MPa |
| | Raw peak | 51.3 MPa | 29.0 MPa |
| Weight plus 10 N sideways on the +x rim | Max displacement | 0.223 mm | 0.206 mm |
| | 95% stress | 0.50 MPa | 0.51 MPa |
| | Raw peak | 51.6 MPa | 29.6 MPa |
| | Material above 2 MPa | 14.7 mm³ | 22.1 mm³ |

- Design history under this screen: with a 2.8 mm wall v14 was 36% more flexible than v13 under the side push (0.304 mm). Thickening the wall inward to 3.5 mm along the long sides brought that to 0.201 mm. The wider rib arch then traded some weight stiffness for airflow (0.078 mm to 0.137 mm under weight), leaving both cases a little stiffer than v13.
- Raw peaks are not mesh-converged here (60.9 MPa coarse, 29.0 MPa finer, in badly shaped elements). The optimized-quality TetGen mesh could not be built for the final geometry ("input surface mesh contain self-intersections"), so there is no third mesh.
- The uneven-weight case is not comparable with v13: it loads faces at x > 8 mm, which is one small rib patch in v13 and two whole pads in v14 (0.189 mm, 18.0 MPa raw peak).

Meshes: 547,825 and 665,991 tetrahedra. Simulation surface versus CAD: −1.29% volume, 0.19 mm at the 95th percentile, 0.52 mm maximum sampled deviation. Heatmaps: [weight](output/v14_fine_result_vertical_1g_stress.png) · [uneven weight](output/v14_fine_result_eccentric_1g_stress.png) · [side push](output/v14_fine_result_rim_side_10N_stress.png). Data: [fea_review.json](analysis/fea_review.json), `analysis/v14_*_result.json`.

## 5. Stress with Gmsh + CalculiX and PA 2200 properties

### Reference material

EOS PA 2200 (laser-sintered PA12, white), from the [EOS material data sheet](https://www.eos.info/polymer-solutions/polymer-materials/data-sheets/mds-pa-2200) ("PA 2200 Balance", 120 µm layers, status 12.11.2026). The sheet does not name a machine, so **P 396 is not confirmed by the source**. All values are dry, short-term, room-temperature.

| Property | X / Y | Z (build direction) | Standard |
|---|---:|---:|---|
| Tensile modulus | 1,650 MPa | 1,650 MPa | ISO 527 |
| Tensile strength | 48 MPa | 42 MPa | ISO 527 |
| Strain at break | 18% | 4% | ISO 527 |
| Heat deflection, 1.80 MPa | 64 °C | 57 °C | ISO 75 |
| Heat deflection, 0.45 MPa | 157 °C | 145 °C | ISO 75 |
| Density | 0.93 g/cm³ | | EOS method |

Poisson's ratio is **not on the data sheet**. The model uses 0.40, from [Faes et al. 2015](https://utw10945.utweb.utexas.edu/sites/default/files/2015/2015-69-Faes.pdf), who measured 0.3967 (uniaxial) and 0.41 (full-field) on PA 2200 from an EOS P395. At 78.54 cm³ the part weighs about 73 g.

### Model

- **Mesh:** Gmsh could not mesh the print STL directly ("two exactly self-intersecting facets"), and its surface reparametrisation failed on both the print STL and the simulation surface ("wrong topology of boundary mesh"). The mesh therefore starts from the existing simulation surface (`analysis/regularized.stl`), is remeshed isotropically with MMG 5.8 (target edge 0.45× around the pads and rib crossings, 0.55× on the +x wall struts), and is then filled by Gmsh 4.15 (HXT) and raised to **second-order tetrahedra** (C3D10). Mid-side nodes sit on straight edges.
- **Solver:** CalculiX 2.20, linear elastic, clamped base (nodes within 0.2 mm of the lowest point). The multi-threaded SPOOLES solver returned wrong, unbalanced answers on the fine mesh (25 N reaction for a 31 N load), so every run uses one solver thread and is checked for force balance.
- **Loads:** the same three cases. In the pressure model the weight is a uniform pressure on the pad tops. In the contact model the console is a rigid flat plate resting on the pads through frictionless contact, with the weight applied at the core centroid (and 10 mm towards +x for the uneven case), so pad loads follow from equilibrium.

| Mesh | Surface tolerance | Tetrahedra | Nodes | Volume vs simulation surface | Worst element quality (gamma) |
|---|---:|---:|---:|---:|---:|
| Coarse | 0.60 mm | 103,741 | 215,525 | −3.69% | 0.120 |
| Fine | 0.35 mm | 214,875 | 433,027 | −0.65% | 0.092 |
| Extra-fine | 0.20 mm | 300,727 | 617,790 | +0.55% | 0.082 |

No element is below 0.05 on any mesh. The coarse surface is visibly thinner than the geometry, so treat it as a lower-fidelity check only.

### Results, uniform pressure

| Case | | Coarse | Fine | Extra-fine |
|---|---|---:|---:|---:|
| Console weight | Max displacement | 0.199 mm | 0.183 mm | 0.180 mm |
| | 95% stress | 0.59 MPa | 0.56 MPa | 0.55 MPa |
| | 99.9% stress | 1.74 MPa | 1.67 MPa | 1.65 MPa |
| | Peak, pads and rib crossings | 5.0 MPa | 4.9 MPa | 5.3 MPa |
| | Peak anywhere above the base | 11.3 MPa | 11.2 MPa | 15.5 MPa |
| Uneven weight | Max displacement | 0.272 mm | 0.252 mm | 0.246 mm |
| | Peak anywhere above the base | 12.0 MPa | 12.1 MPa | 16.4 MPa |
| Weight + 10 N side push | Max displacement | 0.253 mm | 0.236 mm | 0.231 mm |
| | Peak, +x wall struts | 5.9 MPa | 6.7 MPa | 7.1 MPa |
| | Peak anywhere above the base | 11.3 MPa | 11.2 MPa | 15.5 MPa |

![CalculiX side push](output/ccx_fine_pressure_rim_side_10N_stress.png)

- **Displacement and bulk stress converge** (within 2% between the two finer meshes).
- **The single highest peak does not converge.** It sits at the same place on all meshes, about (−51.4, −38.7, 5.5) mm, where a cross rib's foot meets the wall near the floor, and it rises as the surface tolerance tightens (11.3, 11.2, 15.5 MPa). That is the signature of a sharp inside corner. The rib feet need a fillet before a converged peak exists there.
- **Safety factor against the data-sheet tensile strength, using the highest value found (16.4 MPa, uneven weight, extra-fine):** 2.9 in X/Y and 2.6 against the Z strength. Because that peak is still rising, these are upper bounds on the margin at that corner, not a converged result. Away from it, 99.9% of the material is below 2.3 MPa (factor above 18 on the Z strength).
- The wall-strut peak under the side push is also still creeping up (5.9, 6.7, 7.1 MPa).

### Results, rigid-plate contact (coarse mesh only)

| Case | Max displacement | Peak above the base | 99.9% stress | Iterations |
|---|---:|---:|---:|---:|
| Console weight | 0.132 mm | 8.0 MPa | 1.41 MPa | 22 |
| Uneven weight (load point +10 mm in x) | 0.156 mm | 8.5 MPa | 1.67 MPa | 21 |
| Weight + 10 N side push | 0.242 mm | 7.8 MPa | 1.90 MPa | 23 |

Contact converged with exact force balance (31.392 N). The plate keeps the four pads level, so the stand deflects a third less than under uniform pressure (0.132 mm against 0.199 mm on the same mesh). **The fine-mesh contact run was started and stopped before it finished; it is still to do**, and pad-by-pad load shares have not been extracted. Heatmaps: [weight](output/ccx_coarse_contact_vertical_1g_stress.png) · [uneven](output/ccx_coarse_contact_eccentric_1g_stress.png) · [side push](output/ccx_coarse_contact_rim_side_10N_stress.png).

### Solver change versus material change

Console weight, uniform pressure, max displacement:

| Step | Model | Displacement |
|---|---|---:|
| 1 | scikit-fem, first-order, in-house mesh, E 1,200 / ν 0.35 | 0.137 mm |
| 2 | Same, PA 2200 (E 1,650 / ν 0.40) | 0.0973 mm |
| 3 | CalculiX, first-order, the identical mesh and loads, PA 2200 | 0.0973 mm |
| 4 | CalculiX, second-order, Gmsh fine mesh, PA 2200 | 0.183 mm |

- **Material (1 → 2):** deflection falls 29%, as expected from the stiffer modulus.
- **Solver (2 → 3):** no difference to three figures; the two codes agree on the same mesh. The side-push case also matches (0.1463 mm in both).
- **Element order and mesh (3 → 4):** deflection nearly doubles. First-order tetrahedra are artificially stiff in thin bending members, so **every first-order displacement in section 4 and in v13's report is too low by roughly half**. Relative v13/v14 comparisons there still hold; absolute values do not.

### Still missing

- **Creep:** PA12 creeps under a constant load, and the console sits on the stand indefinitely. The data sheet gives no creep modulus, so long-term sag is not estimated.
- **Warm air:** the 1.80 MPa heat-deflection temperature is 64 °C (57 °C in Z) and stiffness falls well before that. Stresses here are far below 1.80 MPa in almost all of the part, but no temperature-dependent modulus was available and the air temperature around the stand is unmeasured.
- Layer-direction stiffness differences, moisture conditioning, impact, tipping and sliding are not modelled. The base is clamped, which hides lift-off and rocking.
- Results are on the simulation surface, not the print STL.

Data: `ccx/*/results.json`, `ccx/mesh_*.json`, `ccx/surf_*.json`.

## 6. Airflow with OpenFOAM (set up, not yet run)

The case generator (`openfoam/make_case.py`) and runner (`openfoam/run_case.sh`) exist. One no-stand case was meshed (164,032 cells, checkMesh OK) and its solve started cleanly before being stopped at iteration 86. **No OpenFOAM result exists yet.** The planned sweep, mesh check and comparison with section 3 are listed in [HANDOFF.md](HANDOFF.md).

## Checks performed

STL and 3MF agree in bounds; the body is one watertight, consistently wound component; intersection with the reference console plan and the nominal cavity above the seat is 0 mm³ ([geometry_review.json](analysis/geometry_review.json)). Not done for v14: opening-spacing preflight, slicing, printing, physical fit, thermal testing.

## Reproduce

Python packages: `source/requirements-fea.txt` and `source/requirements-solvers.txt` into `.venv-cad`. Solvers run in containers defined in [docker/compose.yaml](docker/compose.yaml).

```sh
.venv-cad/bin/python designs/v14/source/veil_v14.py designs/v14/output
clang++ -O3 -std=c++17 designs/v14/airflow/lbm.cpp -o /tmp/veil-lbm
VEIL_LBM=/tmp/veil-lbm designs/v14/source/run_checks.sh          # sections 1-4: reviews, renders, in-house stress and airflow

docker compose -f designs/v14/docker/compose.yaml build ccx
cd designs/v14/ccx
P=../../../.venv-cad/bin/python
$P ../source/remesh_surface.py ../analysis/regularized.stl 2.2 surf_fine.stl 0.35   # coarse: 3.0 ... 0.6, extra-fine: 2.2 ... 0.2
$P ../source/mesh_gmsh.py surf_fine.stl 2.2 mesh_fine.msh direct
$P ../source/build_ccx.py mesh_fine.msh fine_pressure pressure                      # or: fine_contact contact
../source/run_ccx.sh fine_pressure
$P ../source/post_ccx.py fine_pressure render
$P ../source/build_ccx_p1.py ../analysis/v14_fine_mesh.npz crosscheck_p1            # solver cross-check deck

cd ../openfoam
$P make_case.py cases/stand_q1p0 stand 1.0 2.5 && ./run_case.sh cases/stand_q1p0
```
