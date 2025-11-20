# MASTER PLAN — Gemantria Pipeline Project

**Version**: Phase 8 Ledger & Phase 10: Multi-Temporal Analytics with Rolling Windows, Forecasting, and Interactive Exploration
**Last Updated**: 2025-11-13
**Current Release**: v0.0.8 (2025-11-12)
**Governance**: OPS Contract v6.2.3

---

### Governance Posture — Always-Apply Triad

We explicitly adopt the 050/051/052 triad:

1. **Rule-050 (LOUD FAIL)** — strict activation + SSOT checks.
2. **Rule-051 (CI gating posture)** — merges honor required checks.
3. **Rule-052 (tool-priority)** — local+gh → codex → gemini/mcp.

This plan assumes these rules are continuously enforced by guards and mirrored to the Atlas proof.

---

## Mission

Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts, with self-healing guards and governance.

### Core Priorities
1. **Correctness**: Code gematria > bible_db > LLM (LLM = metadata only)
2. **Determinism**: content_hash identity; uuidv7 surrogate; fixed seeds; position_index
3. **Safety**: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns (ALLOW_PARTIAL=1 is explicit)

---

## Phase Overview

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ **Complete** | Governance v6.2.3, internal guardrails active |
| 1 | ✅ **Complete** | Data Layer (DB foundation) |
| 2 | ✅ **Complete** | Pipeline Core (LangGraph) |
| 3 | ✅ **Complete** | Exports & Badges |
| 5 | ✅ **Complete** | UI Polish |
| 8 | ✅ **Complete** | Temporal Analytics Suite (rolling windows + forecasts + visualization) |
| 9 | ✅ **Complete** | Graph Latest with Node/Edge Exports |
| 10 | ✅ **Complete** | Correlation Visualization + Pattern Analytics |
| 11 | ✅ **Complete** | Unified Envelope (100k nodes, COMPASS validation) |

## Current Status: **Production Operations**

All core development phases are complete. The system is operational with:
- ✅ Unified envelope pipeline working
- ✅ COMPASS mathematical validation active
- ✅ Schema compliance verified
- ✅ UI integration functional
- ✅ Governance rules enforced
- ✅ **Reality Green Truth Gate** (`make reality.green`) - Canonical "all green" signal for live work

### Reality Green Truth Gate

**Purpose**: The `make reality.green` target is the **110% signal** that the system is up to date and consistent for the next agent. It validates:
- **DB Health (Option C)**: Database is reachable and healthy. DB-down is a hard failure when `GEMATRIA_DSN` is set (DB is SSOT).
- **Control-Plane Health**: Control-plane schema, tables, and materialized views are present and healthy.
- **AGENTS.md Sync**: All AGENTS.md files are in sync with code changes (no stale documentation).
- **Share Sync & Exports**: Share directory is synced and required control-plane exports exist.
- **WebUI Shell Sanity**: WebUI shell files are present (static check only).

**When to Run**: Before declaring features complete, opening PRs for main, generating share/ snapshots, or declaring system "live".

**Enforcement**: If `reality.green` is red, all docs (including AGENTS + SSOT) are treated as untrustworthy until fixed.

### Active Development Workstreams

**PLAN-072: Extraction Agents Correctness & Resume Docs Management** (📋 **Planned**)
- **M1** ⏳ PENDING: DMS guard fixes — ensure documentation management guards are hermetic and pass in CI.
- **M2+** ✅ PASS: Extraction agents provenance (TVs E06–E10) — implemented provenance logic (`ensure_provenance`, `guard_provenance`, `stamp_batch`) with full test coverage, guard integration, and AGENTS.md documentation. All 5 TVs (E06–E10) implemented, tested, guarded (PR #499). Artifacts: `agentpm/extractors/provenance.py`, `agentpm/tests/extractors/test_extraction_provenance_e06_e10.py`, `agentpm/extractors/AGENTS.md`, `scripts/ci/guard_extraction_agents.py`. Targets: `guard.extractors`.
- **M2** ⏳ PENDING: Extraction agents correctness — define TVs for extraction correctness (TV-E01..E05) with golden fixtures, add hermetic guard `guard_extraction_agents.py` (no DB/network), wire pytest collection under `agentpm/tests/extractors/` (unit-only). Artifacts: `agentpm/tests/extractors/test_extraction_correctness.py`, `agentpm/tests/extractors/fixtures/*.json`, `scripts/ci/guard_extraction_agents.py`. Targets: `guard.extractors`.
- **M3** ⏳ PENDING: Visualization hooks — wire extraction outputs to visualization components, ensure data flows correctly from extraction → visualization, add visual verification (browser tools) for rendered outputs.

**PLAN-092: AgentPM-Next Planning Workflows** (📋 **Planned**)
- **M1** ✅ PASS: KB registry-powered planning surface (`pmagent plan kb`) — implemented `build_kb_doc_worklist()` that produces prioritized documentation worklist from KB registry status and hints (missing > stale > out_of_sync > low_coverage > info), grouped by subsystem with suggested actions. Hermetic: read-only, no writes, no LM calls. CLI command `pmagent plan kb` returns JSON worklist + human-readable summary. All tests passing (6/6). Artifacts: `agentpm/plan/kb.py`, `agentpm/tests/cli/test_pmagent_plan_kb.py`, `pmagent/cli.py` (plan_kb command). Targets: `pmagent plan kb`. (PR #580)
- **M2** ⏳ PENDING: Orchestrated doc-fix runs — consume `pmagent plan kb` worklist (by severity and subsystem) and define concrete automation/assistant behaviors around it. Implement `pmagent plan kb fix` or similar command that processes worklist items, suggests fixes, and optionally applies them (with confirmation). Integration with KB registry freshness tracking to update `last_refreshed_at` after fixes. Artifacts: `agentpm/plan/fix.py`, `agentpm/tests/cli/test_pmagent_plan_kb_fix.py`. Targets: `pmagent plan kb fix`.

**PLAN-073: MCP Strict DB Live & Receipts/Guards** (✅ **Complete**)
- **M12** ✅ PASS: Index summary receipt, chip coverage guard, trace badge, roundtrip guard, manifest linkage (E56–E60).
- **Complete** ✅ PASS: Wrap-up receipts/guards E61–E65 (badges rollup, chip-id uniqueness, sitemap min, manifest consistency, stale sweep).
- **M3** ✅ PASS: MCP strict live handshake, DB smoke, Atlas chip inject, strict trace (E11–E15, PR #457).
- **M4** ⏳ PENDING: Strict DB live proofs E16–E20 (checkpointer driver proof, DB SELECT 1 guard, Atlas chip latency, DSN host hash redaction, error path guard).

**PLAN-074 M14: Atlas UI Tiles + Guards** (✅ **Complete**)
- **E66** ✅ PASS: Versioned graph rollup metrics (receipt+guard) (PR #480)
- **E67** ✅ PASS: Per-node drilldown links (receipt+guard) (PR #481)
- **E68** ✅ PASS: Screenshot manifest canonicalized (receipt+guard) (PR #482)
- **E69** ✅ PASS: Reranker signal plumbed into badges (receipt+guard) (PR #483)
- **E70** ✅ PASS: Webproof bundle has backlinks (receipt+guard) (PR #485)

**PLAN-075: DSN Centralization + Control Plane** (Complete)
- **E71** ✅ PASS: Harden DSN centralization (guard + tests prove centralized loader usage) (PR #486)
- **E72** ✅ PASS: Control-plane DDL in schema "control" + schema snapshot artifact (PR #486)
- **E73** ✅ PASS: Control-plane smoke script (insert+select; DB-on) with HINT/DB-off tolerance (PR #487)
- **E74** ✅ PASS: Control-plane compliance MVs + mv_schema.json evidence (PR #488)
- **E75** ✅ PASS: Knowledge-MCP catalog view + mcp_catalog_stub.json evidence (PR #488)

**PLAN-076: Control-Plane Compliance Exports** (Complete)
- **E76** ✅ PASS: Control-plane compliance.head export JSON (PR #489)
- **E77** ✅ PASS: Control-plane top_violations_7d export JSON (PR #489)
- **E78** ✅ PASS: Control-plane top_violations_30d export JSON (PR #489)
- **E79** ✅ PASS: Guard for control-plane compliance exports (JSON-level validation, PR #490)
- **E80** ✅ PASS: Atlas/webproof page for control compliance with backlinks (PR #490)

**PLAN-077: Knowledge-MCP Surfacing (Control Plane)** (✅ **Complete**)

- **E81** ✅ PASS: MCP catalog export (`mcp_catalog.json`) from existing control-plane views (DB-off tolerant, centralized DSN loader) (PR #493).

- **E82** ✅ PASS: Capability rules export (`capability_rules.json`) summarizing `capability_rule` table posture (PR #494).

- **E83** ✅ PASS: Agent run summary export (`agent_runs_7d.json`) from `agent_run` / `capability_session` (7d window, DB-off tolerant) (PR #495).

- **E84** ✅ PASS: Guard for Knowledge-MCP exports (presence + JSON structure) with verdict JSON (PR #496).

- **E85** ✅ PASS: Atlas/Knowledge-MCP webproof page with backlinks to exports + guard verdict (PR #497).

**PLAN-078: Compliance Dashboards & Violation Browser (Phase-2 Milestone)** (📋 **Planned**)

- **E86** ⏳ PENDING: Compliance Summary Dashboard — Build `docs/atlas/dashboard/compliance_summary.html` with tiles: Total violations (24h / 7d / 30d), Violations per tool, Violations per violation code, Violations per ring level, "Top offenders" list (tools / patterns / nodes), Linkouts to raw JSON exports + guard verdicts. JSON metrics export (e.g. `share/atlas/control_plane/compliance_summary.json`). Guard + verdict JSON to ensure metrics exist, dashboard links to JSON and control-plane exports. Artifacts: `docs/atlas/dashboard/compliance_summary.html`, `share/atlas/control_plane/compliance_summary.json`, `scripts/guards/guard_compliance_summary_backlinks.py`, `evidence/guard_compliance_summary_backlinks.json`. Targets: `atlas.compliance.summary`, `guard.atlas.compliance.summary`.

- **E87** ⏳ PENDING: Violation Time-Series & Heatmaps — Build `docs/atlas/dashboard/compliance_timeseries.html` and `docs/atlas/dashboard/compliance_heatmap.html`. Visuals: Time-series of violations per code + per tool, Heatmap tool × violation type. JSON export (e.g. `share/atlas/control_plane/compliance_timeseries.json`). Guard verifying required charts + backlinks to JSON. Artifacts: `docs/atlas/dashboard/compliance_timeseries.html`, `docs/atlas/dashboard/compliance_heatmap.html`, `share/atlas/control_plane/compliance_timeseries.json`. Targets: `atlas.compliance.timeseries`, `atlas.compliance.heatmap`, `guard.atlas.compliance.timeseries`, `guard.atlas.compliance.heatmap`.

- **E88** ⏳ PENDING: Violation → Node & Pattern Drilldowns — For each violation: HTML page `docs/atlas/webproof/violations/<violation_id>.html`, Links to Node page, Pattern page, Guard receipt. Generator script: `scripts/atlas/generate_violation_pages.py`. Guard verifying every violation in the export has an HTML page, backlinks to receipts, nodes, patterns. Artifacts: `docs/atlas/webproof/violations/<violation_id>.html`, `scripts/atlas/generate_violation_pages.py`. Targets: `atlas.compliance.drilldowns`, `guard.atlas.compliance.drilldowns`.

- **E89** ⏳ PENDING: Unified Violation Browser — `docs/atlas/browser/violations.html` with Search, Filter (code, tool, ring, timestamp), Sort (severity, time, tool). Links to Summary + time-series dashboards, Drilldown pages, Raw JSON + guard verdicts. Guard to ensure filters and basic UX elements present, all key links resolve. Artifacts: `docs/atlas/browser/violations.html`. Targets: `atlas.violation.browser`, `guard.atlas.violation.browser`.

- **E90** ⏳ PENDING: Compliance Metrics in Graph Stats — New export: `share/atlas/control_plane/graph_compliance.json`. Metrics per Node, Pattern, Tool, Extraction batch. Integration into Graph stats pages, Node pages (compliance chips), Possibly a dedicated `graph_compliance.html` dashboard. Guards + webproof to verify metrics wired into Atlas. Artifacts: `scripts/db/control_graph_compliance_metrics_export.py`, `share/atlas/control_plane/graph_compliance.json`. Targets: `control.graph.compliance.export`, `guard.control.graph.compliance`, `atlas.graph.compliance`, `guard.atlas.graph.compliance`.

**PLAN-079: Guard Receipts, Screenshot Determinism, and Browser Validation** (📋 **Planned**)

- **E91** ⏳ PENDING: Guard Receipts Index & Browser — Build `docs/atlas/browser/guard_receipts.html` with searchable index of all guard receipts, links to violation drilldowns, filter by guard name/status/date. Guard verifies receipt index exists, all receipts linked, search functional. Artifacts: `docs/atlas/browser/guard_receipts.html`. Targets: `atlas.guard.receipts`, `guard.atlas.guard.receipts`.

- **E92** ⏳ PENDING: Screenshot Manifest Guard — Strengthen/extend from M14 screenshot manifest guard. Ensure all Atlas pages have screenshots, screenshots are deterministic (same content = same hash), manifest includes all required pages. Guard verifies screenshot manifest completeness, hash consistency. Artifacts: `scripts/guards/guard_screenshot_manifest.py`, `evidence/guard_screenshot_manifest.json`. Targets: `guard.screenshot.manifest`.

- **E93** ⏳ PENDING: Browser Verification Guard — Receipts for key Atlas pages via browser automation. Verify pages render correctly, links work, interactive elements functional. Guard verifies browser verification receipts exist for all key pages. Artifacts: `scripts/guards/guard_browser_verification.py`, `evidence/guard_browser_verification.json`. Targets: `guard.browser.verification`.

- **E94** ⏳ PENDING: Screenshot ↔ Tagproof Integration — Ensure tagproof bundle references all screenshots, screenshots included in tagproof artifacts, manifest validated in tagproof. Guard verifies tagproof includes screenshots, manifest consistency. Artifacts: `scripts/guards/guard_tagproof_screenshots.py`, `evidence/guard_tagproof_screenshots.json`. Targets: `guard.tagproof.screenshots`.

- **E95** ⏳ PENDING: Atlas Links Integrity Sweep — Scan for broken links across all Atlas pages, verify internal links resolve, external links accessible (or marked as external). Guard verifies no broken internal links, external links properly marked. Artifacts: `scripts/guards/guard_atlas_links.py`, `evidence/guard_atlas_links.json`. Targets: `guard.atlas.links`.

**PLAN-080: Phase-1+2 Verification Sweep & Tagproof** (📋 **Planned**)

- **E96** ⏳ PENDING: TV-01…TV-05 Re-Run & Coverage Receipt — Re-run all test vectors TV-01 through TV-05, generate coverage receipt showing all vectors pass, document any regressions or fixes needed. Guard verifies all TVs pass, coverage receipt generated. Artifacts: `evidence/tv_coverage_receipt.json`. Targets: `test.tv.coverage`.

- **E97** ⏳ PENDING: Gatekeeper / Guard Shim Coverage Audit — Audit gatekeeper and guard shim coverage, verify all guarded tool calls are covered, document any gaps. Guard verifies coverage audit complete, gaps documented. Artifacts: `evidence/gatekeeper_coverage_audit.json`. Targets: `audit.gatekeeper.coverage`.

- **E98** ⏳ PENDING: Full Extraction & Atlas + Exports Regeneration — Regenerate all extraction outputs, Atlas pages, and export JSONs from scratch to ensure consistency. Verify all exports match expected schemas, Atlas pages render correctly. Guard verifies regeneration complete, all artifacts valid. Artifacts: Regenerated `share/atlas/`, `share/exports/` directories. Targets: `regenerate.all`.

- **E99** ⏳ PENDING: Browser Verification & Screenshot Check (Integrated) — Run integrated browser verification and screenshot checks for all Atlas pages. Verify screenshots match expected content, browser verification passes for all pages. Guard verifies integrated checks pass. Artifacts: `evidence/browser_verification_integrated.json`, `evidence/screenshot_check_integrated.json`. Targets: `verify.browser.integrated`, `verify.screenshot.integrated`.

- **E100** ⏳ PENDING: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle — Create tagproof bundle with all Phase-1+2 artifacts: compliance exports, Atlas dashboards, guard receipts, screenshots, verification evidence. Enable STRICT mode validation for tag lane. Guard verifies tagproof bundle complete, STRICT validation passes. Artifacts: `tagproof/phase2_ready_bundle.tar.gz`, `evidence/tagproof_phase2_ready.json`. Targets: `tagproof.phase2.ready`.

**PLAN-090: Normalize Naming & Metrics (Pre-Implementation)** (📋 **Planned**)
- ⏳ PENDING: Normalize DB objects and schema IDs — tables prefix `mcp_*`, MVs prefix `mv_mcp_*`, columns prefer `status` (not `state`), add `created_at`/`updated_at` where applicable, idempotent migration. Normalize JSON Schemas — `$id` prefix `gemantria://v1/...`, `title` present, top-level `type: "object"` and `additionalProperties: false`. Add schema-naming guard `guard_schema_naming.py` (hermetic) + Makefile target `guard.schema.naming`. Artifacts: `db/migrations/2025-11-guarded-calls-p0.naming.sql`, `scripts/guards/guard_schema_naming.py`. Targets: `guard.schema.naming`.

**PLAN-091: Guarded Tool Calls P0 Execution** (📋 **Planned**)
- ⏳ PENDING: Integrate `jsonschema` validation for all P0 tool I/O schemas (with `$ref` to provenance). Gatekeeper/Guard enforce Proof-of-Readback (PoR) of constraints/tokens before any tool call. Minimal Postgres adapter that reads `mcp.v_catalog` via centralized DSN loader (RO only, no writes in PR CI). Turn TVs 01–05 green (missing-PoR, forbidden-tool, bad-args, ring-violation, bus-parity placeholder). Artifacts: `agentpm/guard/impl.py`, `agentpm/gatekeeper/impl.py`, `agentpm/adapters/mcp_db.py`, `agentpm/tests/test_guarded_calls_tv.py`. Targets: `guard.mcp.db.ro` (opt-in, no CI change).

**PLAN-081: Orchestrator Dashboard Polish** (📋 **Planned**)
- ⏳ PENDING: Add "MCP RO Proof" tile showing endpoint count + last tagproof timestamp. Add Browser-Verified Badge linking to browser verification screenshots (`browser_verified_index.png`, `browser_verified_mcp_catalog_view.png`). Keep clean, "semi-technical orchestrator" aesthetic; no backend changes. Artifacts: `webui/graph/components/MCPROProofTile.tsx`, `webui/graph/components/BrowserVerifiedBadge.tsx`. Integration into main orchestrator dashboard view with responsive layout and accessibility.

**Phase-1 Control Plane: Guarded Tool Calls** (Implementation Complete)
- ✅ PR-1: Control Plane DDL + Health Guard
- ✅ PR-2: Gatekeeper + PoR (TV-01)
- ✅ PR-3: Guard Shim + TVs 02–05
- ✅ PR-4: Atlas Compliance Export
- ⏳ Pending: Final test hardening in CI, governance wiring

#### Postgres Control Plane & Governance Recording (Current Reality)

- **Control schema (`control`)**: Migration `040_control_plane_schema.sql` creates the dedicated `control` schema with five core tables (`tool_catalog`, `capability_rule`, `doc_fragment`, `capability_session`, `agent_run`) plus `mv_compliance_7d` / `mv_compliance_30d` and the `control.refresh_compliance(window)` function. All writes go through centralized DSN loaders (`get_rw_dsn()`), and every row carries a `project_id` for multi-project support.
- **Guarded tool calls → agent_run**: The Phase-1 Guard Shim (`agentpm/guarded/guard_shim.py`) and Gatekeeper (`agentpm/guarded/gatekeeper.py`) record each guarded tool call into `control.agent_run`, including PoR status (`por_ok`), JSON Schema status (`schema_ok`), provenance status (`provenance_ok`), violation codes (`MISSING_POR`, `RING_VIOLATION`, etc.), seed/model/tool_version, latency, and retry counts. Materialized views aggregate these rows into 7d/30d compliance ratios and top violation maps, which are exported to `share/atlas/control_plane/*.json`.
- **Governance + housekeeping tracking**: Migration `015_create_governance_tracking.sql` creates `governance_artifacts`, `hint_emissions`, and `governance_compliance_log` to persist housekeeping and governance checks (Rule-026/Rule-058). Housekeeping scripts call `update_governance_artifact(...)`, `log_hint_emission(...)`, and `check_governance_freshness(...)` so that rule files, AGENTS.md entries, and runtime LOUD HINT emissions are mirrored into Postgres for audit and freshness monitoring.

---

## Phase 8: Multi-Temporal Analytics Suite

### Goals
- Rolling window analysis of temporal patterns in biblical texts
- Prophet-based forecasting for concept frequency trends
- Interactive temporal exploration UI components
- Schema validation and COMPASS mathematical correctness (>80% score)

### Deliverables
- `temporal_patterns.json` — Rolling statistics with z-scores and change points
- `pattern_forecast.json` — Prophet forecasts with confidence intervals
- Temporal strip visualization component
- COMPASS scorer for mathematical envelope validation

### Current Status: ✅ **Active**
- Rolling window computation implemented
- Temporal schema validation in place
- UI temporal strip component ready
- COMPASS scoring framework deployed

---

## Phase 9: Graph Latest Foundation

### Goals
- Complete graph export with nodes, edges, and metadata
- Node clustering and centrality calculations
- Edge strength computation and classification
- Export validation and schema compliance

### Deliverables
- `graph_latest.json` — Complete graph with 50k+ nodes
- `graph_stats.json` — Degree/betweenness/eigenvector metrics
- `graph_patterns.json` — Cross-text pattern analysis
- Schema validation guards

### Current Status: ✅ **Complete**
- Graph export pipeline operational
- Statistics computation working
- Pattern analysis integrated
- Schema guards active in CI

---

## Phase 10: Correlation Visualization

### Goals
- Cross-text pattern analytics with rerank edge strength
- Interactive correlation matrix visualization
- Pattern discovery and motif identification
- Performance optimization for large graphs

### Deliverables
- `correlation_weights.json` — Edge significance analysis
- `graph_correlations.json` — Matrix exports
- Interactive correlation viewer
- Optimized rendering for 100k+ nodes

### Current Status: ✅ **Complete**
- Correlation matrix generation active
- Edge strength rerank blend implemented
- Visualization components ready
- Performance gates in place

---

## Phase 11: Unified Envelope

### Goals
- Single integrated export format with all artifacts
- COMPASS mathematical envelope validation
- Size extraction (100, 1k, 10k, 100k+ nodes)
- Forward compatibility with schema evolution

### Deliverables
- `unified_envelope.json` — Complete integrated format
- COMPASS scorer (correlation + edge blend + temporal validation)
- Size-controlled extraction scripts
- Schema evolution support

### Current Status: ✅ **Complete**
- Unified envelope format implemented
- COMPASS validation framework active
- Size extraction working
- Schema evolution ready

---

## Technical Architecture

### Pipeline Flow
```
Noun Extraction → Enrichment → Network Building → Schema Validation → Analysis → Export
     ↓              ↓              ↓                    ↓             ↓         ↓
collect_nouns → enrichment → network_aggregator → schema_validator → analysis → export_graph
```

### Core Components
1. **LangGraph Orchestration** — Deterministic pipeline execution
2. **Qwen Live Gate** — Fail-closed AI health checks
3. **Schema Validation** — JSON Schema enforcement
4. **COMPASS Scoring** — Mathematical correctness validation
5. **Temporal Analytics** — Rolling windows + forecasting
6. **Unified Exports** — Integrated artifact format

### Quality Gates
- **Schema compliance** — All exports validated against SSOT schemas
- **Mathematical correctness** — COMPASS >80% score requirement
- **Determinism** — Identical inputs produce identical outputs
- **Safety** — bible_db read-only, fail-closed on errors
- **Performance** — Size gates prevent resource exhaustion

---

## Data Lineage

### Primary Artifacts
1. `graph_latest.json` — Core graph with nodes/edges/metadata
2. `temporal_patterns.json` — Time-series rolling window analysis
3. `pattern_forecast.json` — Prophet forecasting results
4. `correlation_weights.json` — Cross-text pattern analytics
5. `unified_envelope.json` — Single integrated format (Phase 11)

### Export Scripts
- `scripts/extract/extract_all.py` — Unified extraction with size controls
- `scripts/temporal_analytics.py` — Rolling window + forecast computation
- `scripts/export_graph.py` — Graph export with statistics
- `scripts/export_correlations.py` — Pattern correlation analysis

---

## Governance & Operations

### Governance: Always-Apply Triad
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
This plan assumes and re-affirms the triad:

**050 (LOUD FAIL)**, **051 (Required Checks Gate)**, **052 (Tool-Priority: local+gh → codex (401) → gemini/mcp)**.

These are active on every branch/state and are not pruned or downgraded.

<!-- guard.alwaysapply sentinel: 050 051 052 -->

### Rules Framework
- **Rule 001-061** — Complete governance rule set
- **OPS Contract v6.2.3** — Execution discipline
- **SSOT Schemas** — docs/SSOT/ directory
- **SHARE_MANIFEST.json** — Export synchronization

### CI/CD Pipeline
- **Hermetic builds** — No external dependencies
- **Schema validation** — All exports checked
- **Mathematical verification** — COMPASS scoring
- **Performance gates** — Size and time limits
- **Determinism checks** — Reproducible outputs

### Agent Framework
- **Ingestion Agent** — Text → shards
- **Discovery Agent** — Organic noun extraction
- **Enrichment Agent** — Theological context
- **Graph Builder** — Network construction
- **Analytics Agent** — Stats + patterns + temporal
- **Guard Agent** — Schema + invariants validation

---

## Next Steps
- Project unification and single UI shell (see RFC-081).


### Phase-3B: pmagent Control-Plane Health Suite (✅ **Complete**)
- ✅ **Feature #4**: `pmagent health` CLI (system, db, lm, graph)
- ✅ **Feature #5**: `pmagent graph import + overview`
- ✅ **Feature #6**: `pmagent control status` (control-plane database posture)
- ✅ **Feature #7**: `pmagent control tables` (schema-qualified table listing)
- ✅ **Feature #8**: `pmagent control schema` (DDL introspection)
- ✅ **Feature #9**: `pmagent control pipeline-status` (recent pipeline runs summary)
- ✅ **Feature #10**: `pmagent control summary` (aggregated control-plane summary)

**Phase-3B Completion**: All control-plane introspection commands implemented, tested, documented, and integrated into `pmagent` CLI. Hermetic DB-off behavior preserved throughout.

### Phase-3C: LM Studio + Control Plane Integration (✅ **Complete**)
- **RFC-080**: LM Studio + Control Plane Integration (ratified by ADR-066)
- **P0**: LM Studio adapter + routing helper (PR #532)
- **P1**: `pmagent health lm` + control-plane logging wrapper (`lm_studio_chat_with_logging`) (PR #533)
- **P1b/P2**: Enrichment pipeline routing + LM Studio setup runbook/docs (PR #533)

**Phase-3C Status**: ✅ **PLUMBING COMPLETE** — LM Studio integration is fully wired. DB/LM may still be off by default (hermetic behavior preserved). See [RFC-080](../rfcs/RFC-080-lm-studio-control-plane-integration.md) and [ADR-066](../ADRs/ADR-066-lm-studio-control-plane-integration.md) for details.

### Phase-3D: LM Observability & Status UI (✅ **Complete**)
- **D1**: LM metrics exports (PR #534)
  - `share/atlas/control_plane/lm_usage_7d.json` — Usage metrics (total calls, success/failure, latency, tokens)
  - `share/atlas/control_plane/lm_health_7d.json` — Health metrics (health score, success/error rates, error types)
  - db_off + LM-off safe (graceful no-op when DB unavailable)
- **D2**: Atlas LM dashboards (PR #535)
  - Usage dashboard config: `docs/atlas/config/lm_usage_dashboard.json`
  - Health dashboard config: `docs/atlas/config/lm_health_dashboard.json`
  - Both dashboards driven by D1 JSON exports
- **D3**: HTML LM status page (PR #535)
  - `docs/atlas/html/lm_status.html` — Non-technical user-friendly status page
  - Browser Verification (Rule-067): Screenshot in `share/webproof/lm/browser_verified_lm_status.png`
  - Explicit db_off handling: Page shows "no data / offline" messaging when DB unavailable
  - Auto-refresh every 30 seconds

**Phase-3D Status**: ✅ **COMPLETE** — All LM observability artifacts are in place and browser-verified. Status page is readable and helpful in db_off mode.

### Phase-4: LM Insights & UI Polish (✅ **COMPLETE**)
- **4A**: LM Insights exports ✅
  - Higher-level JSON export (`lm_insights_7d.json`) summarizing:
    - `lm_studio_usage_ratio` — Percentage of calls using LM Studio vs fallback
    - `fallback_rate` — Rate of fallback to legacy `chat_completion()`
    - `top_error_reason` — Most common error types/causes
    - Additional aggregated insights from `lm_usage_7d.json` and `lm_health_7d.json`
  - db_off-safe (emit "no data" but don't crash)
- **4B**: LM status page UX polish ✅
  - One-sentence summary at the top ("LM Studio is offline / healthy / degraded")
  - Simple explanations of "health score", "db_off", "error_rate" for non-technical users
  - Friendlier layout and typography improvements
  - Consumes `lm_insights_7d.json` for unified status display
- **4C**: LM indicator export for downstream apps ✅
  - Compact JSON export (`lm_indicator.json`) with status classification:
    - `status`: "offline" | "healthy" | "degraded"
    - `reason`: "db_off" | "no_calls" | "high_error_rate" | "ok"
    - Core metrics: `success_rate`, `error_rate`, `total_calls`, `db_off`
  - **Canonical LM status signal for downstream apps** (StoryMaker, BibleScholar, etc.)
  - Derived from `lm_insights_7d.json` (hermetic, no DB/LM calls)
- **4D**: Governance/docs alignment ✅
  - Updated ADR-066 with Phase-4 exports list
  - Updated AGENTS.md, LM_STUDIO_SETUP.md, CHANGELOG.md, and SHARE_MANIFEST
  - Documented `lm_indicator.json` as canonical downstream signal

**Phase-4 Status**: ✅ **COMPLETE** — All LM observability exports are in place, status page is UX-polished, and indicator export provides a canonical signal for downstream apps. All enhancements maintain db_off + LM-off safety.

### Phase-5: StoryMaker & BibleScholar LM Integration (✅ **COMPLETE**)

- **5A**: LM indicator widget contract finalized in `LM_WIDGETS.md` ✅
- **5B**: Hermetic LM indicator adapter implemented in Gemantria (`load_lm_indicator_widget_props`) ✅
- **5C**: StoryMaker integration — LM status tile using the widget props (PR #1 in storymaker-bundle-v1.6) ✅
- **5D**: BibleScholar integration — header status badge using the widget props (PR #2 in BibleScholarProjectClean) ✅

**Phase-5 Status**: ✅ **COMPLETE** — Both StoryMaker and BibleScholar now consume the canonical `lm_indicator.json` signal via
the shared LM widget contract. All adapters are hermetic and fail-closed (offline-safe) and do not introduce new heuristics.

### Phase-6: LM Studio Live Usage + DB-Backed Knowledge (📘 IN PROGRESS)

- **6A**: LM Studio live usage enablement (guarded calls + logs) ✅ **COMPLETE**
- **6B**: LM usage budgets + rate tracking ✅ **COMPLETE**
  - control.lm_usage_budget table with per-app budgets (migration 042)
  - Budget enforcement in guarded_lm_call() with "budget_exceeded" mode
  - lm_budget_7d.json export for visibility
- **6C**: Knowledge Slice v0 (DB-backed) ✅ **COMPLETE**
  - knowledge schema with kb_document and kb_embedding tables (migration 043)
  - Markdown ingestion script (control_kb_ingest.py) with db_off safety
  - KB export script (control_kb_export.py) → kb_docs.head.json
  - Make targets: atlas.kb.ingest, atlas.kb.export
  - Hermetic tests for ingestion and export
- **6J**: BibleScholar Gematria adapter (read-only) ✅ **COMPLETE** (2025-11-15)
  - `agentpm/biblescholar/gematria_adapter.py` — Read-only adapter for Gematria numerics
  - Mispar Hechrachi and Mispar Gadol support
  - DB-off mode handling (graceful degradation)
- **6M**: Bible DB read-only adapter + passage flow ✅ **COMPLETE** (2025-11-15)
  - `agentpm/biblescholar/bible_db_adapter.py` — Read-only adapter for `bible_db`
  - `agentpm/biblescholar/bible_passage_flow.py` — Passage/verse retrieval flow
  - Verse lookup by book/chapter/verse (reference string parsing)
  - Multi-translation support (KJV default, extensible)
  - DB-off mode handling (graceful degradation)
- **6O**: Vector similarity adapter + verse-similarity flow ✅ **COMPLETE** (2025-11-15, PR #557)
  - `agentpm/biblescholar/vector_adapter.py` — Vector similarity adapter (pgvector)
  - `agentpm/biblescholar/vector_flow.py` — Verse-similarity flow wrapper
  - Read-only vector similarity using pgvector cosine distance
  - DB-off mode handling (graceful degradation)
- **6P**: BibleScholar Reference Answer Slice 📋 **PLANNING** (design doc only)
  - Single E2E BibleScholar interaction using LM Studio (guarded), bible_db (read-only), Gematria adapter, and optional knowledge slice
  - Inputs: Natural-language question + optional verse reference
  - Flow: Resolve verse context → Retrieve Gematria patterns → Perform LM Studio guarded call → Synthesize output with justification + trace
  - Outputs: `{ answer: str, trace: [...], context_used: {...} }`
  - Constraints: No new DSNs, must pass db_off hermetic mode, budget enforcement + provenance required
  - Dependencies: 6J, 6M, 6O, 6A, 6B, 6C (all COMPLETE)
  - See `docs/SSOT/BIBLESCHOLAR_REFERENCE_SLICE.md` for design details
- **6D**: Downstream app read-only wiring (StoryMaker + BibleScholar) 📘 PLANNING
- **6E**: Governance & SSOT updates 📘 PLANNING

**Goal**: Move from "LM off" → controlled, observable usage & DB-backed knowledge.

### Phase-7: Runtime Bring-Up Completion (Planning)

- **7A**: Control-Plane Bring-Up (Migration 040) 📋 PLANNING
  - Safely apply migration 040 (dev only)
  - Create the `control` schema and verify required tables/views
  - Re-run the pipeline step previously blocked on "missing control schema"
- **7B**: LM Studio & Model Configuration Normalization 📋 PLANNING
  - Standardize env vars (`THEOLOGY_MODEL`, `MATH_MODEL`, `EMBEDDING_MODEL`, `RERANKER_MODEL`)
  - Align LM Studio adapter defaults with env configuration
  - Update env_example.txt + GPT reference docs
- **7C**: Snapshot Integrity & Drift Review 📋 PLANNING
  - Compare 21-file GPT snapshot contracts vs current repo
  - Classify drift (RED/YELLOW/GREEN)
  - Minimal remediation PRs to realign repo with SSOT or update SSOT accordingly
- **7D**: Runtime & Bring-Up UX Polish (Optional) 📋 PLANNING
  - Improve pmagent bringup / mcp UX for non-expert users
  - Enhanced help text, clearer Reality Check messages, wizard-style flows

- **7E**: Core LLM Prompting Guide (Design Doc) ✅ COMPLETE (docs only)
  - `Prompting Guide for Our Core LLM models.md` documents the Granite 4.0 + BGE-M3 + Granite Reranker stack, chat templates, embedding usage, and reranker prompting.
  - Treated as a **design-level MoE-of-MoEs spec** for future router work; runtime model bindings remain governed by `AGENTS.md` until an explicit Phase-7 implementation milestone is marked complete.

**Goal**: Complete Phase 6 setup and establish operational baseline for production use.

**Status**: 📋 **PLANNING**

### Immediate (PLAN-074 M14 Complete)
- [x] E66: Versioned graph rollup metrics (receipt + guard) ✅
- [x] E67: Per-node drilldown links (receipt + guard) ✅
- [x] E68: Screenshot manifest canonicalized (receipt + guard) ✅
- [x] E69: Reranker signal plumbed into badges (receipt + guard) ✅
- [x] E70: Webproof bundle has backlinks (receipt + guard) ✅
- [x] Complete M14 test suite (all E66–E70 PASS) ✅

### PLAN-078: Compliance Dashboards (Phase-2 Milestone)
- [ ] E86: Compliance Summary Dashboard
- [ ] E87: Violation Time-Series + Heatmaps
- [ ] E88: Violation → Node & Pattern Drilldowns
- [ ] E89: Unified Violation Browser
- [ ] E90: Compliance Metrics in Graph Stats

**PLAN-078 Completion Criteria:** Phase-2 is done when all dashboards render correctly in browser verification, all charts link to correct JSON exports, violation browser functional with search/sort/filter, violation drilldowns render correctly + screenshots stable, all guards produce `ok=true`, tag lane STRICT validates all Atlas dashboards/webproofs/backlinks/screenshots/relevant JSON exports, tagproof bundle includes compliance dashboards/drilldowns/knowledge-MCP pages/screenshots/guard receipts with zero broken links. When complete → **Phase 2 is officially finished** → unlocks **Phase 3** (LM Studio + Knowledge Plane).

### PLAN-079: Guard Receipts, Screenshot Determinism, and Browser Validation
- [ ] E91: Guard Receipts Index & Browser
- [ ] E92: Screenshot Manifest Guard
- [ ] E93: Browser Verification Guard
- [ ] E94: Screenshot ↔ Tagproof Integration
- [ ] E95: Atlas Links Integrity Sweep

### PLAN-080: Phase-1+2 Verification Sweep & Tagproof
- [ ] E96: TV-01…TV-05 Re-Run & Coverage Receipt
- [ ] E97: Gatekeeper / Guard Shim Coverage Audit
- [ ] E98: Full Extraction & Atlas + Exports Regeneration
- [ ] E99: Browser Verification & Screenshot Check (Integrated)
- [ ] E100: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle

### Phase-1 Control Plane (Testing & Governance)
- [ ] Final test hardening in CI (STRICT vs HINT mode)
- [ ] Governance wiring (tag lanes run guards/exports)
- [ ] Atlas UI linkage for compliance exports

### Medium-term (Q1 2026)
- [ ] Phase 12: Advanced Pattern Mining
- [ ] Phase 13: Multi-language Support
- [ ] Phase 14: Real-time Analytics
- [ ] Phase 15: API Gateway

### Long-term Vision
- **Complete Biblical Analytics Suite** — Full corpus analysis
- **Interactive Exploration Platform** — Web-based discovery tools
- **Academic Research Integration** — Scholar collaboration features
- **Global Accessibility** — Multi-language biblical text support

---

## Success Metrics

### Technical Metrics
- **Coverage**: >98% test coverage maintained
- **Performance**: <30s for 100k node exports
- **Correctness**: COMPASS >80% score on all envelopes
- **Reliability**: 99.9% pipeline success rate

### Product Metrics
- **Completeness**: All major biblical books analyzed
- **Accuracy**: Verified gematria calculations
- **Usability**: Intuitive visualization interfaces
- **Adoption**: Active research community engagement

---

## Risk Mitigation

### Technical Risks
- **Scale**: Size gates and performance monitoring
- **Data Integrity**: Schema validation + COMPASS scoring
- **AI Dependency**: Fail-closed Qwen Live Gate
- **Determinism**: Fixed seeds + content hashing

### Operational Risks
- **Code Drift**: git pull blocking + wrapper scripts
- **Schema Evolution**: Versioned schemas + compatibility
- **CI Stability**: Hermetic builds + rollback procedures
- **Documentation**: SSOT sync + automated updates

---

## Conclusion

The Gemantria project represents a comprehensive approach to biblical text analysis, combining rigorous mathematical methods with AI-powered insights and interactive visualization. Through careful phase planning, strict governance, and mathematical validation, we deliver reliable, reproducible results for biblical research and exploration.

**Current Focus**: Phase 8 temporal analytics completion and Phase 11 unified envelope stabilization.

**Next Milestone**: Phase 12 advanced pattern mining capabilities.

<!-- RULES_TABLE_START -->
| # | Title |
|---:|-------|
| 000 | # 000-ssot-index (AlwaysApply) |
| 001 | # --- |
| 002 | # --- |
| 003 | # --- |
| 004 | # --- |
| 005 | # --- |
| 006 | # --- |
| 007 | # --- |
| 008 | # --- |
| 009 | # --- |
| 010 | # --- |
| 011 | # --- |
| 012 | # --- |
| 013 | # --- |
| 014 | # --- |
| 015 | # --- |
| 016 | # --- |
| 017 | # --- |
| 018 | # --- |
| 019 | # --- |
| 020 | # --- |
| 021 | # --- |
| 022 | # --- |
| 023 | # --- |
| 024 | # --- |
| 025 | # --- |
| 026 | # --- |
| 027 | # --- |
| 028 | # --- |
| 029 | # --- |
| 030 | # --- |
| 031 | # --- |
| 032 | # --- |
| 033 | # --- |
| 034 | # --- |
| 035 | # --- |
| 036 | # --- |
| 037 | # --- |
| 038 | # --- |
| 039 | # --- |
| 040 | # --- |
| 041 | # --- |
| 042 | # --- |
| 043 | # --- |
| 044 | # --- |
| 045 | # --- |
| 046 | # --- |
| 047 | # --- |
| 048 | # --- |
| 049 | # --- |
| 050 | # --- |
| 051 | # --- |
| 052 | # --- |
| 053 | # --- |
| 054 | # --- |
| 055 | # --- |
| 056 | # --- |
| 057 | # --- |
| 058 | # --- |
| 059 | # --- |
| 060 | # --- |
| 061 | # --- |
| 062 | # --- |
| 063 | # --- |
| 064 | # id: "064" |
| 065 | # Rule 065 — Auto-Normalize on Branch Switch & PR Events |
| 066 | # --- |
| 067 | # Rule 067 — Atlas Webproof (Browser-Verified UI) |
| 068 | # --- |
<!-- RULES_TABLE_END -->
