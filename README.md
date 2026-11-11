# PS5 Slim dock

A one-piece, sculptural vertical stand for the PS5 Slim Disc. **[Start with v12: a continuous sculpted shell](designs/v12/README.md)** — irregular rounded openings and integrated edges, ready for aesthetic review. Physical qualification is pending. Earlier designs and their validation remain preserved below.

## Start here
- Read `docs/CONTINUE.md` for the current task and exact stopping point.
- Read `docs/claude-conversation.md` for the recovered design history.
- Inspect the original sketch in `references/IMG_6973.HEIC`.
- The supplied fan-made console model is in `references/PS5_Slim-a48efc06.zip` and extracted in `references/console-model/`.
- The complete v5 source archive is imported at `designs/imported/ps5_veil_stand_v5/`. All four user-supplied originals are preserved in `references/user-imports/`, with identities and hashes in `docs/import-manifest.json`.

Source chat: https://claude.ai/chat/f4d270b2-2594-4b75-a828-277e58a32ab0

v6 is generated and geometry-checked in `designs/v6/`. Start with [the v6 preview and files](designs/v6/README.md), [validation](designs/v6/VALIDATION.md), and [print-service brief](designs/v6/PRINT_SERVICE.md). No physical fit, print, strength or thermal validation has been performed.


## Current candidate: v12

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
