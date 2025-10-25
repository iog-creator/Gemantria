# Phase-8 Eval (Local Manifest → Report)

Local-only evaluation flow. No CI gates or `make go` changes.

## Usage
1. Edit tasks in `eval/manifest.yml`
2. Run:
   ```bash
   make eval.report
```

3. Artifacts:

   * `share/eval/report.json`
   * `share/eval/report.md`

### Temporal history (local-only)
Run:
```bash
make eval.history
```

Artifacts:

* `share/eval/history.json` — per-export metrics + summary
* `share/eval/history.md` — human-readable trend table and OK badge

Notes:

* Files matched: `exports/graph_*.json`
* Sorting prefers timestamp in filename; minimal fallback
* Checks: nonzero nodes/edges, strength fraction in [0.30, 0.95] ≥ 0.70, embedding_dim==1024 when present

### Schema validation (local-only)
`eval.report` now supports a `json_schema` task kind using a repo-local schema:
- Schema path: `docs/SSOT/schemas/graph_export.schema.json`
- Local dependency: `pip install jsonschema`
- Run: `make eval.report` — the task key `exports_schema_validate_latest` must be ✅

### Per-run delta (local-only)
Run:
```bash
make eval.delta
```

Artifacts:

* `share/eval/delta.json` — added/removed nodes/edges + strength stats
* `share/eval/delta.md` — human-readable summary
  Policy (initial): **no removals** (nodes/edges) for an ✅ badge. Tolerances can be relaxed in a future PR.

### Thresholds (local-only)
Centralized in `eval/thresholds.yml`. The eval engine substitutes `${thresholds:...}` in `eval/manifest.yml` before running.
Examples:
- `${thresholds:strength.min}` / `${thresholds:strength.max}` / `${thresholds:strength.min_frac}`
- `${thresholds:embedding.dim_if_present}`
- `${thresholds:shape.nodes.min}` / `${thresholds:shape.edges.max}`

### Shape smoke
Task kind `json_shape` verifies node/edge counts within bounds. See task `exports_shape_smoke_latest`.

### Eval index
Run:
```bash
make eval.index
```

Artifact: `share/eval/index.md` — quick links/badges for `report.md`, `history.md`, `delta.md`.

### Referential integrity (local-only)
Task kind `ref_integrity` checks that edges reference existing node ids, and enforces limits on self-loops and duplicates.
Thresholds come from `eval/thresholds.yml` (integrity.*). See task `exports_ref_integrity_latest`.

## Notes

* Deterministic and fast; suited for PR evidence.
* Do **not** wire into CI until stabilized.
* Governance: 037/038 unchanged; share drift remains read-only in CI.
