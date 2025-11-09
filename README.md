# Gemantria

<div align="left">
  <img alt="xref coverage" src="share/eval/badges/xrefs_coverage.svg" />
  <img alt="xref rate" src="share/eval/badges/xrefs_rate.svg" />
  <img alt="Exports JSON" src="share/eval/badges/exports_json.svg" />

#### Operator Status

| Check | Status | Evidence |
|---|---|---|
| Exports JSON | <img alt="Exports JSON" src="share/eval/badges/exports_json.svg" /> | [verdict JSON](evidence/exports_guard.verdict.json) · [rendered MD](evidence/exports_guard.verdict.md) |
| PR Checks (guard-tests) | **Advisory** (branch protection off) | [.github/workflows/guard-tests.yml](.github/workflows/guard-tests.yml) |

### Project Status (evidence-driven)

> **PR** = proposal to merge change · **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker

> Open the visual map: [`docs/atlas/status.mmd`](docs/atlas/status.mmd) (Mermaid) · [HTML preview](docs/atlas/status.html) · [Text view](docs/atlas/status.txt)

</div>

This repository contains the planning scaffolding, lightweight gematria helpers, and hello-graph flow that anchor the larger rebuild effort.

> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.

## Local development
1. Create and activate a virtual environment (for example `.venv`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the lints and tests:
   - `make lint`
   - `make type`
   - `make test.unit`
   - `make coverage.report`

## Quick Start (5 minutes, hermetic)

Use the reuse-first CLI wrapper (no new logic):

```
python3 scripts/cli/gemantria_cli.py quickstart
# or simply:
make cli.quickstart
```

Key knobs (already in your env): `EDGE_STRONG`, `EDGE_WEAK`, `CANDIDATE_POLICY`, `PIPELINE_SEED`.

## Integrated Pipeline

The system now features a fully integrated pipeline that coordinates all components from data extraction through analysis and visualization.

### Complete Workflow
```bash
# Run the full integrated pipeline
make orchestrator.full BOOK=Genesis

# Or run components individually:
make orchestrator.pipeline BOOK=Genesis    # Main pipeline
make orchestrator.analysis OPERATION=all   # Analysis suite
make schema.validate                      # Schema validation
```

### Pipeline Components
1. **Noun Extraction** - Extract Hebrew nouns from Bible database
2. **AI Enrichment** - Generate theological insights using Qwen models
3. **Network Building** - Create semantic embeddings and relationships
4. **Schema Validation** - Ensure data integrity with JSON schemas
5. **Graph Analysis** - Community detection and centrality measures
6. **Data Export** - Generate visualization-ready JSON and statistics

### Book Processing
```bash
# Process entire books with orchestration
make book.plan                             # Plan processing
make book.dry                             # Dry run (validate services)
make book.go                              # Execute full processing
make book.stop N=5                        # Stop-loss after N chapters
make book.resume                          # Resume interrupted processing
```

## Project structure
- `docs/`: ADRs and the SSOT master plan that describe the rebuild objectives.
- `schemas/`: JSON schema placeholders for contract validation.
- `src/`: Minimal core, graph, and infrastructure modules that drive the hello-graph runner.
- `tests/`: Focused unit tests with a mini coverage plug-in enforcing the 98% threshold.

## Quality & Trends

Local smoke artifacts (run via the eval tools) can render quality trends:

![Quality Trend](share/eval/badges/quality_trend.svg)
![Current Quality](share/eval/badges/quality.svg)

### XRef Coverage & Rate (HINT-only)

The operator dashboard includes lightweight badges derived from the published xref index:

![XRef Coverage](share/eval/badges/xrefs_coverage.svg)
![XRef Rate](share/eval/badges/xrefs_rate.svg)

> Generated from `ui/public/xrefs/xrefs_index.v1.json` during `make eval.package`. In main/PR contexts these run in **HINT-only** mode; they do not affect the SSOT/guards.

> **CI behavior:** On PRs, the xref badge guard is path-aware and skips unless `ui/**` or the guard/badge scripts change. On tags, it runs in STRICT mode (release `v*` requires the index).

> In CI these are uploaded as artifacts; `share/**` remains read-only during CI.

## Required Checks

Main branch requires these checks to pass before merging:

![Ruff Format & Lint](https://img.shields.io/github/actions/workflow/status/mccoy/Gemantria.v2/enforce-ruff.yml?label=ruff&branch=main)
![CI Build](https://img.shields.io/github/actions/workflow/status/mccoy/Gemantria.v2/ci.yml?label=ci&branch=main)

> Branch protection requires: `ruff` (formatting + linting) and `build` (CI pipeline)

## Pushing changes
A remote is not configured by default. Add the desired remote (for example, `git remote add origin <url>`) and push normally once credentials are available.

## Developer Validation (Phase-9)

Local-only helpers (CI no-ops):

```bash
make ingest.local.validate
make ingest.local.validate.schema
```

See `docs/phase9/VALIDATION_README.md` for env knobs (SNAPSHOT_FILE, P9_SEED).

- Snapshot prep guide: see `docs/phase9/SNAPSHOTS.md`.

- Ingestion envelope fields (plan): see `docs/phase9/ENVELOPE_FIELDS.md`.

- Phase-10 dashboard plan: see `docs/phase10/DASHBOARD_PLAN.md`.

- UI Integration Spec: see `docs/phase10/UI_SPEC.md`.

## 🔗 Correlation UI (Phase-10)

**Purpose**
Displays cross-text pattern analytics and edge strength distributions for graph validation (see `MASTER_PLAN.md`, Phase-10).

**Usage**
```bash
export BOOK=Genesis
make orchestrator.full BOOK="$BOOK"
make analyze.export
make ui.mirror.correlation
make ui.smoke.correlation
make ui.build
```

**Governance References**

- AGENTS.md §4.1 (UI Agents: Cursor/Frontend)
- RULES_INDEX.md Rule-050 (OPS Contract), Rule-051 (Response Format), Rule-052 (Tool Priority)
- MASTER_PLAN.md Phase-10 Correlation → Phase-11 Unified Envelope transition

**Notes**

- Shows edge class counts (strong/weak/very-weak) with configurable thresholds
- Displays SSOT blend badge: `edge_strength = EDGE_ALPHA*cosine + (1-EDGE_ALPHA)*rerank_score`
- Correlation UI available at `/correlation`.
