# v13 geometry method

v13 is one sculpted shell with openings cut through it. The remaining material forms the visible web; there are no separate exterior pipes, collars or stacked ring rows. The editable generator is [veil_v13.py](source/veil_v13.py).

## Shell and silhouette

The upper outline and lower outline are finite Fourier series with high-frequency coefficients tapered before truncation. The upper radius uses up to 36 harmonics, the lower radius up to 28. The final rim height is the analytic low-amplitude law `39.5 + 1.2 sin(theta + 0.4) + 0.35 cos(2 theta - 0.2)` mm. These guides are periodic and C∞, so their position and derivatives join continuously at the seam. A uniform upper-radius expansion preserves reference clearance without introducing local correction corners.

The upper guide ranges from 38.030 to 40.700 mm, compared with 33.954–48.042 mm in v12. The bottom guide remains at z=0. Its plan displacement from v12 is at most 1.619 mm; maximum sampled curvature falls from 0.20685 to 0.04940 mm⁻¹. Upper-plan displacement is at most 1.098 mm. Sampled seam errors in position and first/second derivatives are below 5×10⁻¹³ in their respective units. These numerical checks supplement the analytic periodic construction, rather than establishing a tolerance for printing. See [guide evidence](analysis/guide_continuity.json).

The radial shell transitions quadratically between base and rim. Nominal shell depth is 2.8 mm, with radial offset adjusted for surface slope: an approximation to normal thickness, not an exact everywhere-minimum. Integrated top/bottom section edges have approximately 0.6 mm quarter-round transitions. Finite Fourier guide continuity does **not** establish global G1/G2 continuity of the complete triangulated, beveled and Boolean-cut shell.

## Irregular openings with a shared flow

1. Build a periodic circumference/height chart, using approximate perimeter arc length to avoid crowding openings simply because the console outline is noncircular.
2. Select 72 reproducible, irregularly spaced seeds by weighted farthest-point sampling of 7,000 candidates (random seed 1204). This is a blue-noise-style placement heuristic, not a claim of an optimized blue-noise spectrum.
3. Replicate seeds around the circumference and reflect them at the chart's upper/lower boundaries, then form ordinary Voronoi cells. The weighting affects seed placement; this is **not** a weighted/power Voronoi diagram. [SciPy's Voronoi implementation constructs the regions using Qhull](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html).
4. Apply the **same smooth periodic flow warp** to every cell, then erode each warped cell by 2.35 chart millimeters. This leaves connecting material between openings without arranging them in horizontal rows.
5. Round the opening corners by an erosion/dilation operation, starting at a 3 mm chart radius and reducing it for cells too small to retain a valid interior. The final 72 openings use chart radii from 2.2 to 3.0 mm; these are not guaranteed 3 mm radii everywhere on the mapped 3D shell.
6. Map the rounded openings onto the shell and cut through it. Several cutter-depth profiles introduce a small aperture-edge bevel, up to 0.35 chart millimeters of outward opening growth at the faces.

These steps create related flowing cells while retaining irregular sizes and positions. Polygon sampling, mapped bevels and triangulation remain visible geometric approximations. A sampled opening-gap check, if included, measures the checked polygonal boundaries and is not a complete finished-part minimum-thickness certification.

## Internal supports and review scope

Bowed longitudinal paths and transverse branches form a lower internal web with broad arch openings and narrowed top contact edges. The supports are clipped to the inner shell envelope and joined to it. Their intended load path still requires actual black-core contact checks. Fresh v13 structural analysis is documented in [STRUCTURAL_ANALYSIS.md](STRUCTURAL_ANALYSIS.md). It identifies unresolved internal-junction stress concentrations; these guide/mesh checks do not establish load capacity.

The final STL/3MF and rendered views use the same geometry. Overview normal interpolation is limited near creases; the flat side-profile view exposes actual facet/edge behavior. Geometry readback checks body integrity and the reference envelope. Guide and mesh checks are separate from the fresh structural and airflow analyses. No production slicing or physical fit/load/thermal qualification is claimed.

## Final lightweight geometry evidence

The delivered body is 150.339 × 241.277 × 40.700 mm, 74.605282 cm³ and 170,792 triangles. STL/3MF agree, and the body, gauge and local coupon are each connected and watertight with consistent winding. The inherited cavity is unchanged, the seat is 30 mm, and final console-plan/cavity-envelope intersections are both 0 mm³. These are reference-model checks, not hardware measurements.

The final maximum-bevel aperture-boundary screen reports a minimum mapped segment gap of 3.04264 mm. It checks polygonal boundaries mapped to the two shell faces, not every finished-Boolean wall or printer toolpath. The coupon is 58 × 36 × 40.700 mm, 6.93403 cm³, including about 3.94243 cm³ of actual internal support geometry. Evidence: `analysis/light_geometry_review.json` and `analysis/aperture_spacing_preflight.json`.
