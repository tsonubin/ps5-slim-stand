# v13 comparison baseline

The v13 design folder was removed from the branch when v14 became the only version kept. These files are what v14's review scripts and README still compare against. The complete v13 folder is available at Git tag `v13`.

| File | Used by |
|---|---|
| `veil_v13_prototype.stl` | `source/review_seat.py`, `source/render_turntable.py` |
| `GAUGE_v13_cavity_1.6mm.stl` | `source/review_geometry.py` (the v14 gauge must have the same extents) |
| `source/veil_v13.py`, `source/outline.json` | `source/review_wall.py` (v13 wall guides) |
| `airflow/*_port0.json`, `*_port60.json` | `airflow/summarize.py` (v13 flow reductions) |
| `airflow/AIRFLOW_REVIEW.md` | Method and limits of the lattice-Boltzmann screen |
| `STRUCTURAL_ANALYSIS.md` | Method of the in-house first-order stress screen |

The two reports describe v13's own results; only their method sections apply to v14.
