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

### ID-type audit (local-only)
Task kind `id_type_audit` enforces ID type policy for nodes. Thresholds under `id_audit.*`.
See `exports_id_type_audit_latest`.

### ID stability (local-only)
Run:
```bash
make eval.idstability
```

Artifacts:

* `share/eval/id_stability.json` — Jaccard similarity and add/remove counts
* `share/eval/id_stability.md` — summary with badge
  Thresholds in `eval/thresholds.yml` under `id_stability.*`.

### Exports catalog (local-only)
Run:
```bash
make eval.catalog
```

Artifact:

* `share/eval/exports_catalog.md` — size + node/edge counts for every `exports/graph_*.json`.

### One-shot reproducer (local-only)

Run:

```bash
bash scripts/eval/repro_local.sh
```

Runs: report → history → delta → idstability → index → catalog (local-only).

### Referential integrity (local-only)
Task kind `ref_integrity` checks that edges reference existing node ids, and enforces limits on self-loops and duplicates.
Thresholds come from `eval/thresholds.yml` (integrity.*). See task `exports_ref_integrity_latest`.

## Notes

* Deterministic and fast; suited for PR evidence.
* Do **not** wire into CI until stabilized.
* Governance: 037/038 unchanged; share drift remains read-only in CI.

### Provenance (local-only)
Run:
```bash
make eval.provenance
```

Artifacts:

* `share/eval/provenance.json` — git SHA, manifest/thresholds versions, latest export info
* `share/eval/provenance.md` — human-readable summary

### Checksums (local-only)

Run:

```bash
make eval.checksums
```

Artifact:

* `share/eval/checksums.csv` — sha256 + size for each `exports/graph_*.json`

> After generating, re-run `make eval.index` to add badges for these artifacts.

### Anomalies (local-only)
Run:
```bash
make eval.anomalies
```

Artifact:

* `share/eval/anomalies.md` — consolidated red flags from report/history/delta/id_stability.

### Run log (local-only)

Run:

```bash
make eval.runlog
```

Artifact:

* `share/eval/run_log.jsonl` — append-only JSONL; each line captures provenance + results snapshot.

### Sanitized export (local-only)
Run:
```bash
make data.sanitize
make eval.report.sanitized
```

Artifacts:

* `exports/graph_sanitized.json` and time-stamped `exports/graph_sanitized_*.json`
* `share/eval/report_for_graph_sanitized.json` — manifest report applied to sanitized file

### Integrity diagnostics (local-only)

Run:

```bash
make diag.integrity
```

Artifact:

* `share/eval/integrity_diag.md` — count + examples of missing endpoints in the canonical latest export.

### Profiles (local-only)
Overlays in `eval/profiles/<name>.yml` merge onto `eval/thresholds.yml`.
Run:
```bash
make eval.profile.strict
make eval.profile.dev
```

### Whitelist (local-only)

Add problematic IDs (one per line) to `eval/id_whitelist.txt`. Integrity and ID-type audits will ignore those IDs when configured via manifest args.

### Repair plan (local-only)

```bash
make eval.repairplan
```

Artifacts:

* `share/eval/repair_plan.json` — proposed stub nodes to fix missing endpoints
* `share/eval/repair_plan.md` — human-readable summary
