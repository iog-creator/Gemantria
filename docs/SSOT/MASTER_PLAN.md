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
- **M1** ✅ COMPLETE: DMS guard fixes — ensure documentation management guards are hermetic and pass in CI. Implemented HINT/STRICT mode support for `guard_docs_db_ssot.py` (DB-off tolerance in HINT mode, fail-closed in STRICT mode). Created `agentpm/tests/docs/test_dms_guards.py` with 7 tests covering HINT/STRICT behavior (all passing). Updated Makefile with `guard.docs.db.ssot` (HINT) and `guard.docs.db.ssot.strict` (STRICT) targets. Documentation updated: `scripts/AGENTS.md`, `agentpm/tests/docs/AGENTS.md`. See `docs/SSOT/PLAN_072_M1_DMS_GUARDS.md`.
- **M2** ✅ COMPLETE: Extraction agents provenance (TVs E06–E10) — implemented provenance logic (`ensure_provenance`, `guard_provenance`, `stamp_batch`) with full test coverage, guard integration, and AGENTS.md documentation. All 5 TVs (E06–E10) implemented, tested, guarded (PR #499). Artifacts: `agentpm/extractors/provenance.py`, `agentpm/tests/extractors/test_extraction_provenance_e06_e10.py`, `agentpm/extractors/AGENTS.md`, `scripts/ci/guard_extraction_agents.py`. Targets: `guard.extractors`.
- **M3** ✅ COMPLETE: Visualization hooks — Wired E21–E25 proofs into Atlas dashboards and control widgets. Created `scripts/atlas/generate_mcp_status_cards.py` to generate `share/atlas/control_plane/mcp_status_cards.json`. Updated Atlas HTML pages: `compliance_summary.html` (MCP status cards tile), `guard_receipts.html` (proof links), `violations.html` (proof status table). Extended `agentpm/control_widgets/adapter.py` with `load_mcp_status_cards_widget_props()` function. Tests: `agentpm/tests/control_widgets/test_m2_visualization.py` (5 tests, all passing). Guards: `guard_control_widgets`, `guard_browser_verification` passing. Browser verification: all 7 pages verified.

**PLAN-092: AgentPM-Next Planning Workflows** (📋 **Planned**)
- **M1** ✅ PASS: KB registry-powered planning surface (`pmagent plan kb`) — implemented `build_kb_doc_worklist()` that produces prioritized documentation worklist from KB registry status and hints (missing > stale > out_of_sync > low_coverage > info), grouped by subsystem with suggested actions. Hermetic: read-only, no writes, no LM calls. CLI command `pmagent plan kb` returns JSON worklist + human-readable summary. All tests passing (6/6). Artifacts: `agentpm/plan/kb.py`, `agentpm/tests/cli/test_pmagent_plan_kb.py`, `pmagent/cli.py` (plan_kb command). Targets: `pmagent plan kb`. (PR #580)
- **M2** ✅ PASS: Orchestrated doc-fix runs — consume `pmagent plan kb` worklist (by severity and subsystem) and define concrete automation/assistant behaviors around it. Implement `pmagent plan kb fix` or similar command that processes worklist items, suggests fixes, and optionally applies them (with confirmation). Integration with KB registry freshness tracking to update `last_refreshed_at` after fixes. Artifacts: `agentpm/plan/fix.py`, `agentpm/tests/cli/test_pmagent_plan_kb_fix.py`. Targets: `pmagent plan kb fix`. (PR #581)
- **M3** ✅ PASS: Doc-health control loop & reporting — `pmagent report kb` aggregates M1 worklists and M2 fix manifests into doc-health metrics and trends. `pm.snapshot` now includes an advisory "Documentation Health" section with fresh ratios, missing/stale counts, and fix activity. Artifacts: `agentpm/status/kb_metrics.py`, `pmagent/cli.py` (report_kb), `agentpm/tests/cli/test_pmagent_report_kb.py`. Targets: `pmagent report kb`. (PR #582)
- **M4** ✅ PASS: Atlas UI Integration — `/status` page now visualizes KB doc health metrics (freshness score, fixes applied, missing/stale counts) in the "Documentation Health" card. `/api/status/system` endpoint includes `kb_doc_health` data for UI consumption. UI elements include metrics container, freshness percentage, fixes counter, and missing/stale breakdown. JavaScript loads and displays metrics from API response with graceful fallbacks. Tests verify HTML elements and API integration. (PR #583)
- **Planning Lane (NEW)**: pmagent now owns a **planning slot** that can dispatch coding/maths/planning tasks to Gemini CLI or OpenAI Codex when `PLANNING_PROVIDER` is set. These CLIs are governed like any other inference provider: configuration lives in `env_example.txt`, adapters are hermetic, and AI tracking captures every run. Operators drive the lane through `pmagent tools.plan`, `pmagent tools.gemini`, or `pmagent tools.codex` (see `docs/runbooks/GEMINI_CLI.md` + `docs/runbooks/CODEX_CLI.md`). The planning lane is explicitly **non-theology**: gematria/theology pipelines stay on LM Studio/Ollama, while planning helpers are reserved for backend work, decomposition, and math-heavy reasoning. Large-context, multi-agent runs are allowed, but CI/dev defaults keep the CLIs disabled unless an operator opts in.

**PLAN-073: MCP Strict DB Live & Receipts/Guards** (✅ **Complete**)
- **M12** ✅ PASS: Index summary receipt, chip coverage guard, trace badge, roundtrip guard, manifest linkage (E56–E60).
- **Complete** ✅ PASS: Wrap-up receipts/guards E61–E65 (badges rollup, chip-id uniqueness, sitemap min, manifest consistency, stale sweep).
- **M3** ✅ PASS: MCP strict live handshake, DB smoke, Atlas chip inject, strict trace (E11–E15, PR #457).
- **M4** ✅ PASS: Strict DB live proofs E16–E20 (checkpointer driver proof, DB SELECT 1 guard, Atlas chip latency, DSN host hash redaction, error path guard). All 5 tests passing. Proof artifacts: `share/mcp/pg_checkpointer.handshake.json`, `share/mcp/db_select1.ok.json`, `share/atlas/db_proof_chip.json`, `share/mcp/db_error.guard.json`. Make target: `make mcp.strict.live.full`.
- **M2** ✅ PASS: Strict DB RO proofs E21–E25 (POR proof, schema proof, gatekeeper coverage, tagproof bundle, complete bundle aggregate). All 5 tests passing. Proof artifacts: `share/mcp/por_proof.json`, `share/mcp/schema_proof.json`, `share/mcp/gatekeeper_proof.json`, `share/mcp/tagproof_proof.json`, `share/mcp/bundle_proof.json`. Make target: `make mcp.strict.live.phase2`.
- **M3** ✅ PASS: Visualization Hooks — Wired E21–E25 proofs into Atlas dashboards and control widgets. Created `scripts/atlas/generate_mcp_status_cards.py` to generate `share/atlas/control_plane/mcp_status_cards.json`. Updated Atlas HTML pages: `compliance_summary.html` (MCP status cards tile), `guard_receipts.html` (proof links), `violations.html` (proof status table). Extended `agentpm/control_widgets/adapter.py` with `load_mcp_status_cards_widget_props()` function. Tests: `agentpm/tests/control_widgets/test_m2_visualization.py` (5 tests, all passing). Guards: `guard_control_widgets`, `guard_browser_verification` passing. Browser verification: all 7 pages verified.

**PLAN-073 M1: Knowledge MCP Foundation** (✅ **COMPLETE**)
- All E01–E05 components implemented and tested. See detailed section above (lines 93-98) and `docs/SSOT/PLAN_073_M1_KNOWLEDGE_MCP.md` for full implementation details.

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

- **E86** ✅ PASS: Compliance Summary Dashboard — Dashboard `docs/atlas/dashboard/compliance_summary.html` with tiles for Total violations (24h/7d/30d), Violations by code, Violations by tool, Top offenders list. JSON export `share/atlas/control_plane/compliance_summary.json` with aggregated metrics from control-plane exports. Guard `scripts/guards/guard_compliance_summary_backlinks.py` validates structure and backlinks. Make targets `atlas.compliance.summary` + `guard.atlas.compliance.summary` working. Tests `agentpm/tests/atlas/test_e86_compliance_summary.py` (4 tests, all passing). Dashboard renders correctly with browser verification.

- **E87** ✅ PASS: Violation Time-Series & Heatmaps — Time-series dashboard `docs/atlas/dashboard/compliance_timeseries.html` with code/tool trends, heatmap dashboard `docs/atlas/dashboard/compliance_heatmap.html` with tool×code matrix visualization. JSON export `share/atlas/control_plane/compliance_timeseries.json` with series_by_code, series_by_tool, heatmap_tool_by_code. Guard `scripts/guards/guard_atlas_compliance_timeseries.py` validates structure and backlinks. Make targets `atlas.compliance.timeseries` + `atlas.compliance.heatmap` + `guard.atlas.compliance.timeseries` working. Tests `agentpm/tests/atlas/test_e87_compliance_timeseries.py` (12 tests, all passing). Webproof and reality.green passing.

- **E88** ✅ PASS: Violation → Node & Pattern Drilldowns — For each violation code: HTML page `docs/atlas/webproof/violations/<violation_code>.html`, Links to Node pages, Pattern pages, Guard receipts, Compliance dashboards. Generator script: `scripts/atlas/generate_violation_pages.py`. Guard `scripts/guards/guard_atlas_compliance_drilldowns.py` verifying every violation code in exports has an HTML page with required backlinks. Artifacts: `docs/atlas/webproof/violations/*.html`, `scripts/atlas/generate_violation_pages.py`, `scripts/guards/guard_atlas_compliance_drilldowns.py`. Targets: `atlas.compliance.drilldowns`, `guard.atlas.compliance.drilldowns`. All guards passing.

- **E89** ✅ PASS: Unified Violation Browser — `docs/atlas/browser/violations.html` with Search, Filter (code), Sort (code, count-7d, count-30d, count-total). Links to Summary + time-series dashboards, Drilldown pages, Raw JSON exports, Guard receipts. Generator script: `scripts/atlas/generate_violation_browser.py`. Guard `scripts/guards/guard_atlas_violation_browser.py` validates filters, UI elements, and backlinks. Artifacts: `docs/atlas/browser/violations.html`, `scripts/atlas/generate_violation_browser.py`, `scripts/guards/guard_atlas_violation_browser.py`. Targets: `atlas.violation.browser`, `guard.atlas.violation.browser`. Browser verification passed.

- **E90** ✅ PASS: Compliance Metrics in Graph Stats — Export `share/atlas/control_plane/graph_compliance.json` with metrics per Tool, Node, Pattern, and Extraction batch. Aggregates violations from `control.agent_run` over 30-day window. Generator script: `scripts/db/control_graph_compliance_metrics_export.py`. Guard `scripts/guards/guard_control_graph_compliance.py` validates structure, schema, timestamp, and metrics presence. Linked from violations browser. Artifacts: `share/atlas/control_plane/graph_compliance.json`, `scripts/db/control_graph_compliance_metrics_export.py`, `scripts/guards/guard_control_graph_compliance.py`. Targets: `control.graph.compliance.export`, `guard.control.graph.compliance`. Browser verification passed.

**PLAN-079: Guard Receipts, Screenshot Determinism, and Browser Validation** (📋 **Planned**)

- **E91** ✅ PASS: Guard Receipts Index & Browser — Searchable index `docs/atlas/browser/guard_receipts.html` with all guard receipts, backlinks to compliance dashboards and violations browser, filter by status. Guard `scripts/guards/guard_atlas_guard_receipts.py` validates HTML structure, backlinks, E91 badge. Tests `agentpm/tests/atlas/test_e91_guard_receipts_index.py` (6 tests, all passing). Make targets `atlas.guard.receipts` + `guard.atlas.guard.receipts` working. Browser verification passed.

- **E92** ✅ PASS: Screenshot Manifest Guard — Guard `scripts/guards/guard_screenshot_manifest.py` validates screenshot manifest structure, hash determinism, and Atlas page coverage. Checks manifest at `share/atlas/screenshots/manifest.json` (primary) or `evidence/` fallbacks. Validates JSON structure, non-empty entries, hash shape consistency (when hash fields present), and reports coverage gaps. Tests `agentpm/tests/atlas/test_e92_screenshot_manifest_guard.py` (6 tests, all passing). Make target `guard.screenshot.manifest` working. Guard passes when manifest structure and hash determinism are valid (coverage is advisory/HINT mode).

- **E93** ✅ PASS: Browser Verification Guard — Guard `scripts/guards/guard_browser_verification.py` validates browser verification receipts for key Atlas pages. Checks `evidence/webproof/report.json` and screenshots, verifies core pages (index.html, mcp_catalog_view.html) are covered, reports optional pages as HINT mode. Validates report structure, screenshot presence, and page coverage. Tests `agentpm/tests/atlas/test_e93_browser_verification_guard.py` (6 tests, all passing). Make target `guard.browser.verification` working. Guard passes when core pages verified and report structure valid.

- **E94** ✅ PASS: Screenshot ↔ Tagproof Integration — Guard `scripts/guards/guard_tagproof_screenshots.py` discovers tagproof directories (`tagproof/`, `share/releases/*/tagproof`), PNG screenshots, and flexible screenshot manifest JSONs, then verifies manifest coverage and consistency. Emits JSON verdict to stdout and optional evidence file `evidence/guard_tagproof_screenshots.json` when invoked with `--write-evidence`. Checks `tagproof_dir_exists`, `has_tagproof_screenshots`, `manifest_nonempty`, `all_screenshots_listed`, and `no_manifest_orphans` with detailed debug lists for unlisted screenshots and orphan manifest entries. Tests `agentpm/tests/atlas/test_e94_tagproof_screenshots_guard.py` (3 tests, all passing). Make target `guard.tagproof.screenshots` wired to write evidence JSON for tag/CI lanes.

- **E95** ✅ PASS: Atlas Links Integrity Sweep — Guard `scripts/guards/guard_atlas_links.py` scans all Atlas HTML pages for broken links, verifies internal links resolve within `docs/atlas/`, and ensures external links are marked (class/rel/data-external). Handles absolute paths (`/...`) as app routes (tracked separately), whitelists evidence/share links (diagnostic, reported but non-blocking), and validates true internal links. Emits JSON verdict with checks, counts, and details. Tests `agentpm/tests/atlas/test_e95_atlas_links_guard.py` (5 tests, all passing). Make target `guard.atlas.links` working. Integrated into E99 guard. Guard passes when no broken internal links and all external links properly marked.

**PLAN-080: Phase-1+2 Verification Sweep & Tagproof** (✅ **Complete**)

- **E96** ✅ PASS: TV-01…TV-05 Re-Run & Coverage Receipt — All test vectors TV-01 through TV-05 re-run with coverage receipt generated and guarded. Guard verifies all TVs pass and the coverage receipt is valid. Artifacts: `evidence/tv_coverage_receipt.json`. Targets: `test.tv.coverage`, `guard.tv.coverage`.

- **E97** ✅ PASS: Gatekeeper / Guard Shim Coverage Audit — Gatekeeper and guard shim coverage audited; all seven violation codes are present and marked covered in the manifest. Guard verifies the coverage audit is complete with no uncovered codes. Artifacts: `evidence/gatekeeper_coverage.json`. Targets: `gatekeeper.coverage`, `guard.gatekeeper.coverage`.

- **E98** ✅ PASS: Full Extraction & Atlas + Exports Regeneration — All extraction outputs, Atlas pages, and export JSONs regenerated from scratch and validated. Guards confirm exports smokes, Atlas viewer validation, schema checks, and analytics export succeed. Artifacts: regenerated `share/atlas/`, `share/exports/` directories plus `share/exports/graph_latest.json`, `share/exports/graph_stats.json`, `share/exports/graph_patterns.json`, `share/exports/temporal_patterns.json`, `share/exports/pattern_forecast.json`. Targets: `regenerate.all`, `ci.exports.smoke`, `atlas.viewer.validate`, `schema.validate`, `analytics.export`.

- **E99** ✅ PASS: Browser Verification & Screenshot Check (Integrated) — Integrated browser verification and screenshot checks run for key Atlas pages via `browser.verify` (Rule-051 + Rule-067), with headless receipts and screenshots captured. Guard wiring for the aggregated browser+screenshot checks is in place for tag lanes. Artifacts: `evidence/webproof/browser_verify_instructions.txt`, `evidence/webproof/report.json`, `evidence/webproof/index.png`, `evidence/webproof/catalog.png`, `evidence/webproof/dashboard_page.png`, `evidence/webproof/status_page.png`. Targets: `browser.verify`, `atlas.webproof`, `guard.browser.integrated`, `test.e99.browser.integrated`.

- **E100** ✅ PASS: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle — Tagproof bundle generator implemented and functional: aggregates TV coverage, gatekeeper coverage, regeneration receipts, browser verification, MCP DB RO guard. STRICT mode validation enabled in guard (dynamic components_total, required component logic). Bundle generation works, guard validates correctly in both HINT/STRICT modes. Artifacts: `evidence/tagproof_phase2_bundle.json`, `evidence/guard_tagproof_phase2.json`. Targets: `tagproof.phase2.ready` (via bundle script + guard).

**PLAN-090: Normalize Naming & Metrics (Pre-Implementation)** (✅ **Done**)
- ✅ DONE: Normalize DB objects and schema IDs — tables prefix `mcp_*`, MVs prefix `mv_mcp_*`, columns prefer `status` (not `state`), `created_at`/`updated_at` added where applicable, idempotent naming migration applied. Normalize JSON Schemas — `$id` prefix `gemantria://v1/...`, `title` present, top-level `type: "object"` and `additionalProperties: false` — enforced via `guard_schema_naming.py` (hermetic) + Makefile target `guard.schema.naming` covering all `*.schema.json` under `schemas/`. All active status columns now use `status`; a single unused optional `state` column on `mcp_agent_queue` is documented for future tool-bus work. Artifacts: `db/migrations/2025-11-guarded-calls-p0.naming.sql`, `scripts/ci/guard_schema_naming.py`, `schemas/graph-stats.schema.json`. Targets: `guard.schema.naming`.

**PLAN-091: Guarded Tool Calls P0 Execution** (✅ **Done**)
- ✅ E101: P0 jsonschema + PoR + TVs 01–05 + MCP adapter stub (referencing implemented files/targets)
- ✅ E102: Tagproof/Atlas wiring + MCP RO proof guard (dynamic components_total, STRICT mode enforcement)
- ✅ E103: Catalog integration into pm.snapshot + end-to-end TVs + tagproof evidence (read-only catalog access, TVs 06–07, bundle generation).

**PLAN-081: Orchestrator Dashboard Polish** ✅ **COMPLETE** (2025-11-21)
- ✅ E101: MCP RO Proof Tile & Browser-Verified Badge — Added "MCP RO Proof" tile component (`webui/orchestrator-shell/MCPROProofTile.tsx`) showing endpoint count, last tagproof timestamp, and individual proof statuses (E21-E24). Added Browser-Verified Badge component (`webui/orchestrator-shell/BrowserVerifiedBadge.tsx`) linking to browser verification screenshots with verified page count and screenshot count. Both components integrated into `OrchestratorOverview.tsx` (badge at top, tile in dedicated section). Components fetch data from `/exports/mcp/bundle_proof.json` and `/exports/evidence/webproof/report.json`. No backend changes; UI-only implementation with clean, semi-technical orchestrator aesthetic. Browser verification completed. Share synced. Quality gates passing.

**Phase-1 Control Plane: Guarded Tool Calls** ✅ **COMPLETE** (2025-11-21)
- ✅ PR-1: Control Plane DDL + Health Guard
- ✅ PR-2: Gatekeeper + PoR (TV-01)
- ✅ PR-3: Guard Shim + TVs 02–05
- ✅ PR-4: Atlas Compliance Export
- ✅ Governance + CI Wiring: STRICT/HINT mode support added to all control-plane guards (`guard_control_graph_compliance.py`, `guard_control_widgets.py`, `guard_biblescholar_reference.py`). Tag lanes (`ops.tagproof` Makefile target and `tagproof.yml` workflow) now enforce STRICT mode for control-plane exports/guards. All compliance exports linked in Atlas UI pages (compliance_summary.html, compliance_timeseries.html, compliance_heatmap.html, violations.html, guard_receipts.html). Atlas links validation passing (83 internal links, 0 broken).

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
- **6P**: BibleScholar Reference Answer Slice ✅ **COMPLETE** (2025-11-21)
  - Single E2E BibleScholar interaction using LM Studio (guarded) or ollama, bible_db (read-only), Gematria adapter, and optional knowledge slice
  - Inputs: Natural-language question + optional verse reference
  - Flow: Resolve verse context → Retrieve Gematria patterns → Perform LM Studio guarded call → Synthesize output with justification + trace
  - Outputs: `{ answer: str, trace: [...], context_used: {...} }`
  - Constraints: No new DSNs, must pass db_off hermetic mode, budget enforcement + provenance required
  - Dependencies: 6J, 6M, 6O, 6A, 6B, 6C (all COMPLETE)
  - **Control-plane export**: `scripts/db/control_biblescholar_reference_export.py` → `share/atlas/control_plane/biblescholar_reference.json` (tracks questions, answers, verse refs, metadata from `control.agent_run`)
  - **Guard**: `scripts/guards/guard_biblescholar_reference.py` validates export structure, schema, timestamp, and questions array
  - **Atlas viewer**: `docs/atlas/browser/biblescholar_reference.html` displays questions, answers, verse references, and metadata with search/filter
  - **Tests**: `agentpm/tests/atlas/test_phase6p_biblescholar_reference_guard.py` (5 tests, all passing)
  - **Make targets**: `control.biblescholar.reference.export`, `guard.biblescholar.reference`
  - See `docs/SSOT/BIBLESCHOLAR_REFERENCE_SLICE.md` for design details
- **6D**: Downstream app read-only wiring (StoryMaker + BibleScholar) ✅ **COMPLETE** (2025-11-21)
  - Control-plane widget adapters for graph compliance and BibleScholar reference exports
  - Adapter module: `agentpm/control_widgets/adapter.py` with `load_graph_compliance_widget_props()` and `load_biblescholar_reference_widget_props()`
  - Hermetic, fail-closed adapters (file-only, offline-safe defaults)
  - Status snapshot integration: `pmagent status snapshot` includes control_widgets summary
  - Guard: `scripts/guards/guard_control_widgets.py` validates adapter module and widget functions
  - Documentation: `docs/runbooks/PHASE_6D_DOWNSTREAM_INTEGRATION.md` with integration guide for StoryMaker and BibleScholar
  - Atlas pages updated with Phase-6D integration links
  - Tests: `agentpm/tests/control_widgets/test_adapter.py` (6 tests, all passing)
  - Make targets: `guard.control.widgets`
- **6E** ✅ PASS: Governance & SSOT Refresh — Reconciled governance docs, AGENTS files, and SSOT surfaces after Phase-7 work. Updated root `AGENTS.md` with planning lane runbook references (`docs/runbooks/GEMINI_CLI.md`, `docs/runbooks/CODEX_CLI.md`) and browser verification requirements (Rule-051 + Rule-067) in UI Generation and Cursor Execution Profile sections. Refreshed `RULES_INDEX.md` summaries for 050/051/052 with planning lane and browser verification details. All governance/runbook links verified. Validation checks (rules index, agents presence, share sync, ruff) all clean.

**Goal**: Move from "LM off" → controlled, observable usage & DB-backed knowledge.

### Phase-7: Runtime Bring-Up Completion (Planning)

- **7A** ✅ PASS: Control-Plane Bring-Up (Migration 040) — Applied `migrations/040_control_plane_schema.sql` via `python scripts/db/migrate_control.py` (idempotent), ran `STRICT_MODE=STRICT python scripts/guards/guard_control_plane_health.py`, captured `evidence/control_plane_smoke.json`, refreshed `share/atlas/control_plane/{schema_snapshot.json,mv_schema.json}` plus compliance exports, and re-verified Atlas guards (`guard_atlas_compliance_timeseries`, `guard_compliance_summary_backlinks`, `guard_browser_verification`). `share/atlas/control_plane/mcp_catalog.json` currently reports the `mcp_tool_catalog` view as missing (expected until view lands), and schema snapshot introspection still logs `operator does not exist: oid = text` warnings (documented for follow-up in 7B), but control-plane health + smoke tests are green and artifacts refreshed.
- **7B** ✅ PASS: LM Studio & Model Configuration Normalization — Canonicalized model-slot env vars and provider overrides in `env_example.txt` (per-slot providers, theology slot base/API key, `OLLAMA_ENABLED`) and documented them in *Prompting Guide for Our Core LLM models.md*. Added `THEOLOGY_LMSTUDIO_*` helpers plus reaffirmed Phase-7F routing contract via `scripts/config/env.py`. Resolved 7A follow-ups: `scripts/db/control_schema_snapshot.py` now casts `('control.' || table_name)::regclass` (no more `oid = text` warnings) and new helper SQL `scripts/db/sql/control_mcp_tool_catalog.sql` builds the `control.mcp_tool_catalog` view (consumed by `scripts/db/control_mcp_catalog_export.py`, which now reports `view_name` + OK status). `share/atlas/control_plane/{schema_snapshot.json,mcp_catalog.json}` refreshed with green evidence.
- **7C** ✅ PASS: Snapshot Integrity & Drift Review — Validated all snapshot/export artifacts (control-plane schema/MVs, ledger, pm snapshot, Atlas compliance artifacts, browser receipts) are consistent, drift-free, and covered by guards. Created `scripts/guards/guard_snapshot_drift.py` to validate snapshot file existence, structure, and ledger sync status. All snapshots refreshed: `share/atlas/control_plane/{schema_snapshot.json,mv_schema.json,mcp_catalog.json,compliance_summary.json,compliance_timeseries.json}`, `share/pm.snapshot.md`. Ledger verification shows all 9 tracked artifacts current. Guard outputs: `guard_control_plane_health` (STRICT), `guard_atlas_compliance_timeseries`, `guard_browser_verification`, `guard_snapshot_drift` all PASS. Evidence: `evidence/guard_snapshot_drift.json`.
- **7D** ✅ PASS: Runtime & Bring-Up UX Polish — Improved pmagent bringup/mcp UX for non-expert users through enhanced Reality Check messages (clearer component labels, user-friendly status indicators, helpful tips), refreshed browser verification receipts for all 7 required Atlas pages (compliance_summary, compliance_timeseries, compliance_heatmap, violations, guard_receipts), and updated `scripts/ci/atlas_webproof.sh` to generate screenshots and report entries for all dashboard pages. Browser verification guard now passes with all pages verified. Reality Check output now uses clearer labels ("Environment & Database Config", "Language Models & Services", etc.) and provides helpful tips for HINT vs STRICT modes.

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
- [x] E86: Compliance Summary Dashboard
- [x] E87: Violation Time-Series + Heatmaps
- [x] E88: Violation → Node & Pattern Drilldowns
- [x] E89: Unified Violation Browser
- [x] E90: Compliance Metrics in Graph Stats

**PLAN-078 Completion Criteria:** Phase-2 is done when all dashboards render correctly in browser verification, all charts link to correct JSON exports, violation browser functional with search/sort/filter, violation drilldowns render correctly + screenshots stable, all guards produce `ok=true`, tag lane STRICT validates all Atlas dashboards/webproofs/backlinks/screenshots/relevant JSON exports, tagproof bundle includes compliance dashboards/drilldowns/knowledge-MCP pages/screenshots/guard receipts with zero broken links. When complete → **Phase 2 is officially finished** → unlocks **Phase 3** (LM Studio + Knowledge Plane).

### PLAN-079: Guard Receipts, Screenshot Determinism, and Browser Validation
- [x] E91: Guard Receipts Index & Browser
- [x] E92: Screenshot Manifest Guard
- [x] E93: Browser Verification Guard
- [x] E94: Screenshot ↔ Tagproof Integration
- [x] E95: Atlas Links Integrity Sweep

### PLAN-080: Phase-1+2 Verification Sweep & Tagproof
- [x] E96: TV-01…TV-05 Re-Run & Coverage Receipt
- [x] E97: Gatekeeper / Guard Shim Coverage Audit
- [x] E98: Full Extraction & Atlas + Exports Regeneration
- [x] E99: Browser Verification & Screenshot Check (Integrated)
- [x] E100: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle ✅ PASS

### PLAN-081: Orchestrator Dashboard Polish
- [x] E101: MCP RO Proof Tile & Browser-Verified Badge ✅ PASS
- **Vision anchor**: Orchestrator dashboard UX and the non-technical orchestrator role are defined in `docs/SSOT/Orchestrator Dashboard - Vision.md`; PLAN‑081 and any future orchestrator UI work must keep that document as the north star for layout, tone, and interaction.

### Phase-1 Control Plane (Testing & Governance)
- ✅ **COMPLETE** — Superseded by "Phase-1 Control Plane: Guarded Tool Calls ✅ COMPLETE" section above (line 180). All governance wiring, STRICT/HINT mode support, and Atlas UI linkage completed.

### Medium-term (Q1 2026)
- [ ] Phase 12: Advanced Pattern Mining
- [ ] Phase 13: Multi-language Support
- [ ] Phase 14: Real-time Analytics
- [ ] Phase 15: API Gateway

### Long-term Vision
- **Chat-first Orchestrator Dashboard** — Conversation-driven dashboard experience for non-technical orchestrators, as defined in `docs/SSOT/Orchestrator Dashboard - Vision.md`.
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

> **Note:** “Next Milestone” indicates **future direction only**. Do **not** begin Phase 12 work until Phases 8–11 have passed both hermetic and live DB+LM runtime gates, and this document **and** `NEXT_STEPS.md` explicitly mark Phase 12 as **Active**.

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
| 069 | # Rule 069 — Always Use DMS First (Planning Queries) |
| 070 | # --- |
| 071 | # Rule 071 — Portable JSON is not Plan SSOT |
<!-- RULES_TABLE_END -->
