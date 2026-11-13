# v13 comparison baseline

Only v15 is kept in the working tree. These few v13 files are what v15's review scripts still compare against. The complete v13 folder is available at Git tag `v13`.

| File | Used by |
|---|---|
| `veil_v13_prototype.stl` | `source/render_turntable.py` |
| `GAUGE_v13_cavity_1.6mm.stl` | `source/review_geometry.py` (the v15 gauge must have the same extents) |
| `source/veil_v13.py`, `source/outline.json` | `source/review_wall.py` (v13 wall guides) |
