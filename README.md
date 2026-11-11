# PS5 Slim dock

A one-piece, sculptural vertical stand for the PS5 Slim Disc. **[Start with v10: the current dense-web design](designs/v10/README.md)** — unified round strands and a sleek curved underside, ready for aesthetic review. Earlier designs and their validation remain preserved below.

## Start here
- Read `docs/CONTINUE.md` for the current task and exact stopping point.
- Read `docs/claude-conversation.md` for the recovered design history.
- Inspect the original sketch in `references/IMG_6973.HEIC`.
- The supplied fan-made console model is in `references/PS5_Slim-a48efc06.zip` and extracted in `references/console-model/`.
- The complete v5 source archive is imported at `designs/imported/ps5_veil_stand_v5/`. All four user-supplied originals are preserved in `references/user-imports/`, with identities and hashes in `docs/import-manifest.json`.

Source chat: https://claude.ai/chat/f4d270b2-2594-4b75-a828-277e58a32ab0

v6 is generated and geometry-checked in `designs/v6/`. Start with [the v6 preview and files](designs/v6/README.md), [validation](designs/v6/VALIDATION.md), and [print-service brief](designs/v6/PRINT_SERVICE.md). No physical fit, print, strength or thermal validation has been performed.


## Current direction and design history

**[v10 is ready for aesthetic review](designs/v10/README.md), not yet user-approved.** View the [actual white/blue mesh](designs/v10/output/preview_v10.png), [reference console assembly](designs/v10/output/reference_assembly.png), [editable source](designs/v10/source/veil_v10.py), or [3MF](designs/v10/output/veil_v10_prototype.3mf).

The **151.32 × 244.47 × 53.22 mm** candidate uses a dense flowing web of 3.3 mm round strands, with three curved supporting rails and two ties underneath. It follows the user's latest Spider-Man / bird-nest direction; the earlier symbol-shaped strand sections and star underside are superseded. Geometry checks pass, but **no FEA has been run for v10**. Vendor slicing/support review and physical fit, load and thermal tests remain necessary.

v7, v8 and v9 are preserved historical candidates, not selected final designs. [Compact v8](designs/v8/README.md) established an approximately **151 × 244 mm** footprint, but its FE work stopped at meshing without a solved stress result. v9's structural analysis was cancelled following the user's rejection.

[Wider v7](designs/v7/README.md) retains actual [3D stress fields](designs/v7/output/stress_heatmap_3d.html) and a [structural-analysis report](designs/v7/STRUCTURAL_ANALYSIS.md). These are exploratory calculations with assumed material/contact and approximate geometry, not physical strength or thermal qualification; they do not validate later designs.

Original uploads, v5 and v6 remain preserved. Historical print-service briefs must not be used to order a superseding revision. The project repository is [tsonubin/ps5-slim-stand](https://github.com/tsonubin/ps5-slim-stand); access is private.
