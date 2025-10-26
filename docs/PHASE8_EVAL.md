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

### Repaired export (local-only)
Run:
```bash
make eval.repairplan
make repair.apply
make eval.report.repaired
```

Artifacts:

* `exports/graph_repaired.json` and time-stamped `exports/graph_repaired_*.json`
* `share/eval/report_for_graph_repaired.json` — manifest report applied to repaired file

### Policy delta (local-only)

Run:

```bash
make eval.policydiff
```

Artifact:

* `share/eval/policy_diff.md` — pass/fail summary for strict vs dev

### Config snapshots (local-only)

Create frozen copies of configuration used for evaluation:

```bash
make eval.snapshot
```

Artifacts:

* `share/eval/snapshot/manifest.snapshot.yml` — exact manifest used
* `share/eval/snapshot/thresholds.snapshot.yml` — resolved thresholds
* `share/eval/snapshot/provenance.snapshot.json` — git SHA, timestamp, tool versions

### HTML dashboard (local-only)

Generate browsable HTML dashboard with artifact links and pass/fail badges:

```bash
make eval.html
```

Artifact:

* `share/eval/index.html` — lightweight dashboard linking to all artifacts with status badges

### Bundle for handoff (local-only)

Create distributable tar.gz bundle with all evaluation artifacts:

```bash
make eval.bundle
```

Artifact:

* `share/eval/bundles/eval_bundle_<ts>.tar.gz` — includes:
  * `share/eval/*` (all artifacts)
  * `exports/graph_{latest,sanitized,repaired}.json` (if present)
  * `eval/manifest.yml`, `eval/thresholds.yml`
  * `share/eval/snapshot/*` (snapshot files)

### Strict preflight gate (local-only)

Quality gate that enforces zero failures under strict profile:

```bash
make eval.gate.strict
```

Returns:
* `0` (success) — no failures detected
* `1` (failure) — failures detected in strict profile
* Override with `ALLOW_FAIL=1` environment variable

### Remediation workflow (local-only)

Automated analysis and fixing of evaluation failures:

```bash
# Step 1: Run evaluation to identify issues
make eval.report

# Step 2: Generate remediation plan with specific fix suggestions
make eval.remediation

# Step 3: Apply automated fixes (optional, skips if SKIP_AUTO_FIXES=1)
make eval.apply.remediation
```

#### Remediation plan generation

Run:
```bash
make eval.remediation
```

Artifacts:
* `share/eval/remediation_plan.json` — structured remediation data
* `share/eval/remediation_plan.md` — human-readable plan with suggested actions

The plan analyzes failed evaluation tasks and provides:
- **Issue categorization** (data_integrity, data_quality, data_distribution, etc.)
- **Severity levels** (high, medium, low)
- **Specific fix suggestions** for each failure type
- **Automated fix availability** indicators
- **Effort estimates** for manual interventions

#### Automated fix application

Run:
```bash
make eval.apply.remediation
```

Features:
* **Safe execution** — only applies fixes marked as automated
* **Timeout protection** — 5-minute timeout per fix
* **Validation** — re-runs evaluation after fixes to measure improvement
* **Detailed logging** — tracks all attempted fixes and outcomes
* **Preview mode** — set `SKIP_AUTO_FIXES=1` to analyze without applying

Artifact:
* `share/eval/remediation_applied.json` — execution log with success/failure details

**Current automated fixes:**
- Pipeline regeneration (`make go`) for missing files
- Future: Additional automated fixes as they're identified and validated

### Badges (local-only)
Run:
```bash
make eval.badges
```

Artifacts:

* `share/eval/badges/report_status.svg`
* `share/eval/badges/strict_gate.svg`

### Release notes (local-only)

Run:

```bash
make eval.release_notes
```

Artifact:

* `share/eval/release_notes.md` — curated summary from report/history/delta/id-stability/provenance/policy_diff.

### Package (local-only)

Run:

```bash
make eval.package
```

Runs: snapshot → html → bundle → badges → release_notes → bundle.all → release_manifest → verify.integrity, then prints `[eval.package] OK`.

### Manifest viewer
Dashboard now renders `release_manifest.json` inline (summary + first 200 artifacts). Works offline.

### Download-all bundle
```bash
make eval.bundle.all
```
Outputs a deterministic tar.gz under `share/eval/bundles/`.

### Integrity verification
```bash
make eval.verify.integrity
```
Writes `share/eval/integrity_report.txt`, exits nonzero on mismatches.

### HTML badges embed
Badges now render inside `share/eval/index.html` when present (no external hosting required).

### Strict package (local-only)
Run:
```bash
make eval.package.strict           # fails if strict has FAILs
ALLOW_FAIL=1 make eval.package.strict  # continues despite strict failures
```

### Release manifest (local-only)

Run:

```bash
make eval.release_manifest
```

Artifact:

* `share/eval/release_manifest.json` — path, size, sha256 for all packaged artifacts.

### Convenience
```bash
make eval.open
```
Opens the offline dashboard.

### Governance
When `share/eval/release_manifest.json` is present, `make ops.verify` now runs integrity verification as part of the ops gate.

### Centrality & Edge Strength
- `make eval.graph.centrality` writes `share/eval/centrality.json` with degree/betweenness/eigenvector.
- `make eval.graph.rerank_blend` fills missing rerank and computes `edge_strength = 0.5*cos + 0.5*rerank` with classes {strong, weak, other}.
- `make eval.package` runs both and updates dashboard + manifest.

### Rerank provider & cache
- Configure (optional) LM Studio provider:
  - `export RERANK_PROVIDER=lmstudio`
  - `export LMSTUDIO_RERANK_URL=http://127.0.0.1:1234/v1/rerank`
  - `export LMSTUDIO_RERANK_MODEL=qwen2.5-rerank`
- Cache lives in `.cache/rerank/` to ensure reproducibility. Safe to delete; it will repopulate.

### Schema verification
```bash
make eval.schema.verify
```
Validates `graph_latest.json`, `centrality.json`, `release_manifest.json` via JSON Schema. Runs automatically inside `eval.package`.

### CSV & Delta
- `make eval.graph.tables` → `share/eval/nodes.csv`, `share/eval/edges.csv`
- `make eval.graph.delta`  → `share/eval/delta.json` and `share/eval/badges/edges_delta.svg`
- Dashboard shows an optional Delta summary. If badge loop is enabled, all `badges/*.svg` display automatically.

### Snapshot & Provenance
- `make eval.snapshot.rotate` writes `graph_prev.json` from the current `graph_latest.json`.
- `make eval.provenance` writes `provenance.json` (git describe, counts, hashes).
- `make eval.package` includes both; dashboard shows a Provenance pane.
- `make ops.verify` now fails if required artifacts (graph, centrality, manifest, provenance) are missing.

### Quality & Summary
- Configure thresholds (optional):
  - `Q_MAX_MISSING_RERANK_PCT` (default 0)
  - `Q_MIN_STRONG_OR_WEAK` (default 1)
  - `Q_REQUIRE_NONZERO_EIG` (default 1)
- Run:
```bash
make eval.quality.check
make eval.summary
```
- Outputs: `share/eval/quality_report.txt`, `share/eval/summary.md`, `share/eval/summary.json`
- `eval.package` runs both and shows the result on the dashboard.
