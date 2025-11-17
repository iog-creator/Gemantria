# Phase-7 Governance Drift Map

> Branch: feat/phase7.governance.rebuild.20251116-085215  
> Scope: Governance-only reconstruction (no UI, no new adapters, no LM routing)  
> Status: Draft v0.1 — docs-only, DB offline (db_off posture)

---

## 1. Sources of Governance Truth — As Designed

From MASTER_PLAN, AGENTS.md, RULES_INDEX, and SSOT docs:

- **RULES_INDEX.md**
  - Canonical index of rules 000–068 (contiguous, no gaps).
  - Always-Apply Triad: Rule-050 (OPS contract), Rule-051 (CI gating), Rule-052 (tool priority).
  - Intended as the human-readable index of governance.  

- **Root AGENTS.md**
  - Defines:
    - Mission and priorities (correctness > determinism > safety).
    - 3-role DB contract (GEMATRIA_DSN, BIBLE_DB_DSN, AI tracking in `public.ai_interactions` / `public.governance_artifacts`).
    - DSN centralization via loaders (`scripts.config.env`, `src.gemantria.dsn`).
    - OPS contract v6.2 (Goal / Commands / Evidence / Next gate).
  - States that SSOT is in-repo (`.cursor/rules/*.mdc`) **for now**, with the intent of stronger governance later.

- **MASTER_PLAN.md**
  - Declares phases for:
    - DSN centralization + control-plane DDL (PLAN-075).
    - Control-plane compliance exports + webproof (PLAN-076).
    - Knowledge-MCP surfacing (PLAN-077).
    - Phase-7 runtime bring-up planning (control-plane bring-up, LM config normalization, snapshot integrity).
  - Treats Postgres control-plane as the long-term governance backbone (compliance MVs, Knowledge-MCP, receipts).

- **SSOT Schemas and Runbooks**
  - `docs/SSOT/*.schema.json` define graph, stats, and patterns contracts.
  - DB Health runbook defines DB modes `ready`, `db_off`, `partial` and expects hermetic behavior when DB is down.
  - LM/DB usage patterns reference centralized loaders and Postgres as canonical knowledge spine.

- **Control-Plane (Conceptual)**
  - `control` schema: compliance MVs, MCP catalog, agent_run summaries.
  - AI tracking tables in `public` (ai_interactions, governance_artifacts).
  - Compliance exports mirrored to `share/atlas/control_plane/*.json` for dashboards and guards.

---

## 2. Sources of Governance Truth — As Implemented Today

Based on OPS-001/002 evidence:

- **.cursor/rules/*.mdc**
  - 69 rule files (000–068) + README.
  - Rules numbering is contiguous and passes rules_guard.
  - Contains many governance policies (PR workflow, GitHub operations, docs sync, visualization contracts, etc.).
  - Operates as the **de facto SSOT** for Cursor behavior.

- **RULES_INDEX.md + AGENTS.md**
  - Snapshots show:
    - Rules index matches `.cursor/rules` numerically (no gaps).
    - AGENTS.md documents DSN centralization, OPS contract, LM control, and Phase-7F local LM architecture.
  - However, they **do not yet push rules into Postgres**; they live as docs, not DB truth.

- **Postgres Control-Plane**
  - `pmagent control *` commands currently report `mode=db_off` (DB not running in this analysis session).
  - Expected tables (based on code + docs) include:
    - `public.ai_interactions`
    - `public.governance_artifacts`
    - `control.agent_run`
    - `control.tool_catalog`
    - `gematria.graph_stats_snapshots`
  - Control-plane is implemented in migrations, but we have **no online DB evidence** in this session.

- **Compliance & Knowledge-MCP Exports**
  - MASTER_PLAN/CHANGELOG list:
    - `compliance.head.json`
    - `top_violations_7d.json`
    - `top_violations_30d.json`
    - `mcp_catalog.json`
    - `capability_rules.json`
    - `agent_runs_7d.json`
  - These exports summarize violations and agent activity but **derive from DB state**, not from the rules docs themselves.

- **PM Snapshot + DSN Posture**
  - `make pm.snapshot` shows:
    - DSNs configured at least for GEMATRIA and BIBLE.
    - DB health mode `error` (not one of `ready/db_off/partial`).
    - Share manifest count 37 (docs claim canonical 25-file manifest).

---

## 3. Drift Findings

### 3.1 Rules SSOT vs `.cursor/rules`

**What matches:**
- Rule IDs 000–068 exist and are contiguous in both RULES_INDEX and `.cursor/rules`.
- Always-Apply triad (050/051/052) is present, documented, and active in both places.

**Drift:**
- **Location of SSOT**:
  - As-designed, governance was meant to move toward a Postgres-backed control-plane (phases 3B, 6, 7).
  - As-implemented, `.cursor/rules` remain the **operational SSOT**; Postgres only tracks effects (violations, runs), not rule definitions.
- **Cursor-only semantics**:
  - Some rules encode behavior tied specifically to Cursor's runtime (e.g., how it prints evidence, how it chooses tools).
  - These semantics are not mirrored into DB tables, so governance in DB cannot reason about them.

**Conclusion:**  
The **rules content** is mostly consistent; the **rules authority** is not. SSOT for rules is still in `.cursor/rules`, not in Postgres.

---

### 3.2 Docs vs DB (Control-Plane)

**What docs say:**
- Control-plane schema under `control` plus AI tracking tables are the backbone for:
  - Guard receipts.
  - Compliance metrics.
  - Knowledge-MCP catalog.
- DB Health runbook expects modes `ready`, `db_off`, `partial`, and tolerates DB-off scenarios hermetically.
- MASTER_PLAN and CHANGELOG assert that DSN centralization and control-plane migrations have landed.

**What evidence shows in this session:**
- DB is offline (`db_off`/`error` posture) — expected for our analysis, but it means:
  - We cannot confirm whether all control-plane tables actually exist in the live DB.
  - We cannot confirm whether violations, guards, and agent runs are populated as designed.
- `pmagent control status` reports all tracked tables as `present=false` with `row_count=null` (because connection failed, not necessarily because tables don't exist).

**Concrete drift patterns (design vs observed session):**
- **Behavioral drift**:
  - PM snapshot reports `DB_HEALTH_MODE=error` instead of runbook's `db_off/partial/ready` triad.
- **Authority drift**:
  - Control-plane records compliance data but is **not driving** governance decisions (rule enable/disable, strict/hint per rule, etc.).
  - Governance decisions remain embedded in `.cursor/rules` and CI workflows rather than a unified DB schema.

**Conclusion:**  
Control-plane is *implemented* but not yet the **primary governance SSOT**. It is used for telemetry, not for rules ownership.

---

### 3.3 AGENTS.md vs Actual Workflows / CI

**AGENTS.md promises:**
- DSN centralization (`scripts.config.env` + `src.gemantria.dsn`), never `os.getenv` directly.
- 3-role DB contract and AI tracking in Postgres.
- OPS contract v6.2 with baseline evidence commands (ruff, book.smoke, eval.calibrate.adv, ci.exports.smoke).
- `make pm.snapshot` + `make share.manifest.verify` as part of governance health.

**Evidence:**
- `rules_guard` passes Rule-017 (AGENTS presence) and Rule-054 (reuse-first), so the file *exists* and is referenced.
- `pm.snapshot` reveals:
  - Manifest count drift (37 vs canonical 25).
  - DB health in `error` mode.
- CI workflows exist for SSOT, rules, DB bootstrap, and exports, but:
  - Some governance steps (like Phase-7 bring-up and strict DSN enforcement) are still planned or partially implemented.

**Conclusion:**  
AGENTS.md is descriptive and aspirational in some areas. CI and runtime behavior partially honor it, but there is **no single enforcement bridge** from AGENTS → DB → CI. That bridge is what Phase-7 governance must restore.

---

### 3.4 TVs & Tags (Planned vs Enforced)

**Planned / documented:**
- PLAN-072/073/076/077 describe TVs (test vectors) and tag lanes (STRICT tag lane, tagproof bundles).
- TVs E06–E10 for extraction provenance are implemented with guards and tests.
- STRICT tag lane proofs (v0.0.3) demonstrate tag-based STRICT behavior in tag builds.

**Current posture (from evidence + your observation):**
- TVs and tags are no longer felt as **active levers**:
  - TVs are implemented but not surfaced in a way you can easily see or run as a "governance dashboard".
  - Tag-based STRICT lanes are present but effectively invisible to day-to-day development.
- There is no unified TV/Tag browser in Atlas or a simple CLI aggregator to answer:
  - "Which TVs are defined?"
  - "Which tags are currently enforcing STRICT?"

**Conclusion:**  
TVs/Tags exist in code and some CI, but governance *experience* is broken: they are not discoverable, not visible, and not clearly wired into Phase-7 bring-up.

---

## 4. Postgres Governance Resurrection Plan

The goal is to make **Postgres + SSOT docs** the true governance SSOT, and treat `.cursor/rules` as a generated mirror.

### 4.1 Target Governance Schema (Conceptual)

We will define (or confirm) the following conceptual tables/views in the `control` schema:

1. **control.rule_definition**
   - One row per rule_id (000–068).
   - Fields: rule_id, name, status (active/deprecated/reserved), description, severity, docs_path.

2. **control.rule_source**
   - Mapping of rule → source artifacts.
   - Fields: rule_id, source_type (cursor_rules, rules_index, agents_md, ci_workflow), path, content_hash.

3. **control.guard_definition**
   - Guards and their linkage to rules.
   - Fields: guard_id, name, description, rule_ids[], strict_default (HINT/STRICT).

4. **control.guard_run / control.guard_violation**
   - Already partially implemented as compliance exports; we will align with existing control-plane MVs.
   - Fields: guard_id, run_id, status, violations[], evidence_path.

5. **control.tv_definition / control.tag_definition / control.tag_binding**
   - TVs: id, description, scope (extraction, LM, UI), status.
   - Tags: name, description, strict_posture, CI usage.
   - Bindings: which TVs/guards/tags apply to which components (modules, workflows, make targets).

6. **Views for Atlas / MCP**
   - Read-only views that surface:
     - Rules catalogue.
     - Guard catalogue.
     - TV/Tag catalogue.
     - Violation summaries and coverage.

### 4.2 Ingestion Pipeline

New or updated scripts (names illustrative):

1. **`scripts/ingest_rules_to_control.py`**
   - Reads:
     - `docs/SSOT/RULES_INDEX.md`
     - `AGENTS.md`
     - `.cursor/rules/*.mdc`
   - Populates:
     - `control.rule_definition`
     - `control.rule_source`

2. **`scripts/ingest_tv_tags_to_control.py`**
   - Reads:
     - MASTER_PLAN (TV/Tag definitions).
     - Existing guard scripts and CI workflows.
   - Populates:
     - `control.tv_definition`
     - `control.tag_definition`
     - `control.tag_binding`

3. **Integration with Existing Exports**
   - Align existing compliance and MCP exports so that:
     - Every violation/receipt references `control.rule_definition.rule_id`.
     - Atlas dashboards pull from DB-backed views, not ad-hoc JSON.

### 4.3 Migration / Backfill Strategy

1. **Schema-first (no behavior change)**
   - Add governance tables/views under `control` with migrations.
   - Keep `.cursor/rules` and CI behavior unchanged initially.

2. **Backfill from existing artifacts**
   - Ingest current RULES_INDEX + `.cursor/rules` snapshots.
   - Backfill guard runs and violations from:
     - `share/atlas/control_plane/compliance.head.json`
     - `top_violations_7d.json`, `top_violations_30d.json`
     - Guard receipts already generated in `evidence/`.

3. **TV/Tag mapping**
   - From MASTER_PLAN and CHANGELOG, enumerate TVs and tags.
   - Backfill `control.tv_definition` and `control.tag_definition` with current state.

4. **Verification**
   - Guards to ensure:
     - Every rule in RULES_INDEX has a `control.rule_definition` row.
     - Every `.cursor/rules/*.mdc` rule maps to a DB row (or is explicitly deprecated).
     - Every TV/tag documented in MASTER_PLAN maps to a DB entry.

### 4.4 Decommissioning `.cursor/rules` as Primary SSOT

1. **Generate `.cursor/rules` from DB**
   - New script: `scripts/generate_cursor_rules_from_control.py`.
   - Renders `.cursor/rules/*.mdc` from:
     - `control.rule_definition`
     - `control.rule_source` (doc pointers)
   - Enforces single direction: DB → `.cursor/rules`, not the other way around.

2. **Update governance docs**
   - Update AGENTS.md and RULES_INDEX to state:
     - Postgres control-plane is the canonical rules SSOT.
     - `.cursor/rules` is a generated mirror for Cursor's consumption.

3. **Cutover plan**
   - Phase A: Generate `.cursor/rules` from DB but keep manual edits allowed (with guards that detect divergence).
   - Phase B: Mark `.cursor/rules` as generated (changes must go through DB/migrations).
   - Phase C: CI fails if `.cursor/rules` differs from DB-generated output.

---

## 5. Branch & Feature Impact (High-Level)

We will classify branches and features into:

1. **Governance Foundations**
   - Branches that touch:
     - RULES_INDEX, AGENTS.md, MASTER_PLAN.
     - Control-plane migrations or guards.
   - These must be reconciled into the governance-rebuild branch or archived.

2. **Telemetry & Exports**
   - Branches that adjust:
     - Compliance exports.
     - MCP exports.
     - PM snapshot / DSN echo behavior.
   - Must be re-based on the resurrected governance schema.

3. **UI / LM / Feature Work (Provisional)**
   - Branches implementing:
     - Atlas dashboards.
     - Bible/StoryMaker UIs.
     - LM insights, indicators, adapters.
   - These remain **provisional** until:
     - Governance SSOT is in Postgres.
     - TVs/Tags and strict/hint mode are enforced end-to-end.

4. **Cleanup Actions (to be detailed in OPS-004)**
   - For each governance-related branch:
     - Decide: merge, rebase onto governance branch, or archive.
   - Make governance branch the base for future feature branches until Phase-7 governance is declared complete.

---

## 6. Next Steps

1. Bring DB online in a controlled way (db_ready posture) and confirm the existence of:
   - `public.ai_interactions`
   - `public.governance_artifacts`
   - `control.agent_run`
   - `control.tool_catalog`
   - `gematria.graph_stats_snapshots`

2. Define actual SQL migrations for the governance tables in 4.1.

3. Implement ingestion scripts in 4.2 and run a first backfill (HINT mode only).

4. Add guards to verify DB↔docs↔.cursor alignment.

5. Only after these are proven green:
   - Resume UI/LM feature work (Phase-7+, Phase-8/9) on top of the repaired governance substrate.
