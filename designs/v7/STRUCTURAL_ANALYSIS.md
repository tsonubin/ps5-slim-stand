# v7 structural simulation — exploratory solid FEA

Actual solved stress and displacement fields are available in [the rotatable 3D viewer](output/stress_heatmap_3d.html), [baseline heatmap](output/full_star_fine_result_stress.png), [reinforced heatmap](output/full_star_reinforced_fine_result_stress.png) and `output/full_star_reinforced_fine_result.vtu` (ParaView-compatible volumetric data). These are stress colors, not temperature results. No CFD or thermal simulation was performed.

The side-load result identified a drive-side lower strand/rib junction near (58, 68, 30) mm. A smoothly blended collar enlarges strand profiles locally by up to 30%, centered at (57.7, 67.6, 30.3) mm, with Gaussian falloff scales (12, 12, 9) mm. It adds 0.384 cm³ (0.20%) to the manufacturing CAD. On the finer paired meshes, maximum displacement changes from 0.2418 to 0.1995 mm (17.5% lower); peak von Mises changes from 4.911 to 4.948 MPa (0.7% higher). The apparent peak reduction on the refined mesh did not survive finer meshing. The collar is only a provisional stiffness improvement; it is not a demonstrated peak-stress fix, a strength certification, or proof that weak points are eliminated. Peak location can move after reinforcement.

## Loading and assumptions

- Units: millimetres, newtons, MPa. Homogeneous isotropic linear elasticity, E=1200 MPa and Poisson ratio 0.35. These are assumptions, not measured printed-material properties or a material qualification.
- Distributed gravity: 31.392 N (assumed 3.2 kg console) on nearly horizontal rib-top boundary triangles inside a fan-made reference black-core footprint. The hardware mass/contact surfaces have not been measured here. Stand self-weight is omitted.
- Eccentric load: the same 31.392 N restricted to contact with x > 8 mm, approximately the +X half. This is an imposed pressure pattern, not a contact solution.
- Side case: gravity plus a 10 N +X force distributed over the upper-shell boundary patch x > 40, 15 < y < 100, z > 45 mm. This is a local push on the stand, **not a push at the top of the console**. The console itself is not meshed. Patch area and moment arm are geometry-dependent.
- Nodes within 0.2 mm of the lowest point of each regularized whole-stand mesh are fixed in all translations. This assumes bonded/clamped feet. Real feet can slide, lift, rock or tip, so this condition can overstate stiffness. Real console/stand contact and cover loading are unresolved.
- No plasticity, fracture, anisotropy, inter-layer weakness, creep, thermal softening, buckling, impact or fatigue model. The 3g JSON entry is just linear scaling of the gravity solution, not a transient/drop simulation. No safety factor is reported because a defensible allowable strength is unavailable.

## Geometry approximation and why the colors are provisional

Direct tetrahedralization of the detailed CAD failed at small facets/junctions. Several alternate remeshes with excessive shape/volume loss were rejected. The accepted **simulation-only** surface uses exact CAD horizontal slices on a 0.6 mm grid, hole/component processing, Gaussian smoothing (0.55 voxel sigma), an isosurface, topology-preserving decimation, smoothing and a small repair. It does not replace the manufacturing STL/3MF.

Baseline simulation volume is 190.566 cm³ versus CAD 192.788 cm³ (−1.152%). Reinforced simulation volume is 190.956 cm³ versus CAD 193.172 cm³ (−1.147%). Bidirectional sampled surface distances are approximately 0.35 mm at P95 and 1.845 mm maximum. These are sampled distances, **not a guaranteed Hausdorff bound**. The largest error is comparable to the smallest 1.6 mm X arms. Consequently, actual symbol-profile notches, local radii and thin-section peak stresses are not resolved reliably. Volume agreement alone cannot establish local fidelity.

The manufacturing output includes less than 1 mm³ of sealed microvoid cleanup at intersecting strands; no substantial disconnected structural parts were discarded. The simulation smoothing also changes contact area: about 1618 mm² is used for the whole-model pressure selection versus about 2119 mm² CAD rib-top overlap. This contributes uncertainty beyond numerical residuals.

## Mesh sensitivity

| Geometry / mesh | Tetrahedra | Side-load max displacement (mm) | Peak von Mises (MPa) | Volume-weighted P95 (MPa) |
|---|---:|---:|---:|---:|
| Baseline coarse | 645,147 | 0.176329 | 4.5417 | 0.12706 |
| Baseline refined | 779,324 | 0.228406 | 4.8662 | 0.14352 |
| Baseline finer | 1,031,620 | 0.241801 | 4.9113 | 0.14784 |
| Reinforced refined | 780,296 | 0.189366 | 3.8032 | 0.14079 |
| Reinforced finer | 1,031,405 | 0.199523 | 4.9475 | 0.14270 |

The baseline displacement increases 29.5% from coarse to refined and another 5.9% from refined to finer. This is **not a fully converged solution**. TetGen refinement holds the regularized surface facets fixed (`nobisect=True`); the runs mainly refine tetrahedral interiors, so they do not demonstrate surface-resolution convergence. Coarse/refined eccentric peaks also change substantially. Stress at fixed edges and thin junctions must not be treated as a mesh-independent failure prediction.

Reinforcement comparisons use matching mesher settings on each geometry: refined quality ratio 2; finer quality ratio 1.4 and target maximum tetrahedron volume 0.4 mm³. Boundary constraints and sampling rules are the same, but connectivity and exact nodes differ. Element limits and fixed surfaces mean requested sizing is a mesher control, not a guarantee of uniform element size.

## Solver checks

The formulation uses first-order vector tetrahedra in scikit-fem, linear isotropic elasticity, algebraic multigrid preconditioning and conjugate gradients. Per-tetrahedron von Mises stress comes from the displacement gradient. P95 is weighted by tetrahedron volume; it does not substitute for peak or failure assessment.

The same formulation reproduces a 10 × 10 × 30 mm uniaxial block under 0.31392 MPa traction: analytical displacement −0.007848 mm, relative error 1.33e−15 (`analysis/solver_benchmark.json`). This checks implementation and units for a uniform-stress case; it does not validate the stand geometry, load model or bending convergence. Solver relative residuals are about 1e−8. Summed support reactions balance applied forces to numerical precision (approximately −10, 0, +31.392 N for the side case). Small algebraic residuals do not remove discretization/model error.

## Star versus honeycomb, and the rejected toe trial

| Ribs-only concept | Material volume (cm³) | Contact area (mm²) | Gravity displacement (mm) | Gravity peak (MPa) | Gravity P95 (MPa) |
|---|---:|---:|---:|---:|---:|
| Star | 116.531 | 2119.9 | 0.0004791 | 0.5881 | 0.01931 |
| Rounded-toe star trial | 119.197 | 2119.9 | 0.0004629 | 1.4294 | 0.01748 |
| Compact honeycomb trial | 103.559 | 1206.1 | 0.0007197 | 0.0556 | 0.02759 |

The star support is stiffer in these assumed load cases, but the compact honeycomb has less material, a different footprint/contact area and a much coarser mesh. This is not a controlled equal-mass/equal-boundary strength comparison. Its lower peak cannot establish superiority. Retain the star for the user's preference and current load path, not as a universal structural winner.

The rounded-toe trial modestly reduced bulk displacement/P95 but increased the reported peak from about 0.588 to 1.429 MPa under gravity. The peak is constraint/mesh-sensitive; the trial was not adopted or represented as a successful stress reduction.

## Reading and reproducing the results

The viewer initially selects reinforced/finer and gravity plus the 10 N patch load. Drag to rotate, wheel to zoom; change load, stress/displacement field, common/peak/P95 scale, or explicit deformation exaggeration. Colors use solved fields; deformation is off by default. P95 mode saturates high stresses and labels that fact. Static images use a common 0–0.6 MPa scale, with higher stresses saturated red and the absolute peak stated separately.

The HTML contains baseline-finer and reinforced-finer fields, embedded as gzip data; it needs a current browser with the built-in DecompressionStream API and does not fetch external resources. `export_heatmap.py --all` can build the much larger exploratory-history viewer. VTU includes volumetric tetrahedra, cell stress and nodal displacement for all three solved cases. Results are in `analysis/*result.json`; raw arrays are reproducible local caches and may be distributed separately from Git.

From project root, using the installed CAD environment:

```sh
.venv-cad/bin/python designs/v7/source/verify_solver.py
.venv-cad/bin/python designs/v7/source/voxel_surface.py designs/v7/output/veil_v7_prototype.stl .6 designs/v7/analysis/reinforced_regularized.stl
FEA_NO_OPT=3 .venv-cad/bin/python designs/v7/source/mesh_fea.py designs/v7/analysis/reinforced_regularized.stl .4 designs/v7/analysis/full_star_reinforced_fine_mesh.npz
.venv-cad/bin/python designs/v7/source/solve_fea.py designs/v7/analysis/full_star_reinforced_fine_mesh.npz designs/v7/analysis/full_star_reinforced_fine_result
.venv-cad/bin/python designs/v7/source/export_heatmap.py
.venv-cad/bin/python designs/v7/source/export_stress_vtu.py full_star_reinforced_fine_result
```

Method references: [scikit-fem documentation](https://scikit-fem.readthedocs.io/), [elasticity examples](https://scikit-fem.readthedocs.io/en/latest/listofexamples.html), [TetGen wrapper API](https://tetgen.pyvista.org/api.html), [TetGen features](https://wias-berlin.de/software/tetgen/features.html). Software methods do not supply printed-material allowables.

Interactive browser QA could not be completed: the automation browser denied the local `file://` URL, and no workaround was attempted. The standalone HTML is generated from solved arrays and receives a JavaScript syntax check; the PNG fields are independently rendered locally. Open the HTML in a normal browser manually to review interaction.

Before hardware use: qualify the chosen vendor/process/material with coupons, inspect actual contact/vents/ports with the gauge and prototype, obtain nonlinear contact and material-informed analysis if required, and perform restrained dummy-load/creep tests. Ventilation evidence and unresolved fit constraints remain in [v6 validation](../v6/VALIDATION.md). No thermal or physical-fit claim follows from these stress plots.
