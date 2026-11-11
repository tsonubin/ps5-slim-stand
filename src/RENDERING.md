# Actual-mesh render pipeline

`render_mesh.py` and `raster_mesh.cpp` render the exported triangle mesh directly. The renderer does not alter vertex positions, stitch geometry, fill holes, or apply a subdivision modifier.

The C++ helper performs perspective-correct interpolation and depth testing with a CPU z-buffer. Python supplies mesh coordinates, normals and colors, then downsamples a 2× supersampled image. The helper is compiled with `clang++ -O3 -std=c++17` into the system temporary directory and is never stored in the repository.

The v11 overview uses vertex normals only where the averaged corner normal is within 20 degrees of its face normal; other corners keep their face normals. Junction comparisons use **flat face normals only**, with identical camera and lighting before/after. This separates geometry improvements from shading improvements.

From the repository root, after v11 geometry is generated:

```sh
.venv-cad/bin/python designs/v11/source/render_clean.py
```

Dependencies: NumPy, trimesh, Pillow and a C++17 compiler named `clang++`. The script requires the preserved v10 mesh for comparison and uses the supplied console reference mesh for visual assembly. The resulting pictures do not establish physical fit, printability or strength.

The rasterizer was checked with two triangles sharing a diagonal (no background cracks) and overlapping near/far squares (near-face occlusion). These rendering checks are separate from CAD validation.
