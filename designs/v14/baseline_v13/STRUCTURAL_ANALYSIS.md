# v13 structural analysis — solved fields, unresolved peak stress

Actual solid finite-element results are in the rotatable 3D viewer (`output/stress_heatmap_3d.html`, available at Git tag `v13`), with static gravity quality-check heatmap (`output/v13_quality_result_vertical_1g_stress.png`, available at Git tag `v13`) and finer side-load heatmap (`output/v13_fine_result_rim_side_10N_stress.png`, available at Git tag `v13`). These are computed stress colors, not temperature. Volumetric ParaView data are delivered locally as `output/v13_fine_result.vtu` and `output/v13_quality_result.vtu`.

**The design has not passed strength qualification.** Global displacement is fairly consistent between two interior meshes, but raw local stress peaks change strongly and move between meshes. An additional mesh-quality trial reduces the peak but does not stabilize it. The internal support web carries the dominant gravity stresses. It contains real sharp reentrant intersections deserving further engineering attention; the numerical peaks cannot yet define a reliable failure location or a justified reinforcement size.

## Model and loading

- Millimeters, newtons and MPa. Assumed homogeneous isotropic linear elasticity: E = 1,200 MPa, Poisson ratio 0.35. These are illustrative stiffness inputs, not measured vendor/process properties. No allowable strength or safety factor is assigned.
- Console gravity: 31.392 N, corresponding to an assumed 3.2 kg mass, uniformly distributed over nearly horizontal boundary triangles within 0.3 mm of the 30 mm seat and inside the fan-made reference core footprint. Effective selected area is 264.769 mm². Independent owner-tetrahedron normal checks confirm all selected faces point upward. This is an imposed pressure model, not a solved console/stand contact problem.
- Eccentric gravity: the same force on the selected contact with x > 8 mm; area 45.639 mm². This represents a prescribed uneven load pattern, not a specific physical console position. The mass center and actual hardware contact have not been measured.
- Side load: gravity plus 10 N in +X distributed over the local upper-shell boundary region x > 40, 15 < y < 100, z > 36 mm. Both inner and outer faces of that region participate. It is a nodal resultant distributed through a region, not pressure exclusively on the outside. Its centroid is approximately (51.60, 56.78, 38.60) mm. It is **not a push at the top of the console**.
- Base nodes less than 0.2 mm above the simulation geometry's lowest point are fixed in all translations. This assumes a clamped/bonded base. It suppresses sliding, lift-off, rocking and tipping, which can govern real use.
- Stand self-weight, orthotropic print layers, nonlinear contact, yielding/fracture, creep, heat-softening, buckling, drop/impact and fatigue are omitted. A reported 3g entry is only three times the linear gravity result, not a dynamic simulation.

## Surface approximation and tetrahedra

The frozen manufacturing STL has SHA256 `bea7633ae9056bdd5e5f3f4c0e4ced1c9958bf9ea5c77ac0db26fd036f9fed11`. Direct TetGen meshing rejected that detailed surface with “input surface mesh contain self-intersections”; this meshing failure does not independently locate or establish a production mesh defect.

The simulation-only surface uses exact CAD horizontal sections rasterized at 0.45 mm pitch, Gaussian smoothing at 0.55 voxel sigma, an isosurface, topology-preserving decimation and bounded repair. It does not replace manufacturing CAD. Its volume is 73.897 cm³ versus CAD 74.605 cm³ (−0.949%). Bidirectional sampled surface deviation is 0.198 mm at P95 and 0.894 mm maximum. These are finite sampled comparisons, not a guaranteed Hausdorff bound. The maximum deviation is significant relative to nominal 2.8 mm walls; local peak stresses and precise contact are therefore provisional. Contact/arch roots are also smoothed.

The paired meshes keep the simulation surface facets fixed (`nobisect=True`): 582,051 coarse and 712,354 finer first-order tetrahedra. The controls are respectively target maximum volume 2 / 0.4 mm³ and radius-edge ratio 2 / 1.4. These are requested controls, not guarantees that every element meets them; fixed facets and Steiner limits leave badly shaped elements. The additional 684,668-element optimized-quality mesh permits surface changes; its volume differs from the regularized surface by only −0.0024%, but this alone does not certify local geometric fidelity. It is a gravity-only diagnostic, not a fully converged replacement for the paired load cases.

## Results and mesh sensitivity

| Mesh | Case | Tetrahedra | Max displacement (mm) | Raw peak (MPa) | Volume-weighted P95 (MPa) |
|---|---|---:|---:|---:|---:|
| Coarse | vertical_1g | 582,051 | 0.15448 | 30.6472 | 0.41899 |
| Coarse | eccentric_1g | 582,051 | 0.09823 | 15.0880 | 0.40692 |
| Coarse | rim_side_10N | 582,051 | 0.21129 | 31.5933 | 0.49429 |
| Finer | vertical_1g | 712,354 | 0.15705 | 51.2531 | 0.42269 |
| Finer | eccentric_1g | 712,354 | 0.10150 | 30.0082 | 0.41429 |
| Finer | rim_side_10N | 712,354 | 0.22271 | 51.6070 | 0.50356 |
| Quality diagnostic | vertical_1g | 684,668 | 0.14910 | 21.6075 | 0.41153 |

For gravity, coarse-to-finer maximum displacement increases 1.66% and volume-weighted P95 stress 0.88%, while the raw peak increases 67.24% and moves. The optimized-quality gravity check gives 0.14910 mm, 0.41153 MPa P95 and 21.6075 MPa peak. **Do not interpret the lower peak as a verified improvement to the stand:** the CAD is identical and only meshing changed.

The minimum mean-ratio tetrahedron quality is around 5–7 × 10⁻⁶ (1 is a regular tetrahedron). The coarse/finer/quality meshes retain 439/423/264 elements below 0.001. No high-stress elements or raw peaks were discarded. `analysis/fea_review.json` records quality, peak element volumes/locations, nearby volume-weighted stress and displacement locations. Neither surface convergence nor reliable peak convergence is established.

## Investigation and iteration decision

The coarse gravity peak is near (−11.67, 52.64, 16.22) mm on the longitudinal support. Its tetrahedron is only 4.24 × 10⁻⁵ mm³; stress averaged in the surrounding 3 mm region is much lower (volume-weighted P95 0.567 MPa). The finer gravity peak moves to (−23.62, −29.70, 26.39) mm. The quality trial moves it again to (−20.98, −45.29, 21.14) mm; the local 3 mm-region P95 there is 0.528 MPa versus the raw 21.6075 MPa peak. These observations suggest numerical/local-notch sensitivity but do not prove the peaks are harmless.

Read-only CAD inspection found the neighboring support centerline crossing near (−13.60, 48.67) mm, with roughly 12–14 mm vertical material below the top contact and no near-zero tangential neck. There are unfilleted reentrant root edges with approximately 68° and 114° local face turns. The external shell need not be thickened based on this result. A sensible next engineering iteration is a smoothly filleted internal junction, checked with reliable local meshing and actual process/material/contact data. No arbitrary collar was added merely to lower one unstable numerical maximum. The approved exterior is preserved.

## Numerical verification and use of the plots

The formulation uses scikit-fem first-order vector tetrahedra, isotropic elasticity, algebraic-multigrid-preconditioned conjugate gradients and elementwise von Mises stress from displacement gradients. The analytical 10 × 10 × 30 mm uniform-compression benchmark reproduces displacement to relative error 1.33 × 10⁻¹⁵. Stand relative residuals range from about 1.36 × 10⁻⁸ to 2.91 × 10⁻⁷; reaction forces balance the loads to approximately 10⁻⁷ N or better. The quality gravity diagnostic also checks moment equilibrium, error 6.4 × 10⁻⁸ N·mm. These numerical checks do not validate the physical assumptions or resolve poor element quality.

PNG colors use a shared 0–0.6 MPa scale with higher values saturated red; the **unfiltered peak is printed separately**. The HTML offers raw-peak, common-peak and P95 color scales, plus nodal displacement and explicit deformation exaggeration. P95 mode is labeled as saturating peaks. All boundary triangle colors come from their adjacent solved tetrahedron. The gravity-only quality model exposes only its actual solved case, never zero-filled missing cases. Interactive browser QA has not been completed; standalone payload/JavaScript integrity and actual local PNG/VTU readback are checked.

## Reproduce

Use `.venv-cad` with `source/requirements-fea.txt` from the repository root. Source and installed package versions are preserved.

```sh
.venv-cad/bin/python designs/v13/source/verify_solver.py
.venv-cad/bin/python designs/v13/source/voxel_surface.py designs/v13/output/veil_v13_prototype.stl .45 designs/v13/analysis/regularized.stl
FEA_NO_OPT=2 .venv-cad/bin/python designs/v13/source/mesh_fea.py designs/v13/analysis/regularized.stl 2 designs/v13/analysis/v13_coarse_mesh.npz
FEA_NO_OPT=3 .venv-cad/bin/python designs/v13/source/mesh_fea.py designs/v13/analysis/regularized.stl .4 designs/v13/analysis/v13_fine_mesh.npz
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv-cad/bin/python designs/v13/source/solve_fea.py designs/v13/analysis/v13_fine_mesh.npz designs/v13/analysis/v13_fine_result
.venv-cad/bin/python designs/v13/source/mesh_fea.py designs/v13/analysis/regularized.stl .4 designs/v13/analysis/v13_quality_mesh.npz
FEA_CASE=vertical_1g OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv-cad/bin/python designs/v13/source/solve_fea.py designs/v13/analysis/v13_quality_mesh.npz designs/v13/analysis/v13_quality_result
.venv-cad/bin/python designs/v13/source/review_fea.py
.venv-cad/bin/python designs/v13/source/render_stress.py v13_fine_result
.venv-cad/bin/python designs/v13/source/export_heatmap.py
.venv-cad/bin/python designs/v13/source/export_stress_vtu.py v13_fine_result
```

Run `solve_fea.py` on the coarse mesh as well to reproduce all viewer models. Raw mesh/result arrays and VTU are local artifacts; JSON, source, PNG and self-contained HTML are retained for review.

Method references: [scikit-fem examples](https://scikit-fem.readthedocs.io/en/latest/listofexamples.html), [TetGen wrapper API](https://tetgen.pyvista.org/api.html). Neither source supplies a printed-material allowable. Thermal/airflow modeling is a separate report; these stress results imply no ventilation safety claim.
