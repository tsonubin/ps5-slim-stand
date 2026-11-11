# Design versions and Git checkpoints

Each design milestone has an annotated Git tag, published to `origin`. Tags mark reviewable design snapshots, not engineering approval or print qualification. Existing history has not been rewritten.

| Tag | Commit | Authoritative design folder | Checkpoint provenance |
|---|---|---|---|
| `v5` | `7070cee` | `designs/imported/ps5_veil_stand_v5/` | Imported original archived in the initial repository snapshot; not an original v5-era Git commit |
| `v6` | `7070cee` | `designs/v6/` | Initial repository baseline, including preserved imports |
| `v7` | `7947185` | `designs/v7/` | Retrospective marker for the preserved v7 study within the combined v7–v10 snapshot |
| `v8` | `7947185` | `designs/v8/` | Retrospective marker for the preserved v8 study within the combined v7–v10 snapshot |
| `v9` | `7947185` | `designs/v9/` | Retrospective marker for the preserved v9 study within the combined v7–v10 snapshot |
| `v10` | `7947185` | `designs/v10/` | Combined design-history commit ending at v10 |
| `v11` | `557163f` | `designs/v11/` | Dedicated v11 design commit |
| `v12` | `ede01eb` | `designs/v12/` | Dedicated v12 design commit |
| `v13` | `f5dd66f` | `designs/v13/` | Dedicated v13 design, stress and conditional airflow investigation commit |

The earlier work was committed in batches. In particular, `v7`, `v8`, and `v9` cannot honestly be presented as separate historical whole-repository checkpoints: those tags point to the first commit containing their preserved folders, which also contains later studies. Inspect the authoritative folder listed above. Tag annotations record this limitation.

## Review a version

```sh
git fetch origin --tags
git show v13
git diff v12 v13 -- designs/ README.md docs/CONTINUE.md
# Optional isolated checkout for review:
git worktree add --detach ../ps5-slim-stand-v13 v13
```

Large reproducible solver arrays, local review ZIPs and some volumetric results are intentionally excluded from Git. Each version's documentation specifies tracked deliverables, locally generated outputs and reproduction commands. A tag alone does not archive ignored files.

## Future milestones

For each new numbered design: preserve the prior design, commit the new model and its corresponding evidence as a separate checkpoint, create an annotated version tag, and push both branch and tag. Published tags are immutable; corrections receive a new tag rather than silently moving an existing one. The draft PR remains the review channel; tags provide stable version references independently of PR status.
