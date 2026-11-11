# PS5 Slim dock

A one-piece, sculptural vertical stand for the PS5 Slim Disc. **[Start with v13: smoother, nearly level perimeter loops](designs/v13/README.md)** — the accepted shell direction with restrained rim height and fresh engineering studies. Physical qualification is pending. Earlier designs and their validation remain preserved below.

## Start here
- Read `docs/CONTINUE.md` for the current task and exact stopping point.
- Read `docs/claude-conversation.md` for the recovered design history.
- Inspect the original sketch in `references/IMG_6973.HEIC`.
- The supplied fan-made console model is in `references/PS5_Slim-a48efc06.zip` and extracted in `references/console-model/`.
- The complete v5 source archive is imported at `designs/imported/ps5_veil_stand_v5/`. All four user-supplied originals are preserved in `references/user-imports/`, with identities and hashes in `docs/import-manifest.json`.

Source chat: https://claude.ai/chat/f4d270b2-2594-4b75-a828-277e58a32ab0

v6 is generated and geometry-checked in `designs/v6/`. Start with [the v6 preview and files](designs/v6/README.md), [validation](designs/v6/VALIDATION.md), and [print-service brief](designs/v6/PRINT_SERVICE.md). No physical fit, print, strength or thermal validation has been performed.


## Current candidate: v13

[Veil v13](designs/v13/README.md) preserves the user-liked continuous mesh shell and lower-loop silhouette. The upper perimeter is nearly level at **38.03–40.70 mm**; finite Fourier guides remove abrupt local changes in both loops. Overall size: **150.34 × 241.28 × 40.70 mm**, **74.61 cm³**.

- [Actual assembly detail](designs/v13/output/assembly_base_detail.png), [standalone view](designs/v13/output/hero_v13.png), [3MF](designs/v13/output/veil_v13_prototype.3mf) and [STL](designs/v13/output/veil_v13_prototype.stl).
- [Geometry method](designs/v13/GEOMETRY_METHOD.md), [continuity checks](designs/v13/analysis/guide_continuity.json), [reference/mesh checks](designs/v13/analysis/light_geometry_review.json) and [vendor brief](designs/v13/PRINT_SERVICE.md).

Fresh [v13 FEA](designs/v13/STRUCTURAL_ANALYSIS.md) and [conditional airflow screening](designs/v13/airflow/AIRFLOW_REVIEW.md) are available, with [3D stress colors](designs/v13/output/stress_heatmap_3d.html) and [flow views](designs/v13/airflow/flow_streamlines_3d.png). Stress peaks remain unconverged, and the hypothetical airflow channel does not establish actual PS5 cooling loss. Lower rear-grille clearance and the real active vent map remain unresolved. This is a review prototype, **not yet ready for service-use printing**; internal junctions/contact and hardware vent spacing need further work.

## Preserved v12 shell study

[Veil v12](designs/v12/README.md) is a continuous sculpted shell with **72 irregular flowing openings**, integrated edges and a lower internal support web. The **150.40 × 240.62 × 48.04 mm** candidate is ready for aesthetic review; it is not yet a qualified console support.

- [Actual hero view](designs/v12/output/hero_v12.png), [console–shell transition](designs/v12/output/assembly_base_detail.png) and [reference assembly](designs/v12/output/reference_assembly_clean.png).
- [STL](designs/v12/output/veil_v12_prototype.stl), [3MF](designs/v12/output/veil_v12_prototype.3mf), [editable source](designs/v12/source/veil_v12.py) and [geometry method](designs/v12/GEOMETRY_METHOD.md).
- [English/Chinese vendor brief](designs/v12/PRINT_SERVICE.md) and [lightweight geometry checks](designs/v12/analysis/light_geometry_review.json).

The final mesh and reference-envelope checks pass. **No FEA has been run for v12**; historical stress results do not establish its strength. Physical fit, process-specific slicing and load/thermal checks remain unperformed.

## Preserved v11 geometry study

[Veil v11](designs/v11/README.md) refines the dense nest with periodic spline guides, eased strand roots, rounded rings and dedicated local blends at roots and crossings. It measures **151.71 × 244.56 × 53.22 mm** and is preserved as a historical geometry study. Its smoother connections did not satisfy the user's aesthetic request.

- [Actual mesh preview](designs/v11/output/preview_v11_clean.png) and [reference console assembly](designs/v11/output/reference_assembly_clean.png).
- [Flat-shaded junction comparison](designs/v11/output/junction_comparison_flat.png), [geometry method](designs/v11/GEOMETRY_METHOD.md) and [editable source](designs/v11/source/veil_v11.py).
- [3MF](designs/v11/output/veil_v11_prototype.3mf), [compressed STL](designs/v11/output/veil_v11_prototype.stl.gz) and [print-service brief](designs/v11/PRINT_SERVICE.md). Decompress the STL gzip before importing; the 110 MB raw STL remains local.

The final mesh and reference-envelope checks pass. Mathematical guide continuity does not establish exact global surface continuity, physical fit or structural safety. **No FEA has been run for v11**; real slicing/support review and physical fit, load and thermal tests remain necessary.

## Preserved history

[v10](designs/v10/README.md) established the dense unified round-strand direction and is preserved. Earlier v7/v8/v9 concepts remain historical. v8 FE preparation stopped at meshing without a solved result; v9 analysis was cancelled after aesthetic rejection.

[Wider v7](designs/v7/README.md) retains actual [3D stress fields](designs/v7/output/stress_heatmap_3d.html) and a [structural-analysis report](designs/v7/STRUCTURAL_ANALYSIS.md). These exploratory calculations do not validate later geometries. Original uploads, v5 and v6 remain preserved; historical vendor briefs must not be used to order another revision.

The project repository is [tsonubin/ps5-slim-stand](https://github.com/tsonubin/ps5-slim-stand); access is private.
