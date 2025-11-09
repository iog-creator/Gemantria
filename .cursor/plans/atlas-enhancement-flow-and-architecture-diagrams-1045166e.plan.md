<!-- 1045166e-a28a-40b0-8555-f0a31ee538ca f6ea9fd4-18d6-4cce-88f1-c46fb1efcab4 -->
# Telemetry-Driven Atlas (Browser-First, PR-Safe)

## Goal
Ship a visual Atlas dashboard powered by existing telemetry and evidence, rendered in the browser (no IDE dependency), with human-readable summaries behind every click. PR runs are file-only (grey scaffolds); tags pull real DB telemetry via `GEMATRIA_DSN`.

## Scope

### 1. Browser Hub
- Add `docs/atlas/index.html` (single entry page)
- Vendor `docs/vendor/mermaid.min.js` (no CDN)
- Render these Mermaid files:
  - `docs/atlas/execution_live.mmd` (Now)
  - `docs/atlas/pipeline_flow_historical.mmd` (Historical)
  - `docs/atlas/dependencies.mmd`
  - `docs/atlas/call_graph.mmd`
  - `docs/atlas/class_diagram.mmd`
  - `docs/atlas/knowledge_graph.mmd`
  - `docs/atlas/kpis.mmd` (Active runs, Errors(24h), Top 5 slowest p90)

### 2. DB Query Layer (Read-Only)
**File:** `scripts/atlas/telemetry_queries.py` (new)

- Use existing sources: `metrics_log`, `checkpointer_state`, `v_metrics_flat`, `v_pipeline_runs`, `v_node_latency_7d`, `v_node_throughput_24h`, `v_recent_errors_7d`, `ai_interactions`, `governance_artifacts`
- Force read-only session (`SET default_transaction_read_only=on`)
- Empty-DB tolerant: return `[]`, never error

### 3. Generators
**File:** `scripts/atlas/generate_atlas.py` (new)

- Queries → write `.mmd` diagrams (listed above)
- Generate human summaries for every clickable node:
  - Markdown: `docs/evidence/*.md`
  - HTML: `docs/evidence/*.html`
- Summaries explain "what this shows," status, tiny excerpt, link to raw JSON if relevant
- Relative links only; diagram clicks go to `docs/evidence/*.html`
- TAG hub also links to `CHANGELOG.md`

### 4. PR vs Tag Lanes
- **PR lane:** run generators without DSN; render grey scaffolds (no secrets)
- **Tag lane:** before tagging, run generators with `GEMATRIA_DSN` and commit updated `.mmd` + summaries with other evidence

## Makefile Targets

Add:
- `atlas.generate` (build all diagrams + summaries; honors env knobs)
- `atlas.live`, `atlas.historical`, `atlas.dependencies`, `atlas.calls`, `atlas.classes`, `atlas.knowledge`
- `atlas.dashboard` (ensures `index.html` + vendor present)
- `atlas.all` (alias to `atlas.generate`)
- `atlas.test` (times generation; warn if >5s)
- `atlas.serve` (`python3 -m http.server --directory docs 8888`)
- *(Optional local)* `atlas.watch` (file watcher to re-gen "Now"; not used in CI)

## Env Knobs (Performance & Scope)

- `ATLAS_WINDOW=24h|7d` (default: 24h for "Now", 7d historical)
- `ATLAS_MAX_ROWS=500` (hard LIMIT for all queries)
- `ATLAS_ENABLE_DEEP_SCAN=0|1` (default 0; keeps deps/class/knowledge views light)
- `ATLAS_HIDE_MISSING=0|1` (default 0; hides nodes if evidence missing when 1)

## Operator Dashboard Integration

In `README.md` (below badges), add Atlas links:
- **Now:** `docs/atlas/execution_live.mmd`
- **Historical:** `docs/atlas/pipeline_flow_historical.mmd`
- **Dashboard:** `docs/atlas/index.html`

Keep a tiny glossary strip on pages:
- **PR** = proposal to merge change (fast checks)
- **Tag** = frozen proof snapshot
- **Badge** = visual pass/fail
- **Verdict** = JSON pass/fail

## Release Hook (STRICT/Tag Lane)

Before cutting an `-rc` tag:
```bash
make -s atlas.generate
git add docs/atlas/*.mmd docs/evidence/*.{md,html}
git commit -m "docs: refresh Atlas before tag"
```

## Acceptance Criteria

- PRs: diagrams render as grey scaffolds without DSN; CI green
- Tags: diagrams populated from DB in <5s total; committed with evidence
- All clickable nodes open orchestrator summaries (HTML) with plain language + excerpt
- Links are relative and work on GitHub, local browser, and `make atlas.serve`
- KPIs visible/correct for selected window
- No network usage (vendored Mermaid)