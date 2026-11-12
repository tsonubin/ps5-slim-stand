# Veil — a vertical stand for the PS5 Slim

A one-piece, 3D-printed stand that lifts a PS5 Slim (disc model, CFI-20xx) 30 mm off the desk inside a perforated, sculpted shell.

> **Do not print this version to hold a console.** On 2026-11-12 the seat layout and both simulated tests were found to rest on a wrong picture of the console's underside. The fan-made reference model shows a flat, symmetric base with no openings. A real CFI-2009 has a row of about 17 vent slots in a recessed strip along the disc-drive side of the black base. Two of the stand's four pads and one rib sit under that strip. The stress results assume contact on a surface that is not there, and the airflow results draw air through a solid face instead of through those slots. Sections below are kept as a record and are **not valid** until the seat is redesigned against measurements of real hardware.

**Status: review prototype.** The geometry is final for a first print, and it has been through simulated stress and airflow tests. Nothing has been printed, fitted to a console or heat-tested yet.

![Veil v14 with the reference console](designs/v14/output/assembly_base_detail.png)

[Standalone view](designs/v14/output/hero_v14.png) · [four views](designs/v14/output/preview_v14_clean.png) · [turntable](designs/v14/output/turntable_v14.png) · [full engineering report](designs/v14/README.md)

## Design philosophy

- **One continuous surface, not a frame.** The shell is a single sculpted wall with 72 irregular, rounded openings that drift around it in one flowing pattern. It should read as part of the console's own curves, in the spirit of Zaha Hadid's buildings, and not as a basket of struts.
- **Quiet silhouette.** The outline is strictly convex with no ripples, the rim is nearly level, and the base ring is flat. The interest is in the openings, not in the outline.
- **Structure stays out of sight.** Four ribs and four pads under the console carry the weight. From normal viewing angles only the shell is visible.
- **The console sits on its strong part.** The pads touch only the flat black core at the bottom of the console, at least 6.6 mm in from its edge. The white covers carry nothing.
- **Loose, forgiving fit.** 1.5 mm clearance all round the console, checked with a cheap flat gauge before the full print.
- **Air first.** No floor, no closed panels. With the desk sealing the bottom, all air reaches the console's underside through the wall openings, so their area (about 112 cm²) is larger than the underside they feed (about 70 cm²).
- **Compact footprint.** 153 × 247 mm on the desk, for a cavity of about 99 × 219 mm.
- **Made by a print service.** Shaped for laser sintering in one piece with no supports.
- **Say what is known.** Every number here is labelled as simulation, data sheet or assumption. Nothing is called validated until a part has been printed and tested.

## Specifications

| | |
|---|---|
| Fits | PS5 Slim, disc model (CFI-20xx), standing vertically. Based on a fan-made 3D model of the console, not a scan of real hardware |
| Overall size | 152.83 × 247.08 × 40.70 mm |
| Volume / mass | 79.26 cm³; about 74 g in sintered PA12 (0.93 g/cm³) |
| Console lift | 30 mm from desk to the underside of the console |
| Cavity | About 99 × 219 mm outline, 1.5 mm nominal clearance to the console all round |
| Rim height | 38.0 to 40.7 mm above the desk (8 to 11 mm above the console's underside) |
| Wall | 2.8 mm at the two tight ends, rising to 3.5 mm along the long sides (80% of the perimeter is above 3.3 mm); thickened inward only |
| Wall shape | Strictly convex in plan; tightest rim radius 10.7 mm; leans at most 43.6° from vertical |
| Openings | 72, with rounded corners, about 112 cm² in total (about 92 cm² below the console) |
| Seat | Four flat pads, each a 21.6 × 10.6 mm land, at (±16.5, +44) and (±11.5, −44) mm; 771 mm² in total |
| Seat pressure | 0.041 MPa mean under an assumed 3.2 kg console |
| Ribs | Four, 2.8 mm thick, crest 1 mm below the seat so only the pads touch the console; each a single open arch; crossings and wall junctions filleted (3 mm, 1.5 mm inside the wall thickness) |
| Base | Flat open ring; no floor |
| Material and process | White PA12 nylon, laser sintered (SLS), bead-blasted. HP Multi Jet Fusion PA12 if black is wanted |
| Reference material data | EOS PA 2200: modulus 1,650 MPa, tensile strength 48 MPa in the build plane and 42 MPa along the build direction, heat deflection 64 °C at 1.80 MPa |
| Files | 3MF and STL of the stand, a flat cavity gauge (106.91 × 227 × 1.6 mm) and a local print coupon (58 × 36 × 40.7 mm) |

## Stress test (simulation)

Method: Gmsh meshes with second-order tetrahedra, solved with CalculiX 2.20 as linear elastic PA 2200, base clamped, on three mesh densities (102,000 to 297,000 elements). The console is 3.2 kg (31.4 N). It is applied either as an even pressure on the pads or as a rigid flat plate resting on them.

| Load case | Deflection | Highest stress | Safety factor (build plane / build direction) |
|---|---:|---:|---:|
| Console weight | 0.17 mm | 4.7 MPa | 10 / 8.9 |
| Weight placed 10 mm off-centre | 0.23 mm | 6.1 MPa | 7.9 / 6.9 |
| Weight plus a 10 N sideways push on the rim | 0.21 mm | 6.6 MPa | 7.2 / 6.3 |
| Worst value in any run (off-centre weight, rigid-plate contact) | 0.13 mm | 8.1 MPa | 5.9 / 5.2 |

![Stress under weight plus a side push](designs/v14/output/ccx_fine_pressure_rim_side_10N_stress.png)

- Deflection and the bulk of the stress agree to within 2% between the two finer meshes. 99.9% of the material stays at or below 2 MPa.
- Under plain weight the peak is stable across all three meshes (4.6, 4.9, 4.7 MPa). An earlier build peaked at 11 to 15 MPa where one rib end touched the rim of a wall opening at a single point; blending that joint removed it.
- Two peaks still rise as the mesh is refined, so they are not final numbers: the wall-strut peak under the side push, and the contact peak at a pad edge.
- All four pads stay loaded in every case. Under plain weight they carry 18 to 30% each.
- Safety factors compare with short-term, room-temperature data-sheet strength. Slow sag under constant weight (creep), softening in warm air, tipping and sliding are not modelled.

Details: [engineering report, sections 4 and 5](designs/v14/README.md).

## Wind test (airflow simulation)

There is no physical wind-tunnel test. Two computer models answer the same question: with the desk sealing the bottom, how much does the stand restrict air reaching the console's underside through the wall openings?

Set-up for both: solid desk, solid cap at the console's underside, air drawn evenly through the whole underside, sides open to still air. **The flow rates are assumptions**; the console's real fan flow and vent positions have not been measured.

| Assumed flow | Pressure drop, no stand | Pressure drop, with stand | Added by the stand |
|---:|---:|---:|---:|
| 0.25 m³/min | 0.11 Pa | 0.39 Pa | 0.28 Pa |
| 0.5 m³/min | 0.42 Pa | 1.45 Pa | 1.02 Pa |
| 1.0 m³/min | 1.61 Pa | 5.95 Pa | 4.34 Pa |
| 1.5 m³/min | 3.50 Pa | 13.54 Pa | 10.04 Pa |

![Airflow with and without the stand](designs/v14/output/airflow_openfoam.png)

- These are OpenFOAM v2412 results (steady flow, k-ω SST turbulence model). The stand multiplies this set-up's pressure drop by 3.4 to 3.9. At equal suction, about half the flow gets through compared with a console hovering in open air.
- A second, in-house model (lattice-Boltzmann, very slow flow) gives a resistance ratio of 4.3, within about 25% of OpenFOAM's. Both agree on the pattern: about 70% of the air comes in through the two long sides.
- Accuracy: the with-stand values hold to about ±5% when the mesh is refined. The no-stand value moves by 21%, so the ratio is less certain than the absolute numbers.
- Whether a few pascals matter depends on the console's fan, which is not characterised here. This is not a cooling prediction.

Details: [engineering report, sections 3 and 6](designs/v14/README.md).

## Notice for printing

Full brief for the print service, in English and Chinese: [designs/v14/PRINT_SERVICE.md](designs/v14/PRINT_SERVICE.md).

1. **Fit check first.** Print only the flat gauge and the small coupon at home in PETG. Lay the gauge around the console's base to check the outline; use the coupon to judge the openings and a rib at full size. Neither can carry the console.
2. **Then the stand**, in white SLS PA12, bead-blasted, in one piece, flat with the base down.
3. **Scale:** millimetres, 100%. Do not scale the part to fit a build volume; the cavity must stay true to size.
4. **Do not let the service alter it:** no filled or closed openings, no added floor, no thickened walls, no vapour smoothing or coating. The openings are the air path.
5. **Keep as printed:** the four flat pad tops, the flat base ring and the inner cavity outline. Ask for the expected flatness of the pads and base; uneven pad tops change how the weight is shared.
6. **Ask which PA12 powder and machine they use.** The strength figures above are for EOS PA 2200 and another powder may differ.
7. **Do not print the whole stand in PETG or PLA and trust these margins.** PETG's strength is 29% lower in the plane and 45% lower between layers, and it softens far earlier (heat deflection 69 °C against 157 °C at 0.45 MPa).
8. **Before the console goes on it:** check that it rests on the black core and not on the white covers, that cables, the disc slot and every vent are clear, and that the stand does not rock.

## Still open

- **Rear grille.** Teardown photographs show a grille low on the back of the Slim. The rim stands 8 to 11 mm above the console's underside; whether it overlaps that grille on real hardware has not been checked.
- **Vents and fan flow** of the real console are unmeasured.
- **One opening looks slightly different** after the stress fix: a small rounded pocket where a rib end joins its rim ([before and after](designs/v14/output/rib_foot_opening_before_after.png)). Not yet reviewed for appearance.
- No slicing, printing, fit, load, creep or thermal test has been done.

## Repository

| Path | Contents |
|---|---|
| [designs/v14/](designs/v14/README.md) | The design: generator source, exports, renders, stress and airflow studies, print brief |
| `designs/v14/baseline_v13/` | A few files of the previous version that the v14 reports compare against |
| `references/` | The fan-made console model, the original sketch and the first uploaded files |
| `src/` | The mesh renderer used for the pictures |
| `docs/` | Project history and notes |

Only v14 is kept on this branch. Earlier versions (v5 to v13) were removed from the tree; each remains available at its Git tag, listed in [docs/VERSION_HISTORY.md](docs/VERSION_HISTORY.md).

Console reference model: [PS5 Slim by rtql8d on Sketchfab](https://sketchfab.com/3d-models/ps5-slim-a48efc06663541a1bc19297995fea91d).
