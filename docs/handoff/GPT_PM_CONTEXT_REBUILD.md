# GPT PM Context Rebuild — Complete Project Summary

**Generated**: 2025-11-13  
**Purpose**: Complete context handoff for GPT PM after data loss  
**Status**: Current as of PLAN-077 completion, PLAN-078/079/080 planned

---

## 1. What Is Gemantria?

**Gemantria** is a deterministic, schema-first AI pipeline that transforms Hebrew biblical text into structured semantic graph insights. It uses a hybrid approach:

- **LLM Agents**: Perform semantic enrichment and theological analysis
- **Deterministic Operators**: Handle gematria calculations, verse lookups, and data validation
- **Database Integration**: PostgreSQL with vector extensions for storage and retrieval
- **LangGraph Orchestration**: Stateful, resumable pipeline with checkpoints

### Core Mission

Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and visualization-ready artifacts, with self-healing guards and governance.

### Key Principles

1. **Correctness**: Code gematria > bible_db > LLM (LLM = metadata only)
2. **Determinism**: content_hash identity; uuidv7 surrogate; fixed seeds; position_index
3. **Safety**: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns

---

## 2. Where We've Been (Recent History)

### Phase Completion Status

All core development phases (0-11) are **COMPLETE**:

- ✅ **Phase 0**: Governance v6.2.3, internal guardrails active
- ✅ **Phase 1**: Data Layer (DB foundation)
- ✅ **Phase 2**: Pipeline Core (LangGraph)
- ✅ **Phase 3**: Exports & Badges
- ✅ **Phase 5**: UI Polish
- ✅ **Phase 8**: Temporal Analytics Suite (rolling windows + forecasts + visualization)
- ✅ **Phase 9**: Graph Latest with Node/Edge Exports
- ✅ **Phase 10**: Correlation Visualization + Pattern Analytics
- ✅ **Phase 11**: Unified Envelope (100k nodes, COMPASS validation)

### Recent Completed Plans (PLAN-074 through PLAN-077)

**PLAN-074 (M14): Atlas UI Tiles + Guards** ✅ COMPLETE
- E66-E70: Graph rollup metrics, node drilldowns, screenshot manifest, reranker badges, webproof bundle backlinks
- All episodes passed with guards and receipts

**PLAN-075: DSN Centralization + Control Plane** ✅ COMPLETE
- E71-E72: DSN centralization hardening + control-plane DDL
- E73: Control-plane smoke script with DB-off tolerance
- E74-E75: Compliance MVs + Knowledge-MCP catalog stub

**PLAN-076: Control-Plane Compliance Exports** ✅ COMPLETE
- E76-E78: Compliance exports (compliance.head, top_violations_7d, top_violations_30d)
- E79-E80: Compliance guard + webproof integration

**PLAN-077: Knowledge-MCP Surfacing** ✅ COMPLETE
- E81: MCP catalog export (`mcp_catalog.json`)
- E82: Capability rules export (`capability_rules.json`)
- E83: Agent runs 7d export (`agent_runs_7d.json`)
- E84: Guard for Knowledge-MCP exports
- E85: Atlas/Knowledge-MCP webproof page with backlinks

### Current Release

**v0.0.8** (2025-11-12) — Production operations with all core phases complete.

---

## 3. Why We're Doing This

### The Problem

Hebrew biblical text contains rich semantic relationships that traditional analysis methods miss. Gematria (numerical values of Hebrew letters) reveals hidden patterns, but manual analysis is:
- Time-consuming and error-prone
- Difficult to scale across entire books
- Hard to visualize and explore

### The Solution

Gemantria automates the entire pipeline:
1. **Extract** nouns from Hebrew text (AI-powered discovery)
2. **Enrich** with theological context and gematria calculations
3. **Build** semantic graphs showing relationships
4. **Analyze** patterns, correlations, and temporal trends
5. **Visualize** through Atlas dashboards and interactive UIs

### Key Benefits

- **Deterministic**: Same input → same output (critical for research)
- **Resumable**: Pipeline can pause/resume at any point
- **Verified**: COMPASS mathematical validation ensures correctness
- **Governed**: Self-healing guards and compliance tracking
- **Scalable**: Handles 100k+ nodes with performance gates

---

## 4. Where We're Going (Current Plans)

### Phase-2 Control Plane: Compliance & Governance

We're currently in **Phase-2** of the Control Plane work, focusing on compliance dashboards and governance tooling.

### Active Plans (PLAN-078 through PLAN-080)

**PLAN-078: Compliance Dashboards & Violation Browser** 📋 PLANNED
- **E86**: Compliance Summary Dashboard (tiles, metrics, violations by tool/code/ring)
- **E87**: Violation Time-Series & Heatmaps (visualization pages)
- **E88**: Violation → Node & Pattern Drilldowns (HTML pages per violation)
- **E89**: Unified Violation Browser (search/filter UI)
- **E90**: Compliance Metrics in Graph Stats (integration into graph stats)

**PLAN-079: Guard Receipts, Screenshot Determinism, and Browser Validation** 📋 PLANNED
- **E91**: Guard Receipts Index & Browser
- **E92**: Screenshot Manifest Guard (deterministic screenshots)
- **E93**: Browser Verification Guard (automated page verification)
- **E94**: Screenshot ↔ Tagproof Integration
- **E95**: Atlas Links Integrity Sweep

**PLAN-080: Phase-1+2 Verification Sweep & Tagproof** 📋 PLANNED
- **E96**: TV-01…TV-05 Re-Run & Coverage Receipt
- **E97**: Gatekeeper / Guard Shim Coverage Audit
- **E98**: Full Extraction & Atlas + Exports Regeneration
- **E99**: Browser Verification & Screenshot Check (Integrated)
- **E100**: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle

**Completion Criteria**: Phase-2 is done when all dashboards render correctly in browser verification, all charts link to correct JSON exports, violation browser functional with search/sort/filter, violation drilldowns render correctly + screenshots stable, all guards produce `ok=true`, tag lane STRICT validates all Atlas dashboards/webproofs/backlinks/screenshots/relevant JSON exports, tagproof bundle includes compliance dashboards/drilldowns/knowledge-MCP pages/screenshots/guard receipts with zero broken links.

**When Phase-2 is complete** → **Phase 3** unlocks (LM Studio + Knowledge Plane).

### Future Plans (Renumbered)

- **PLAN-090**: Normalize Naming & Metrics (Pre-Implementation)
- **PLAN-091**: Guarded Tool Calls P0 Execution
- **PLAN-081**: Orchestrator Dashboard Polish

---

## 5. Key Operational Context for GPT PM

### Governance Framework (Always-Apply Triad)

Three rules are **always active** and must be referenced in all operations:

1. **Rule-050 (LOUD FAIL)**: Strict activation + SSOT checks
   - Every operation must verify repo presence, governance docs, and quality SSOT
   - Emit LOUD FAIL if any required tool/context is missing

2. **Rule-051 (CI Gating)**: Required-checks/CI gating posture
   - Non-required automated reviews are **advisory only**
   - Merges honor required checks only
   - Browser verification **mandatory** for visual/web content

3. **Rule-052 (Tool Priority)**: Tool-priority (local+gh → codex → gemini/mcp)
   - Use local tools first (git, make, gh pr)
   - Fallback to codex if available
   - Use gemini/mcp for long governance files

### Response Format (4-Block Standard)

Every PM reply must contain:

1. **Goal** — One sentence defining the action
2. **Commands** — Runnable shell/gh/make lines only
3. **Evidence to return** — Numbered list of expected outputs
4. **Next gate** — What to do after evidence is seen

### Key Files & Directories

**SSOT Documentation** (`docs/SSOT/`):
- `MASTER_PLAN.md` — Complete project roadmap (27K)
- `AGENTS.md` — Agent framework and contracts
- `RULES_INDEX.md` — All 69 governance rules
- `GPT_SYSTEM_PROMPT.md` — PM operating contract (11K)
- `GPT_REFERENCE_GUIDE.md` — GPT file reference guide (5.7K)

**Share Directory** (`share/`):
- Mirrored artifacts for external consumption
- 25 files total (under GPT's 22-file limit for curated set)
- Synced via `make share.sync`

**Evidence Directory** (`evidence/`):
- Guard verdicts, receipts, screenshots
- Governance hints, compliance reports
- Browser verification artifacts

### Database Architecture

**Three-Role DB Contract**:
- **Extraction DB**: `GEMATRIA_DSN` → database `gematria` (read/write)
- **SSOT DB**: `BIBLE_DB_DSN` → database `bible_db` (read-only)
- **AI Tracking**: Lives in `gematria` DB, `public` schema

**DSN Access**: All DSN access must go through centralized loaders:
- **Preferred**: `scripts.config.env` (`get_rw_dsn()`, `get_ro_dsn()`, `get_bible_db_dsn()`)
- **Legacy**: `src.gemantria.dsn` (`dsn_rw()`, `dsn_ro()`, `dsn_atlas()`)
- **Never**: Direct `os.getenv("GEMATRIA_DSN")` — enforced by guards

### Hermetic Behavior (Rule-046)

Scripts must handle missing/unavailable databases gracefully:
- DB-dependent operations check availability first
- Emit HINTs (not errors) when DB unavailable
- Housekeeping passes even when DB unavailable
- Per AGENTS.md: "If DB/services down → 'correct hermetic behavior.'"

### Quality Gates

**SSOT for Quality**: `ruff format --check . && ruff check .`
- If ruff fails → stop and request last 60–200 lines

**Hermetic Test Bundle**:
- `make book.smoke`
- `make eval.graph.calibrate.adv`
- `make ci.exports.smoke`
- If DB/services down → "correct hermetic behavior"

**Housekeeping** (Rule-058): **MANDATORY** after every change
- `make housekeeping` must run after any docs/scripts/rules change
- Includes: share sync, governance audit, rules audit, forest regen, evidence archiving

### Episode Numbering

Episodes are globally sequential:
- E1-E85: Used in PLAN-074 through PLAN-077
- E86-E90: PLAN-078 (Compliance Dashboards)
- E91-E95: PLAN-079 (Guard Receipts & Browser Validation)
- E96-E100: PLAN-080 (Verification Sweep & Tagproof)

### Plan Numbering

Plans are sequential with some renumbering:
- PLAN-072: Extraction Agents Correctness
- PLAN-073: MCP Strict DB Live (Complete)
- PLAN-074-077: Complete
- PLAN-078-080: Current Phase-2 plans
- PLAN-081: Orchestrator Dashboard Polish
- PLAN-090-091: Renumbered from old PLAN-079/080

---

## 6. Critical Workflows

### Standard PR Workflow

1. Branch `feature/<short>` → write tests first
2. Code → `make lint type test.unit test.int coverage.report`
3. Commit → push → PR
4. Coverage ≥98%
5. Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`
6. PR: Goal, Files, Tests, Acceptance
7. **MANDATORY**: Update `AGENTS.md` files when code changes (Rule 006, Rule 027)
8. **MANDATORY**: Run `make housekeeping` after any docs/scripts/rules change (Rule 058)

### Browser Verification (Rule-051 + Rule-067)

**MANDATORY** when OPS OUTPUT involves:
- Web pages / HTML / docs site
- UI components, dashboards, charts, Mermaid diagrams
- GitHub Pages or any web-based outputs
- Visual layout, CSS, rendering, or navigation/links

**Process**:
1. Use standardized script: `bash scripts/ops/browser_verify.sh --strict --port 8778`
2. Or manual: Start HTTP server, navigate with browser tools, capture screenshots
3. Verify all expected content is visible
4. Save screenshots to `evidence/` directory

### Share Sync (Rule-030)

Always sync share directory after changes:
- `make share.sync` updates `share/` with latest artifacts
- 25 files total (curated set for GPT consumption)
- Must stay in sync with source files

---

## 7. Key Make Targets

**Core Operations**:
- `make housekeeping` — Complete housekeeping (Rule-058, MANDATORY)
- `make share.sync` — Sync share directory (Rule-030)
- `make bringup.001` — STRICT bring-up verification
- `make dsns.echo` — Print redacted DSNs (operator sanity check)

**Quality Checks**:
- `make lint` — Ruff format + check
- `make type` — MyPy type checking
- `make test.unit` — Unit tests
- `make test.int` — Integration tests
- `make coverage.report` — Coverage report (target ≥98%)

**Guards**:
- `make guards.all` — Run all guards
- `make guard.atlas.compliance.summary` — Compliance summary guard
- `make guard.browser.verification` — Browser verification guard

**Exports**:
- `make control.mcp.catalog.export` — MCP catalog export
- `make control.capability.rules.export` — Capability rules export
- `make control.agent_runs_7d.export` — Agent runs 7d export

---

## 8. Important Notes for GPT PM

### What NOT to Do

- ❌ Never use `os.getenv("GEMATRIA_DSN")` directly — use centralized loaders
- ❌ Never skip `make housekeeping` after changes (Rule-058)
- ❌ Never skip browser verification for visual/web content (Rule-051)
- ❌ Never commit without running ruff checks first
- ❌ Never assume DB is available — scripts must be hermetic (Rule-046)

### What TO Do

- ✅ Always use centralized DSN loaders
- ✅ Always run `make housekeeping` after changes
- ✅ Always verify browser rendering for web content
- ✅ Always follow 4-block response format (Goal, Commands, Evidence, Next gate)
- ✅ Always check Rule-062 environment validation
- ✅ Always emit LOUD FAIL if required tools/context missing
- ✅ Always treat non-required automated reviews as advisory only

### When in Doubt

1. Check `docs/SSOT/MASTER_PLAN.md` for current plans
2. Check `docs/SSOT/AGENTS.md` for operational contracts
3. Check `docs/SSOT/RULES_INDEX.md` for governance rules
4. Check `docs/SSOT/GPT_SYSTEM_PROMPT.md` for PM operating contract
5. Run `make housekeeping` to verify current state
6. Check `evidence/governance_docs_hints.json` for recent changes

---

## 9. Current State Summary

**Status**: Production operations with Phase-2 Control Plane work in progress

**Completed**: All core phases (0-11), PLAN-074 through PLAN-077

**In Progress**: PLAN-078 (Compliance Dashboards), PLAN-079 (Guard Receipts), PLAN-080 (Verification Sweep)

**Next Milestone**: Complete Phase-2 → Unlock Phase-3 (LM Studio + Knowledge Plane)

**Governance**: OPS Contract v6.2.3 active, Always-Apply Triad (050/051/052) enforced

**Quality**: All checks passing, hermetic behavior verified, share directory synced

---

## 10. Quick Reference

**Key Commands**:
```bash
# Housekeeping (MANDATORY after changes)
make housekeeping

# Share sync
make share.sync

# Quality checks
ruff format --check . && ruff check .

# Browser verification (when needed)
bash scripts/ops/browser_verify.sh --strict --port 8778

# DSN sanity check
make dsns.echo
```

**Key Files**:
- `docs/SSOT/MASTER_PLAN.md` — Project roadmap
- `docs/SSOT/AGENTS.md` — Agent contracts
- `docs/SSOT/GPT_SYSTEM_PROMPT.md` — PM operating contract
- `CHANGELOG.md` — Version history
- `evidence/governance_docs_hints.json` — Recent changes

**Key Rules**:
- Rule-050: LOUD FAIL (activation + SSOT)
- Rule-051: CI gating + browser verification
- Rule-052: Tool priority
- Rule-058: Housekeeping mandatory
- Rule-062: Environment validation

---

**End of Context Rebuild Document**

For detailed information, see:
- `docs/SSOT/MASTER_PLAN.md` — Complete project plan
- `docs/SSOT/GPT_SYSTEM_PROMPT.md` — PM operating contract
- `docs/SSOT/AGENTS.md` — Agent framework
- `README.md` — Project overview

