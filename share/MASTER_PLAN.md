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

### Active Development Workstreams

**PLAN-072: Extraction Agents Correctness & Resume Docs Management** (📋 **Planned**)
- **M1** ⏳ PENDING: DMS guard fixes — ensure documentation management guards are hermetic and pass in CI.
- **M2+** ✅ PASS: Extraction agents provenance (TVs E06–E10) — implemented provenance logic (`ensure_provenance`, `guard_provenance`, `stamp_batch`) with full test coverage, guard integration, and AGENTS.md documentation. All 5 TVs (E06–E10) implemented, tested, guarded (PR #499). Artifacts: `agentpm/extractors/provenance.py`, `agentpm/tests/extractors/test_extraction_provenance_e06_e10.py`, `agentpm/extractors/AGENTS.md`, `scripts/ci/guard_extraction_agents.py`. Targets: `guard.extractors`.
- **M2** ⏳ PENDING: Extraction agents correctness — define TVs for extraction correctness (TV-E01..E05) with golden fixtures, add hermetic guard `guard_extraction_agents.py` (no DB/network), wire pytest collection under `agentpm/tests/extractors/` (unit-only). Artifacts: `agentpm/tests/extractors/test_extraction_correctness.py`, `agentpm/tests/extractors/fixtures/*.json`, `scripts/ci/guard_extraction_agents.py`. Targets: `guard.extractors`.
- **M3** ⏳ PENDING: Visualization hooks — wire extraction outputs to visualization components, ensure data flows correctly from extraction → visualization, add visual verification (browser tools) for rendered outputs.

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
