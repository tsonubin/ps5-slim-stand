# v6 validation — 2026-11-11

**Status: geometry-checked development prototype. No physical print, printer-specific slicing, strength qualification, CFD or thermal measurement has been performed.**

## Verified computationally

- STL, 3MF, gauge and test section reopen as connected, watertight meshes with consistent winding. The main STL has 62,518 triangles. STL and 3MF dimensions/volumes agree.
- Size: 151.3035 × 244.1810 × 63.3491 mm. Geometric volume: 107.82494 cm³. See `output/validation.json` for exact bounds, hashes and counts.
- Boolean intersection with the **inherited console plan extruded above the 30 mm seat** is 0 mm³. This checks that reference envelope, not the real console or a complete 3D fit. The nominal clearance envelope itself has a tiny 0.0112 mm³ intrusion after mesh simplification; nominal 1.5 mm clearance is not an exact everywhere-minimum measurement.
- A reference black-core section 0.5 mm above its modeled base overlaps the rib tops by about 925 mm². This supports the intended load path (core → curved ribs → desk), but does not establish actual contact, contact pressure distribution or absence of vent obstruction.
- A geometric screen evaluated 316 horizontal sections at 0.2 mm spacing. No new section islands lacked overlap with the preceding section. Local material extends outside a 45° support envelope: the worst layer is approximately 15.2 mm² at z=48.5 mm. Other review heights are 25.5, 39.9 and 58.7 mm. See `layer_screen.png` and `layer_screen.json`.
- All four original uploaded files still match their import SHA-256 values. All ten imported v5 files match their source ZIP, including the original fit gauge. Evidence: `originals_check.json`.

The generator verifies a single CAD body and does not discard disconnected stand fragments. A 0.05 mm CAD simplification and float32 export cleanup remove only collapsed-index and duplicate faces; the final STL is then reopened and checked. The print-test section deliberately keeps the largest connected component of a crop; it is not a full stand or a strength specimen.

## What the layer screen means

Each new geometric cross section is compared with the previous section expanded by 0.2 mm. This approximates a 45° growth envelope. It does **not** model extrusion width, toolpaths, bridges, layer adhesion, seam placement, cooling, thin-wall decisions or support removal. Accordingly, **support-free printing is not established**. No PrusaSlicer/OrcaSlicer/Cura executable was available in the checked application/tool locations; the installed `Orca.app` is not OrcaSlicer. The vendor must perform the actual process-specific slice. No production G-code is included.

The teardrop, triangle and diamond cutter profiles have angled roofs, but intersecting them with curved walls changes local conditions. A round opening has been adapted to a teardrop instead of retaining a difficult horizontal crown. Nominal widths are design inputs, not a full wall-thickness audit of every junction. Have the vendor check small fragments, disappearing features, rim undersides and lattice junctions.

## Conditional stability estimate — not a guarantee

Using the convex hull of the modeled desk-contact section, a 3.2 kg console, an assumed console center of mass 179 mm above its bottom, 30 mm lift, and a top push 388 mm above the desk gives **4.86–5.94 N** to tip the assembly over the nearest support edge across nine assumed CoM positions (X = −5, 5, 15 mm; Y = −15, 0, 15 mm). The corresponding tilt estimates are 16.0–19.3°.

These calculations assume rigid, no-slip coupling between console and stand, solid-PLA-equivalent stand mass and a flat rigid desk. The loose cavity has no positive screw retention, so the console may move or rock independently and fail earlier. Real CoM, cable loads, friction, printer defects, impact response and creep are unknown. These figures are not a safety factor and are not a comparison with Sony's stand. No strength or stress safety margin is claimed. Proof-load any prototype with a restrained dummy mass, not the console; a competent fabricator should define the load/duration and inspect deformation and joints before service use.

## Dimensions and interfaces still requiring hardware checks

| Item | Basis | Remaining check |
|---|---|---|
| 358 × 96 × 216 mm and 3.2 kg console | Sony CFI-2002 Disc specification | Confirm user's actual CFI model; other revisions may differ |
| Bottom outline and black-core footprint | Supplied fan-made GLB / inherited JSON | Gauge fit and direct measurements; no scan accuracy asserted |
| 1.5 mm nominal clearance / 30 mm lift | Design choices | Process tolerance, shrinkage, finish and pad allowance |
| Approximately 29.3 mm front/rear center rim | Generated geometry | Shoulder/cable and disc insertion clearances, including plug strain relief |
| Seat load on black core | Geometric overlap of reference sections | Real contact marking; white covers must not carry the load |
| Anti-slip behavior and retention | Not measured, no retention screw | Flatness, rocking, slide and restrained tipping tests |
| Bottom vents and thermal behavior | Not established for user's unit | Identify all vents; no rib/pad may cover them; compare controlled operation |

The reference mesh is not a closed engineering solid. It is therefore not used as a certified collision/strength model. The assembly rendering removes its separate ring stand and applies a 30 mm lift to the console geometry; it is only a visual check.

## Ventilation evidence and limits

Sony's [CFI-2002 safety guide, pp. 6, 12–13](https://www.playstation.com/content/dam/global_pdc/en-au/corporate/support/manuals/ps5-docs/2000/CFI-2002_PS5_Disc_Safety_Guide_Web%24en-au.pdf) requires unobstructed vents, at least 10 cm from a wall, and an appropriate vertical stand. Its external dimensions and mass do not describe the underside contact or vent geometry. This prototype is not Sony's specified stand.

Sony's [PS5 ventilation support page](https://www.playstation.com/en-us/support/hardware/ps5-console-noise/) identifies sides and rear as areas that must remain unobstructed. [iFixit's Slim fan replacement guide](https://www.ifixit.com/Guide/PlayStation+5+Slim+Fan+Replacement/167652) documents the Slim fan beneath the side cover. Neither source establishes the direction or exact active area of every opening at the bottom of this user's console.

**The bottom-intake-versus-exhaust question remains unresolved for the precise region in the sketch.** Original PS5 and PS5 Pro teardowns must not be silently substituted for a Slim underside map. The design therefore has no fan, duct or claim of beneficial air direction. Removing v5's full liner and leaving openings reduces solid enclosure geometrically, but it does not prove improved airflow, lower temperature or absence of exhaust recirculation. A 30 mm lift does not replace Sony's surrounding-clearance guidance. Before powered use, verify the vent layout and perform a controlled comparison with a known-good stand under equivalent ambient/load conditions; surface temperature alone cannot establish internal thermal safety.
