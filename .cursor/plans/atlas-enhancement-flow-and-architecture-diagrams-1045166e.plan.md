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

## Integration with Existing Workflows

### Hermetic Behavior (Rule 046)
- All database queries must be optional (emit HINTs if DB unavailable, never fail)
- File operations verify existence first (`os.path.exists`, `test -f`) before reading/writing
- Missing critical files emit LOUD FAIL (no auto-creation, fail-closed)
- Empty database returns `[]` gracefully, never errors

### Post-Change Workflows (Rule 058, 050)
- After generating diagrams, MUST run `make housekeeping` before committing
- Housekeeping includes: share.sync, governance tracking, rules audit, forest regen
- Follow post-change checklist from Rule 050:
  1. Run housekeeping: `make housekeeping`
  2. Check hints: Verify hints emitted if rule/docs changed (Rule 026)
  3. Verify share sync: Check `share/` updated (Rule 030)
  4. Check related rules: Review "Related Rules" sections for updates needed
  5. Commit generated files: Share sync, evidence, forest updates, etc.

### Governance Tracking
- Generated evidence files (`docs/evidence/*.md`, `docs/evidence/*.html`) should be tracked in `governance_artifacts` table with `artifact_type='evidence'`
- Atlas diagrams (`docs/atlas/*.mmd`) are generated artifacts (not in share manifest, but tracked in governance_artifacts with `artifact_type='atlas'`)
- Use `scripts/governance_tracker.py` or direct `update_governance_artifact()` function to track new artifacts
- **Note**: Generated files (evidence/atlas) are NOT in share manifest (they're artifacts, not source files)
- **Note**: Changes to generator scripts (`scripts/atlas/*.py`) will trigger hints if they modify rules/docs (via `governance_docs_hints.py`)
- **Out of scope**: Share manifest guards/status scripts (separate backlog task per GPT validation)

### Database Integration (Rule 064)
- Use `GEMATRIA_DSN` for all queries (same DB as AI tracking)
- Force read-only session: `SET default_transaction_read_only=on`
- All queries must handle empty database gracefully
- Emit HINTs when database unavailable (hermetic behavior)

## Implementation Specification

### File Structure

**New Files:**
- `docs/atlas/index.html` - Browser hub with vendored Mermaid, navigation sidebar, click handlers
- `docs/vendor/mermaid.min.js` - Vendored Mermaid (stub initially, replace with real dist)
- `scripts/atlas/telemetry_queries.py` - Read-only DB query layer (empty-DB tolerant)
- `scripts/atlas/generate_atlas.py` - Diagram and summary generator
- `docs/evidence/*.md` - Human-readable summaries (one per diagram)
- `docs/evidence/*.html` - HTML versions of summaries

**Modified Files:**
- `Makefile` - Add atlas.* targets
- `README.md` - Add Atlas dashboard links under badges
- `CHANGELOG.md` - Add Atlas track entry

### Implementation Steps

1. **Create Atlas browser hub** (`docs/atlas/index.html`)
   - Single entry page with sticky header
   - Navigation sidebar with links to all diagram views
   - Main content area renders Mermaid diagrams
   - Click handlers load `.mmd` files dynamically
   - Vendored Mermaid (no CDN dependency)
   - Glossary strip: PR/Tag/Badge/Verdict definitions

2. **Create vendor stub** (`docs/vendor/mermaid.min.js`)
   - Stub implementation (developers replace with real dist)
   - Prevents CDN dependency

3. **Create query layer** (`scripts/atlas/telemetry_queries.py`)
   - Read-only PostgreSQL connection with `SET default_transaction_read_only=on`
   - Empty-DB tolerant: returns `[]` if DSN missing or connection fails
   - Emits HINTs on failure (never errors)
   - Query functions:
     - `q_active_runs()` - Currently executing pipelines
     - `q_errors()` - Recent errors from `v_recent_errors_7d`
     - `q_latency_p90()` - Top slowest nodes from `v_node_latency_7d`
     - `q_throughput()` - Throughput metrics from `v_node_throughput_24h`
     - `q_ai_interactions()` - AI tool usage
     - `q_governance_artifacts()` - Governance tracking
   - Environment knobs: `ATLAS_WINDOW`, `ATLAS_MAX_ROWS`

4. **Create generator** (`scripts/atlas/generate_atlas.py`)
   - Generates all 7 diagram types (execution_live, pipeline_flow_historical, dependencies, call_graph, class_diagram, knowledge_graph, kpis)
   - Generates human summaries (`.md` and `.html`) for each diagram
   - PR lane: Grey scaffolds when no DSN
   - Tag lane: Populated from DB when DSN present
   - Relative links only
   - Timing output for performance monitoring

5. **Update Makefile**
   - `atlas.generate` - Build all diagrams + summaries
   - `atlas.live`, `atlas.historical`, `atlas.dependencies`, `atlas.calls`, `atlas.classes`, `atlas.knowledge`, `atlas.kpis` - Individual diagram targets
   - `atlas.dashboard` - Ensure hub + vendor present
   - `atlas.all` - Alias to `atlas.generate`
   - `atlas.test` - Time generation (warn if >5s)
   - `atlas.serve` - Local HTTP server on port 8888
   - `atlas.watch` - Optional file watcher (local-only)

6. **Update README.md**
   - Add Atlas dashboard links under badges section
   - Links to: Now, Historical, Dashboard

7. **Update CHANGELOG.md**
   - Add "ops: Atlas — browser-first, PR-safe" entry
   - Document new files, query layer, generators, Make targets

8. **Run housekeeping** (Rule 058)
   - Execute `make housekeeping` after all changes
   - Ensures share sync, governance tracking, rules audit

9. **Verify locally**
   - Run `make atlas.dashboard`
   - Run `python3 scripts/atlas/generate_atlas.py`
   - Verify files generated: `.mmd` diagrams, `.md`/`.html` summaries
   - Check HINT output in stderr

10. **Commit and PR**
    - Stage all new/modified files
    - Commit with message: `docs(ops): Atlas — browser-first, PR-safe (hub+queries+generators+targets)`
    - Create PR with descriptive body

### Execution Workflow

**Baseline (Rule 050):**
```bash
cd /home/mccoy/Projects/Gemantria.v2
source activate_venv.sh
ruff format --check . && ruff check .
```

**Implementation:**
1. Create `docs/atlas/index.html` with full HTML structure
2. Create `docs/vendor/mermaid.min.js` stub
3. Create `scripts/atlas/telemetry_queries.py` with query functions
4. Create `scripts/atlas/generate_atlas.py` with all generators
5. Update `Makefile` with atlas.* targets
6. Update `README.md` with Atlas links
7. Update `CHANGELOG.md` with Atlas entry
8. Run `make housekeeping`
9. Test: `make atlas.dashboard && python3 scripts/atlas/generate_atlas.py`
10. Commit and create PR

**Tag Lane (Post-Merge):**
```bash
# Before cutting -rc tag (operator runbook)
GEMATRIA_DSN=postgresql://... make -s atlas.generate
git add docs/atlas/*.mmd docs/evidence/*.{md,html}
git commit -m "docs: refresh Atlas before tag"
```

### Evidence Requirements

**Expected Outputs:**
- Ruff: `… already formatted` and `All checks passed!`
- Generated files listing:
  - `ATLAS: execution_live.mmd`
  - `ATLAS: pipeline_flow_historical.mmd`
  - `ATLAS: kpis.mmd`
  - `ATLAS: dependencies.mmd`
  - `ATLAS: call_graph.mmd`
  - `ATLAS: class_diagram.mmd`
  - `ATLAS: knowledge_graph.mmd`
  - `ATLAS: index.html`
- Stderr HINTs:
  - `HINT: atlas: wrote docs/atlas/execution_live.mmd`
  - `HINT: atlas: generation completed in <N>ms`

### Next Gates

**PR Lane Proof:**
- Land PR with grey scaffolds (no DSN)
- Verify links open `docs/evidence/*.html` summaries locally (`make atlas.serve`)
- Confirm CI green

**Tag Lane Proof:**
- With `GEMATRIA_DSN` set, run `make -s atlas.generate`
- Commit refreshed `.mmd` + summaries
- Cut `-rc` tag
- Confirm DB queries populated KPIs and live view in **<5s**

**Follow-ups (Fast):**
- Replace stub `docs/vendor/mermaid.min.js` with real vendored file
- Add DEEP scan toggles
- Wire optional governance artifact inserts if DSN present (tolerant on failure)

## Acceptance Criteria

- PRs: diagrams render as grey scaffolds without DSN; CI green
- Tags: diagrams populated from DB in <5s total; committed with evidence
- All clickable nodes open orchestrator summaries (HTML) with plain language + excerpt
- Links are relative and work on GitHub, local browser, and `make atlas.serve`
- KPIs visible/correct for selected window
- No network usage (vendored Mermaid)
- Hermetic: Works without database (emits HINTs, never fails)
- Housekeeping: `make housekeeping` runs after diagram generation
- Governance: Evidence files tracked in `governance_artifacts` table