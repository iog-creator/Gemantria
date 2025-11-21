## [Unreleased]

- **AgentPM-Next PLAN-092 (M1–M4) — Complete**: KB registry-powered planning workflows implemented and shipped. M1: `pmagent plan kb` for prioritized documentation worklists. M2: `pmagent plan kb fix` for orchestrated doc-fix runs. M3: `pmagent report kb` for doc-health control loop & reporting. M4: `/status` page KB doc-health metrics visualization. CLI, API, and UI integration tested; browser verification setup complete; governance gates passed.
- **Phase-7 — Runtime Bring-Up Completion**: Planning initiated. Added planning section to MASTER_PLAN.md describing:
  - 7A control-plane bring-up (migration 040)
  - 7B LM Studio model configuration normalization
  - 7C snapshot integrity and drift review
  - 7D optional UX polish for bring-up tooling
- **Phase-6 — LM Studio Live Usage + DB-Backed Knowledge**: Planning started for enabling LM Studio live usage under guardrails and establishing Postgres as canonical knowledge spine.
- **Phase-6P — BibleScholar Reference Answer Slice**: Design doc added for single E2E BibleScholar interaction using LM Studio (guarded), bible_db (read-only), Gematria adapter, and optional knowledge slice. Planning-only PR; implementation to follow.

- **Phase-5 — StoryMaker & BibleScholar LM Integration**: LM indicator widget contract finalized; Gemantria adapter implemented; StoryMaker React tile and BibleScholar header badge added as hermetic consumers of `lm_indicator.json`.

- **Phase-4 — LM Insights & UI Polish** (PRs #536, #537, #538, #539, #540)
  - Implemented LM insights exports (`lm_insights_7d.json`) aggregating usage and health metrics (Phase-4A)
  - Enhanced LM status page UX with one-sentence status summary and friendly explanations (Phase-4B)
  - Added LM indicator export (`lm_indicator.json`) as canonical LM status signal for downstream apps (Phase-4C)
    - Status classification: offline (db_off/no_calls), degraded (error_rate>=0.2), healthy (error_rate<0.2)
    - Compact JSON format for StoryMaker, BibleScholar, and other consumer applications
  - Updated governance/docs to mark `lm_indicator.json` as canonical downstream signal (Phase-4D)
  - Key PRs: #536 (Phase-4 planning docs), #537 (LM insights exports, 4A), #538 (LM status UX polish, 4B), #539 (LM indicator export, 4C), #540 (governance/docs alignment, 4D)
- **Phase-3C/3D — LM Studio integration & observability** (PRs #532, #533, #534, #535)
  - Added LM Studio adapter + routing helper (`src/services/lm_routing_bridge.py`) and `pmagent health lm` command
  - Wired enrichment pipeline through `chat_completion_with_routing()` with control-plane logging
  - Added LM Studio setup runbook (`docs/runbooks/LM_STUDIO_SETUP.md`) and AGENTS documentation
  - Implemented LM metrics exports (`lm_usage_7d.json`, `lm_health_7d.json`) — db_off + LM-off safe
  - Added Atlas LM dashboards (usage + health configs) and HTML LM status page with Browser Verification (Rule-067)
  - Key PRs: #532 (LM Studio adapter + routing, P0), #533 (LM routing in enrichment + setup docs, P1b/P2), #534 (LM metrics exports, D1), #535 (LM dashboards + status page, D2/D3)
- PLAN-072 M2+: TVs E06–E10 implemented, tested, guarded (PR #499) — provenance logic complete with `ensure_provenance`, `guard_provenance`, `stamp_batch` functions, full test coverage, guard integration, and AGENTS.md documentation.
- PLAN-074 M14: Atlas UI tiles + guards (E66–E70 COMPLETE) — graph rollup metrics, node drilldowns, screenshot manifest, reranker badges, and webproof bundle backlinks with guards + receipts.
- PLAN-075 E71–E72: DSN centralization hardening + control-plane DDL — guard enforces centralized loader usage, control schema migration + schema snapshot artifact.
- PLAN-075 E73: Control-plane smoke script + evidence JSON — insert+select smoke test for control schema tables with DB-off tolerance.
- PLAN-075 E74–E75: Control-plane compliance MVs + Knowledge-MCP catalog stub — mv_compliance_7d/30d schema snapshot, control.mcp_tool_catalog view, and evidence JSON artifacts.
- Phase-3B Feature #4: pmagent health CLI (PR #524) — `pmagent health system|db|lm|graph` commands with DB-off hermetic behavior, JSON output, and Make targets.
- Phase-3B Feature #5: pmagent graph import + overview (PR #525) — `pmagent graph import` and `pmagent graph overview` commands with Postgres as source of truth for graph statistics.
- Phase-3B Feature #6: pmagent control status (PR #526) — `pmagent control status` command for control-plane database posture and table row counts.
- Phase-3B Feature #7: pmagent control tables (PR #527) — `pmagent control tables` command listing all schema-qualified tables with row counts.
- Phase-3B Feature #8: pmagent control schema (PR #528) — `pmagent control schema` command for DDL/schema introspection of control-plane tables (columns, primary keys, indexes).
- PLAN-076 E76–E78: Control-plane compliance exports — compliance.head, top_violations_7d, and top_violations_30d JSON exports with DB-off tolerance.
- PLAN-076 E79–E80: Control-plane compliance guard + webproof integration — guard validates compliance export JSONs, webproof page with backlinks to exports and guard verdict.
- PLAN-077 E81–E85: Knowledge-MCP surfacing — COMPLETE — read-only MCP catalog + capability/agent_run summaries with guards and Atlas webproof.
- PLAN-078 E86–E90: Compliance Dashboards & Violation Browser — *Planned* — Compliance summary dashboard, violation time-series & heatmaps, violation drilldowns, unified violation browser, compliance metrics in graph stats.
- PLAN-079 E91–E95: Guard Receipts, Screenshot Determinism, and Browser Validation — *Planned* — Guard receipts index & browser, screenshot manifest guard, browser verification guard, screenshot ↔ tagproof integration, Atlas links integrity sweep.
- PLAN-080 E96–E100: Phase-1+2 Verification Sweep & Tagproof — *Planned* — TV-01…TV-05 re-run & coverage receipt, gatekeeper/guard shim coverage audit, full extraction & Atlas + exports regeneration, browser verification & screenshot check (integrated), strict tag lane / tagproof "Phase-2 Ready" bundle.

- pmagent control summary (#530)
- pmagent control pipeline status (#529)
- pmagent control schema introspection (#528)
- pmagent control-plane status (#526)
- merge pmagent graph import + overview
- merge pmagent health CLI
- merge system health aggregate
- merge LM health guard + smoke
- merge DB-backed graph overview

- mark Phase-3D complete and add Phase-4 LM insights & UI polish (#536)
- LM metrics exports for Atlas (D1)

- enhance migration plan with schema-based analysis (primary input)
- add Knowledge Slice v0 schema and exports (6C) (#546)
- add LM usage budgets and 7d budget export (#545)
- enable LM Studio live usage behind flag (#544)
- add Phase-6 plan (LM Studio live usage + DB-backed knowledge) (#543)
- LM observability governance & indicator docs (4D) (#540)

- unified bring-up system (DB + LM Studio server+GUI + model loader)
- add reality-check CLI command integration
- automated Reality Check #1 bring-up script (#564)
- SSOT docs → DB → LM Studio Q&A pipeline (Reality Check #1) (#562)
- BibleScholar Reference Slice design doc + MASTER_PLAN update (#559)
- bible_db verse vector similarity (adapter + flow) (#557)
- bible_db read-only adapter + passage flow (#555)

- remove Granite model references from docs
- update env_example.txt with models that actually exist
- lm config normalization + model discovery + ops ledger v0
- LM Studio model configuration normalization
- add Phase-7 planning section

- add Postgres Control Plane & Governance Recording section to MASTER_PLAN
- use json.dumps() instead of psycopg.types.json.dumps() for JSONB inserts

- add kb_document registry, docs inventory, and duplicates report (#578)

- normalize book name handling and fix branch consistency

- KB registry M1–M6 (doc health, hints, status surfaces) (#579)

- add AgentPM-Next:M2 planning hook to MASTER_PLAN (PR #580)
- AgentPM-Next:M1 registry-powered planning (pmagent plan kb) (#580)

- ruff linting issues in share/ledger_*.py files

## [v0.0.8] - 2025-11-12

### Highlights

- **PLAN-073 complete:** Wrap-up receipts/guards E61–E65 (badges rollup, chip-id uniqueness, sitemap min, manifest consistency, stale sweep).

## [v0.0.3] - 2025-11-12

### Highlights

- **STRICT tag lane:** Added read-only MCP guard step (`make guard.mcp.db.ro STRICT_DB_PROBE=1`) proving `mcp.v_catalog` on tags.

- **Hermetic PRs:** No DB/network probes in PR CI; STRICT proofs run only in tagproof.

- **Governance:** Tool Bus remains **OFF** by default; Guarded Tool Calls P0 execution landed with TVs 01–05 green.

### Proofs (tagproof)

- RO guard executed successfully (see `share/releases/v0.0.3/tagproof/*`).

- Webproof artifacts mirrored when locally available.

## [v0.0.3] - 2025-11-12

### Highlights

- **STRICT tag lane:** Added read-only MCP guard step (`make guard.mcp.db.ro STRICT_DB_PROBE=1`) proving `mcp.v_catalog` on tags.

- **Hermetic PRs:** No DB/network probes in PR CI; STRICT proofs run only in tagproof.

- **Governance:** Tool Bus remains **OFF** by default; Guarded Tool Calls P0 execution landed with TVs 01–05 green.

### Proofs (tagproof)

- RO guard executed successfully (see `share/releases/v0.0.3/tagproof/*`).

- Webproof artifacts mirrored when locally available.
- TBD

2025-11-11 — v0.0.2: Browser Verification template (Rule-051/067) + STRICT webproof + DSN automation
2025-11-09 — ci: enforce xref badge presence on tags (STRICT_XREF_BADGES=1); add pip cache; require xref index on **release tags** (v*); main/PR remain HINT-only
2025-11-09 — ops: archive rc16 STRICT-tag (prod path) artifact; record in CHANGELOG; reset to fixtures default
2025-11-09 — ops: expand extraction truth-suite to 25 cases (fixtures path); add derive tool; guard prefers v2≥25
2025-11-09 — ops: archive rc17 STRICT-tag (fixtures) artifact; record in CHANGELOG
2025-11-09 — ops: promote extraction truth-suite to **v2** (≥25 cases); guard now prefers v2 when available
2025-11-09 — ops: archive rc18 STRICT-tag (fixtures, v2) artifact; record in CHANGELOG
2025-11-09 — ops: archive rc19 STRICT-tag (fixtures,v2,with HINT) + logs; record in CHANGELOG
2025-11-09 — ops: guard hardening — STRICT-on-tags requires **truth v2 ≥25** (HINT-only on main/PR)
2025-11-08 — ops: add xref coverage/rate badges (HINT-only) to operator dashboard; wire into `eval.package`
2025-11-08 — webui: xref a11y — ARIA for +N more; main landmark; smoke asserts [a251b135]
2025-11-08 — webui: xref UX polish — keyboard chips, Esc to close, focus trap, scroll-lock [468d2088]
2025-11-08 — OPS: UI xrefs index landed (HINT integrity guard) [fe7bded1]
2025-11-08 — OPS: Land light xref extractor (HINT guard; schema preserved) [8b23eaf4]
2025-11-08 — OPS: Lock 3-role DB contract; AI-tracking guard (HINT on PRs, STRICT gated by vars.STRICT_DB_MIRROR_CI) [6ddce6ee]
# Changelog

## v0.0.2 (2025-11-11)

### docs: Browser Verification template (Rule-051/067) + RFC-077
- Mandatory Browser Verification section in `GPT_SYSTEM_PROMPT.md` for all OPS OUTPUT blocks involving visual/web artifacts
- Template includes local server setup, browser navigation, screenshots, and `STRICT_WEBPROOF=1` hook
- Updated `RULES_INDEX.md` to mark Rule-067 as Always-Apply for `docs/atlas/*` edits
- Added browser verification evidence examples to EVIDENCE PLACEHOLDERS section
- Updated EXAMPLE section to show browser verification integrated into OPS OUTPUT block

### ci: STRICT webproof + DSN posture alignment (Rule-067)
- Aligned `tagproof.yml` workflow with STRICT webproof enforcement
- Added `STRICT_WEBPROOF=1` environment variable for release tags
- DSN secrets (`BIBLE_DB_DSN`, `GEMATRIA_DSN`) and variable (`ATLAS_DSN`) required for release tags
- PM Snapshot regeneration with DSNs on release tags (excludes RC tags)

### ops: DSN secrets automation
- Created `scripts/ops/sync_github_dsns.sh` to automatically sync local DSN values to GitHub repository variables and secrets
- Updated `docs/runbooks/DSN_SECRETS.md` to document `ATLAS_DSN` variable requirement
- All required DSN secrets/variables now set and verified for tagproof CI

### ops: Rule-067 webproof hardening
- Webproof now fails on Mermaid syntax errors (STRICT mode)
- Fixed `mcp_flow.mmd` diagram syntax errors
- Added Atlas webproof Make target and pre-push integration

### mcp: Atlas UI enhancements
- Atlas live fetch (dev server + viewer hook); offline-safe
- MCP catalog view with offline-safe guards
- Real read-only endpoints with safe fallbacks

## Unreleased

- ops: standardize Python runner to **python3** across Makefiles and scripts; re-prove STRICT triad + guards (PR #346)

## 2025-11-08 — Triad Enforcement Finalization

- Merge **PR #272**: lock Always-Apply triad to **050/051/052** only.
- Regenerate **RULES_INVENTORY** from `.cursor/rules/*.mdc`; add guard to **ops.verify**.
- Enforce **folder-scoped AGENTS.md** pattern; mirror to **share/**; tag **ops/agents-md-inventory-sync** to trigger STRICT agents-lint.

### ci: enforce RFC3339 on tag builds; add normalization step (PR #262)

## v0.1.0 — stable

- Fixtures-posture STRICT gate proven with **truth v2 ≥25** on tag (rc20); production-path STRICT re-proof captured (rc21).
- Attached tag guard artifact in the v0.1.0 Release (see assets); repo vars restored to fixtures default.
- Notes auto-generated per **RELEASES.md**; badges and CI validated on tag.

### v0.1.0 — CI verification

- STRICT tag workflow for **v0.1.0**: ✅ green (see run `19203434209`); artifact attached to Release.
- README badges checked; docs mirrored to `share/`.

## v0.1.1-dev — open

- Begin next development cycle under OPS triad (050/051/052). Fixtures posture by default; STRICT on tags remains enforced.

### ops: Atlas — evidence-driven status visualization

- New `make atlas.update` target generates Mermaid diagram from existing evidence files.
- Reads: `evidence/exports_guard.verdict.json`, `exports_rfc3339.verdict.json`, `guard_extraction_accuracy.json`, `xrefs_metrics.json`, `badges_manifest.json`, `share/eval/badges/exports_json.svg`.
- Outputs: `docs/atlas/status.mmd` with green/red/grey nodes and click-through links to evidence files.
- No DB/network dependencies; evidence-only visualization for OPS handoffs.

### ops: Atlas — telemetry-driven dashboard (browser-first, PR-safe)

- New browser-first Atlas dashboard at `docs/atlas/index.html` with vendored Mermaid (no CDN).
- Telemetry query layer (`scripts/atlas/telemetry_queries.py`) with read-only DB access, empty-DB tolerant.
- Diagram generator (`scripts/atlas/generate_atlas.py`) creates 7 diagram types:
  - `execution_live.mmd` - Currently executing pipelines
  - `pipeline_flow_historical.mmd` - Historical pipeline flow
  - `kpis.mmd` - Key performance indicators
  - `dependencies.mmd` - Module dependencies
  - `call_graph.mmd` - Function call relationships
  - `class_diagram.mmd` - UML class relationships
  - `knowledge_graph.mmd` - Semantic concept relationships
- Human-readable summaries (`.md` and `.html`) for each diagram in `docs/evidence/`.
- PR lane: Grey scaffolds when no DSN (no secrets, CI-safe).
- Tag lane: Populated from DB when `GEMATRIA_DSN` present.
- Makefile targets: `atlas.generate`, `atlas.live`, `atlas.historical`, `atlas.kpis`, `atlas.dependencies`, `atlas.calls`, `atlas.classes`, `atlas.knowledge`, `atlas.dashboard`, `atlas.all`, `atlas.test`, `atlas.serve`.
- Environment knobs: `ATLAS_WINDOW` (24h|7d), `ATLAS_MAX_ROWS` (500), `ATLAS_ENABLE_DEEP_SCAN` (0|1), `ATLAS_HIDE_MISSING` (0|1).
- Hermetic: Works without database (emits HINTs, never fails per Rule 046).

### ops: add exports JSON guard

- New guard verifies presence + JSON validity of core exports (HINT on main/PR; STRICT on tags).

### ops: exports guard — JSON-Schema validation

- Guard now validates exports against repo JSON Schemas (subset: type/required/properties/items/additionalProperties). HINT on main/PR; STRICT on tags.

### ops: exports JSON guard — rc1 evidence

- Tag **rc1** ran with exports JSON guard (STRICT); logs archived at `evidence/rc1_tag.log`.

### ops: exports JSON guard — rc2 (shape checks enforced)

- Tag **rc2** confirmed STRICT enforcement including minimal shape validation; logs archived at `evidence/rc2_tag.log`.

### v0.1.1-rc3 — fixtures tag with evidence badge

- Tag CI: **STRICT** green (exports JSON guard incl. shape checks).
- Release assets include: `exports_json.svg` badge, `badges_manifest.json`, and `guard_extraction_accuracy.json` (attached after CI).
- Logs archived at `evidence/v0.1.1-rc3_tag.log`.

### v0.1.1-rc5 — fixtures tag with machine-readable exports verdict

- Exports guard now emits `evidence/exports_guard.verdict.json` (HINT & STRICT).
- Evidence bundle includes verdict JSON for dashboards/release assets.
- Tag CI: STRICT green; artifact(s) archived to `evidence/`.

### v0.1.1-rc6 — fixtures tag with JSON-Schema PASS

- Export schemas committed under `schemas/`; guard now finds and validates all four exports.
- Tag CI: **STRICT** green with **schema_ok=✅**; verdict/badge/manifest archived in `evidence/`.

### v0.1.1-rc7 — fixtures tag post–required-tests

- Tag CI: **STRICT** green; `guard-tests` workflow runs on PRs (**advisory**; branch protection currently disabled).
- Release assets: guard artifact, exports verdict JSON, badge SVG, badges manifest.

> Note: Branch protection is OFF in this repository, so PR checks are not enforced by GitHub. Our Rule-051 posture applies: checks are advisory unless marked required in repo settings.

### v0.1.1-rc8 — fixtures tag with RFC3339 guard

- Tag CI: **STRICT** green; RFC3339 timestamp guard enforced on all exports.
- Release assets: guard artifact, exports verdict JSON, RFC3339 verdict JSON, badge SVG, badges manifest.

## v0.1.1 — stable

- JSON-Schema validation **PASS** for all four exports (see `schemas/`).
- Release assets: `exports_guard.verdict.json`, `exports_json.svg`, `badges_manifest.json`, and `guard_extraction_accuracy.json`.
- Posture held at fixtures (`STRICT_REAL_EXTRACTION=0`); STRICT remains enforced on tags.

## v0.1.1-dev — open

- Begin next development cycle under OPS triad (050/051/052). Fixtures posture by default; STRICT on tags remains enforced.

### tests: exports guard — schema-backed

- Added pytest covering HINT and STRICT (tag-sim) modes; asserts `schema_ok` for ai-nouns, graph, graph-stats, graph-patterns.

## [pre] v0.1.0-rc21 — tag STRICT (production path) proof

- Ran with `STRICT_REAL_EXTRACTION=1` and real extractor; STRICT guard passed on production path.
- **Run ID**: 19203400031 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true` with non-null totals).
- Posture restored to fixtures after proof.

## [pre] v0.1.0-rc20 — tag STRICT (fixtures) with **v2≥25 enforced**

- Hardened guard active on tag CI; fixtures path passed and HINT confirms `truth=v2`.
- **Run ID**: 19203390058 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`; totals may be null on fixtures).
- Posture: `STRICT_REAL_EXTRACTION=0`.

## [pre] v0.1.0-rc19 — tag-only STRICT (fixtures, v2) with guard HINT

- Guard now emits a **HINT** indicating which truth file/version is used; tag logs confirm `truth=v2`.
- **Run ID**: 19203349054 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`; totals may be null on fixtures path).
- Posture: `STRICT_REAL_EXTRACTION=0` (fixtures default).

## [pre] v0.1.0-rc18 — tag-only STRICT (fixtures, v2) proof

- Truth-suite **v2** (≥25 cases) preferred by guard; STRICT tag passed on fixtures path.
- **Run ID**: 19203322649 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`; totals may be null on fixtures path).
- Repo vars: default fixtures posture (`STRICT_REAL_EXTRACTION=0`).

## [pre] v0.1.0-rc17 — tag-only STRICT (fixtures path) proof

- Truth-suite expanded to **25** deterministic cases; STRICT guard passes on fixtures.
- **Run ID**: 19203285597 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`, fixtures posture).
- Repo vars: default fixtures posture (`STRICT_REAL_EXTRACTION=0`).

## [pre] v0.1.0-rc16 — tag-only STRICT (production path) proof

- Hardened tag workflow (fail-fast, preflight, grouped logs, always-upload) ran on **production path** via repo vars.
- **Run ID**: 19203122465 · **Verdict**: `ok:true`, totals `{"cases":10,"correct":10}` (artifact: `evidence/guard_extraction_accuracy.json`).
- Repo vars at proof time: `STRICT_REAL_EXTRACTION=1`, `REAL_EXTRACT_CMD="python3 scripts/analytics/build_graph_from_repo_fixtures.py"`.

## v0.1.0-rc1

- Phases 1–3 merged under reuse-first (schemas, pipeline, exports)
- Phase 4 adapters for Web UI (no new components)
- Phase 5 quality gates: reranker adapter + thresholds smoke
- Phase 6 CLI: Typer wrapper + quickstart

### Fixes

- **Confidence validator threshold**: Now runtime (env-respected); default lowered to **0.80** (uniform 0.85 artifact). See `AGENTS.md#environment`.

## [v0.0.7] - 2025-11-12

### Highlights
- PLAN-073 M12: index summary receipt, chip coverage guard, trace badge, roundtrip guard, manifest linkage (E56–E60 PASS).

### Proofs
- STRICT tagproof (RO-DSN MCP guard + Webproof) expected on CI for v0.0.7.

## [v0.0.8] - 2025-11-12

### Highlights
- PLAN-073 complete: wrap-up receipts/guards E61–E65 (badges rollup, chip-id uniqueness, sitemap min, manifest consistency, stale sweep).

### Proofs
- STRICT tagproof (RO-DSN MCP guard + Webproof) on tag.
