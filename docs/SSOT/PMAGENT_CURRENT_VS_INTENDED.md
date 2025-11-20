# pmagent — Current vs Intended State (Control Plane Orchestrator)

> **Short version:**
> `pmagent` (`agentpm`) is already the *governed conductor* for parts of the system, but a lot of the original design lives in **guards + Make + workflows** instead of a single, clean CLI surface.
> 
> This doc explains what's **implemented now** and what's still **planned**.

---

## 1. Role in the Architecture

### Intended

* **pmagent is the central operational orchestrator** for Gemantria.v2.
* All serious operations are supposed to go:
  * Human / Cursor → **pmagent** → guards / tools → Postgres control plane → Atlas / dashboards.
* pmagent should be the **only public entry point** that:
  * Validates environment + DSN,
  * Chooses models,
  * Runs pipelines,
  * Records runs and violations,
  * Emits Atlas/Proof artifacts.

### Current

* pmagent **exists** and is used for:
  * Control-plane status and health checks (`pmagent control status`, `pmagent control summary`).
  * LM health checks (`pmagent health lm`, `pmagent lm status`).
  * Semantic doc search (`pmagent docs search`).
  * System health aggregation (`pmagent health system`).
  * Reality checks (`pmagent reality-check 1`, `pmagent reality-check live`).
* But **not all workflows go through pmagent** yet:
  * Many CI jobs and guard suites still call `make` targets or scripts directly.
  * pmagent is a "governed tool" rather than the absolute gatekeeper.

**Gap:**
We're partway through the migration from "Make + scripts + guards" to "pmagent as the top-level conductor."

---

## 2. CLI Commands

### Intended CLI Surface (examples from original design)

Planned or aspirational commands:

* `pmagent lm.models` – enumerate and validate LM Studio models.
* `pmagent reality.check` – single command to run DSN, DB, LM, guard smokes.
* `pmagent atlas.proof` – generate full Atlas proof bundle.
* `pmagent mcp.catalog` – export/validate MCP catalog view.
* `pmagent ops.ledger.append` – append new ops bundles into a ledger.
* Later: `pmagent pipeline.full`, `pmagent storymaker.run`, etc.

### Current CLI Surface (as of now)

Implemented commands (names approximate):

* `pmagent health system` – Aggregate system health (DB + LM + Graph).
* `pmagent health db` – Database health posture.
* `pmagent health lm` – LM Studio / model slot health.
* `pmagent health graph` – Graph overview statistics.
* `pmagent lm status` – Show LM configuration and local service health (all slots).
* `pmagent status explain` – Explain current DB + LM health in plain language.
* `pmagent control status` – DB/control-plane health summary.
* `pmagent control summary` – Richer control-plane info (aggregated).
* `pmagent control tables` – List all schema-qualified tables with row counts.
* `pmagent control schema` – Introspect control-plane table schemas (DDL).
* `pmagent control pipeline-status` – Summarize recent pipeline runs.
* `pmagent graph overview` – Display graph overview statistics.
* `pmagent graph import` – Import graph_stats.json into database.
* `pmagent ask docs <question>` – Answer questions using SSOT documentation.
* `pmagent docs search <query>` – Search governance/docs content via semantic similarity.
* `pmagent kb registry list` – List all registered KB documents.
* `pmagent kb registry show <doc_id>` – Show details for a single KB document.
* `pmagent kb registry by-subsystem --owning-subsystem <subsystem>` – Filter documents by owning subsystem.
* `pmagent kb registry by-tag --tag <tag>` – Filter documents by tag.
* `pmagent kb registry summary` – Get KB registry status summary (same as `status kb`).
* `pmagent kb registry validate` – Validate registry entries (check file existence, duplicates).
* `pmagent status kb` – **Primary KB status view for PM/AgentPM planning (KB-Reg:M3b)** – Shows document counts by subsystem/type and missing files.
* `pmagent plan kb` – **Registry-powered planning surface (AgentPM-Next:M1)** – Returns prioritized documentation worklist (missing > stale > out_of_sync > low_coverage > info) with suggested actions, grouped by subsystem.
* `pmagent reality-check 1` – Run Reality Check #1 automated bring-up.
* `pmagent reality-check live` – Run Reality Check #1 LIVE (DB + LM + pipeline).
* `pmagent bringup full` – Fully start DB, LM Studio server+GUI, and load models.
* `pmagent mcp sse` – Ensure MCP SSE server is running.

**Gaps:**

* No single **`reality.check`** command yet (only `reality-check 1` and `reality-check live`).
* No first-class **`atlas.*`**, **`mcp.*`** (beyond `mcp sse`), **`ops.ledger.*`** commands yet.
* Pipelines (graph, eval, knowledge) are still driven by Make + scripts, not pmagent verbs.

---

## 3. Governance & Rules (050/051/052, PoR, Phase Gates)

### Intended

* pmagent is **the most governed component**:
  * **Rule-050** (LOUD FAIL): any guard/DSN/LM/control-plane violation → immediate non-zero exit with a structured verdict.
  * **Rule-051** (CI gate): merges must pass pmagent reality checks (HINT on PRs, STRICT on tags).
  * **Rule-052** (Tool priority): pmagent commands are only issued via an ordered tool chain (local → GitHub → codex → gemini/mcp).
* Every pmagent command should:
  * Create an `agent_run` row in the control plane.
  * Pass through PoR (doc fragment hashes for AGENTS, MASTER_PLAN, etc).
  * Record any violations in `violations_json`.
* Phase gates:
  * Certain pmagent capabilities (Phase-8+) only run once earlier phases (e.g. Phase-7B) have recorded ledger entries.

### Current

* **Governance exists**, but it's not all inside pmagent yet:
  * DSN centralization, ALWAYS-APPLY guards, and control-plane checks are wired via **scripts + Make + workflows**.
  * `scripts/config/env.py` is the canonical DSN loader.
  * Guards exit loudly and write evidence if something is wrong.
* Control-plane tables and exports are real:
  * `control.capability_session`, `control.agent_run`, `control.doc_fragment` tables exist.
  * `ai_interactions`, `governance_artifacts`, Atlas exports (`lm_indicator`, `compliance.head`, kb docs, etc.).
* PoR / doc-hash gating is **not yet enforced** by every pmagent command.
* Rule-050/051/052 behavior is enforced **operationally** (through how CI and OPS are written), not yet uniformly inside pmagent itself.
* **AI tracking is implemented**:
  - Runtime LM calls: `lm_studio_chat_with_logging()` and `guarded_lm_call()` write to `control.agent_run` via `_write_agent_run()` helper
  - CLI commands: Most pmagent commands (e.g., `reality-check check`, `health system`, `control status`, `bible retrieve`) use `create_agent_run()` and `mark_agent_run_success()` / `mark_agent_run_error()` to track executions in `control.agent_run_cli`
  - DB-off behavior: All tracking functions gracefully no-op when DB is unavailable (return `None`, no exceptions) for hermetic CI/testing
* **pm.snapshot integration is implemented (AgentPM-First:M3 + M4 + KB-Reg:M2)**:
  - `make pm.snapshot` / `scripts/pm_snapshot.py` composes health, status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10), and KB registry into a single operator-facing snapshot
  - **Unified helper**: `agentpm.status.snapshot.get_system_snapshot()` — Single source of truth for system snapshot composition, shared by `pm.snapshot` and WebUI APIs (`/api/status/system`)
  - Generates both Markdown (`share/pm.snapshot.md`) and JSON (`evidence/pm_snapshot/snapshot.json`) outputs
  - Calls `pmagent health system` (via `agentpm.tools.system.health()`), `pmagent status explain` (via `agentpm.status.explain.explain_system_status()`), and `pmagent reality-check check --mode hint` (via `agentpm.reality.check.reality_check()`)
  - Queries `control.agent_run` and `control.agent_run_cli` tables for AI tracking summary (counts, success/error rates)
  - Reads `SHARE_MANIFEST.json` for share manifest summary (file count and status)
  - Reads Phase-8/10 eval exports for eval insights summary (advisory-only, export-driven analytics)
  - Reads `share/kb_registry.json` for KB registry summary (KB-Reg:M2 + M3a, advisory-only, read-only in CI, seeded with core SSOT/runbook/AGENTS docs)
  - **KB status view (KB-Reg:M3b)**: `pmagent status kb` provides PM-focused KB registry status view with document counts by subsystem/type and missing files list
  - **KB hints (KB-Reg:M4)**: KB registry health surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`; hints include missing docs, low coverage subsystems, and validation issues; all hints are advisory-only and never affect `overall_ok`
  - **KB-aware status explanation (KB-Reg:M5)**: `pmagent status.explain` includes `documentation` section with KB registry status, coverage breakdown, key docs (SSOT, ADRs, root AGENTS.md), and hints; `/status` UI shows "Documentation Health" card with counts, subsystem breakdown, hints badge, and key doc links
  - **KB drift & freshness checks (KB-Reg:M6)**: KB registry tracks document freshness (last_seen_mtime, last_refreshed_at, min_refresh_interval_days); `analyze_freshness()` detects stale/missing/out-of-sync docs; freshness summary included in `pmagent status kb` and `pmagent status.explain`; KB hints include `KB_DOC_STALE` and `KB_DOC_OUT_OF_SYNC` warnings; `pmagent reality-check` includes concise doc freshness summary in hints (advisory-only); default refresh intervals: SSOT (30d), ADR (90d), AGENTS.md (14d), runbook (60d), rule (90d), changelog (7d), other (60d)
  - DB-off/LM-off behavior: All components degrade gracefully to clear HINTs and explicit mode indicators; snapshot is still produced with all available information (hermetic behavior for CI/testing)
  - **WebUI alignment**: WebUI status pages (`/status`, `/dashboard`, `/lm-insights`, `/db-insights`) consume the same snapshot data via `/api/status/system` and related endpoints, ensuring consistency between CLI and web interfaces

**Gap:**

* We still rely heavily on Make + scripts to enforce governance.
  pmagent hasn't yet become the single enforcement point for all of those rules.

---

## 4. Capabilities

### Intended Capabilities (macro-level)

* **Env & LM validation**: deep reality checks for DSN, DB, LM Studio and model slots.
* **Pipeline execution**: running full LangGraph pipelines, temporal analytics, correlations.
* **Atlas proofs**: generating all compliance, badges, coverage, traces, webproof bundles.
* **MCP integration**: MCP RO views, validation, SSE bridge.
* **Ops ledger**: append/query known-good command bundles.
* **Guard proofs**: structured, strict guard runs with verdicts.
* **Phase-8+**: direct DSPy pipelines, StoryMaker orchestration, live compliance queries.

### Current Capabilities

* ✅ **Env/LM health** via:
  * `pmagent health`, `pmagent health lm`, `pmagent lm status`.
  * Control-plane DB checks via `pmagent control status/summary` and smokes.
* ✅ **Semantic search**:
  * `pmagent docs search` for Tier-0 docs and governance.
* ✅ **Dashboards**:
  * Phase-8 orchestrator dashboards (Forecast + Graph) wired to control-plane exports.
* 🟡 **Atlas/guards**:
  * Atlas + guard tooling is live via Make + scripts, but not wrapped neatly as `pmagent atlas.*` or `pmagent guards.*`.
* 🔴 **Ops ledger + pipelines as pmagent verbs**:
  * Control-plane + logs are there, but we don't yet have nice `pmagent ops.*` or `pmagent pipeline.*` commands.

---

## 5. Execution Flow

### Intended Flow

Any pmagent command should:

1. Start a capability session (`capability_session` row).
2. Validate PoR (doc fragments for AGENTS, MASTER_PLAN, contracts).
3. Discover/validate LM providers and configured models.
4. Call into guarded tools with JSON schema validation and provenance.
5. Record results and violations in control plane and evidence/exports.
6. Return a structured JSON verdict and a clear human summary.

### Current Flow

* We **do**:
  * Call guards and tools that validate DSN, DB, exports, etc.
  * Write evidence to `share/` and `evidence/`.
  * Use control-plane tables for AI tracking:
    * Runtime LM calls write to `control.agent_run` via `_write_agent_run()` (from `agentpm.runtime.lm_logging`)
    * CLI commands write to `control.agent_run_cli` via `create_agent_run()` / `mark_agent_run_success()` / `mark_agent_run_error()` (from `agentpm.control_plane`)
  * Surface status via dashboards and `pmagent health`/`control` commands.
  * Some commands (like `reality-check check`) follow a structured step-by-step flow with AI tracking.

* We **do not yet consistently**:
  * Start and track a fully uniform `capability_session` for every pmagent command.
  * Enforce PoR/doc-hash gates on every run.
  * Guarantee a single universal verdict schema for all commands.

**Gap:**

The plumbing for most of this exists, but pmagent isn't yet the one that always stitches it together.

---

## 6. Roadmap to Alignment (high-level)

To make pmagent match the original design more literally, we need to:

1. Add a **canonical `pmagent reality.check`** command that wraps the health + smokes we already rely on.
2. Introduce **`pmagent atlas.proof`** and other `atlas.*` verbs around existing exports.
3. Gradually route new CI jobs and OPS sequences through pmagent instead of Make-only entrypoints.
4. Tighten session tracking, PoR checks, and verdict schemas so every pmagent call is recorded and governed the same way.

The next concrete step is `pmagent reality.check`.

---

## 7. Related Documentation

* `AGENTS.md` (root) – Agent framework and operational contracts.
* `docs/runbooks/CONTROL_SUMMARY.md` – Control-plane summary usage.
* `docs/runbooks/SYSTEM_HEALTH.md` – System health checks.
* `docs/runbooks/LM_HEALTH.md` – LM health checks.
* `agentpm/scripts/AGENTS.md` – Scripts directory documentation.
* `.cursor/rules/050-ops-contract.mdc` – OPS Contract v6.2.3.
* `.cursor/rules/051-cursor-insight.mdc` – CI gating and handoff protocol.
* `.cursor/rules/052-tool-priority.mdc` – Tool priority and context guidance.

---

**Last Updated:** 2025-11-17  
**Status:** Living document; reflects current state as of Phase-8 completion.

