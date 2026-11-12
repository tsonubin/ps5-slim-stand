# v12 geometry method

v12 is one sculpted shell with openings cut through it. The remaining material forms the visible web; there are no separate exterior pipes, collars or stacked ring rows. The editable generator is [veil_v12.py](source/veil_v12.py).

## Shell and silhouette

Periodic cubic guides define the upper outline, base outline and rim height. The radial surface transitions quadratically between base and rim as height increases. Local smoothed clearance corrections preserve the inherited console cavity, and the final body is cut by that cavity above the 30 mm seat.

The shell uses a **nominal 2.8 mm depth**, with radial offset adjusted for local surface slope. This is a normal-thickness approximation, not a proof that every final wall is exactly 2.8 mm thick. The upper and lower edges are integrated into the shell section with approximately 0.6 mm quarter-round transitions rather than separate added rings. Cubic guides are C2 functions, but that property does not establish global G1/G2 continuity of the triangulated and Boolean-cut surface. [SciPy documents the cubic-spline continuity and periodic boundary conditions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html).

## Irregular openings with a shared flow

1. Build a periodic circumference/height chart, using approximate perimeter arc length to avoid crowding openings simply because the console outline is noncircular.
2. Select 72 reproducible, irregularly spaced seeds by weighted farthest-point sampling of 7,000 candidates (random seed 1204). This is a blue-noise-style placement heuristic, not a claim of an optimized blue-noise spectrum.
3. Replicate seeds around the circumference and reflect them at the chart's upper/lower boundaries, then form ordinary Voronoi cells. The weighting affects seed placement; this is **not** a weighted/power Voronoi diagram. [SciPy's Voronoi implementation constructs the regions using Qhull](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html).
4. Apply the **same smooth periodic flow warp** to every cell, then erode each warped cell by 2.35 chart millimeters. This leaves connecting material between openings without arranging them in horizontal rows.
5. Round the opening corners by an erosion/dilation operation, starting at a 3 mm chart radius and reducing it for cells too small to retain a valid interior. The final 72 openings use chart radii from 2.2 to 3.0 mm; these are not guaranteed 3 mm radii everywhere on the mapped 3D shell.
6. Map the rounded openings onto the shell and cut through it. Several cutter-depth profiles introduce a small aperture-edge bevel, up to 0.35 chart millimeters of outward opening growth at the faces.

These steps create related flowing cells while retaining irregular sizes and positions. Polygon sampling, mapped bevels and triangulation remain visible geometric approximations. A sampled opening-gap check, if included, measures the checked polygonal boundaries and is not a complete finished-part minimum-thickness certification.

## Internal supports and review scope

Bowed longitudinal paths and transverse branches form a lower internal web with broad arch openings and narrowed top contact edges. The supports are clipped to the inner shell envelope and joined to it. Their intended load path still requires actual black-core contact checks and fresh structural analysis.

The final STL/3MF and rendered views use the same geometry. Overview normal interpolation is limited near creases; the flat side-profile view exposes actual facet/edge behavior. Geometry readback checks body integrity and the reference envelope. **No v12 FEA, production slicing or physical fit/load/thermal qualification is claimed.** The current decision is aesthetic review of the actual candidate.

## Final lightweight geometry evidence

The delivered body is 150.395 × 240.625 × 48.042 mm, 76.708578 cm³ and 166,726 triangles. STL/3MF agree, and the body, gauge and local coupon are each connected and watertight with consistent winding. The inherited cavity is unchanged, the seat is 30 mm, and final console-plan/cavity-envelope intersections are both 0 mm³. These are reference-model checks, not hardware measurements.

The final maximum-bevel aperture-boundary screen reports a minimum mapped segment gap of 2.89360 mm. It checks polygonal boundaries mapped to the two shell faces, not every finished-Boolean wall or printer toolpath. The coupon is 58 × 36 × 45.500 mm, 7.23784 cm³, including about 3.99928 cm³ of actual internal support geometry. Evidence: `analysis/light_geometry_review.json` and `analysis/aperture_spacing_preflight.json`.
