# AGENTS.md — Gemantria Agent Framework
<!-- alwaysapply.sentinel: 050,051,052 source=ai_interactions -->

> **Always-Apply Triad**: We operate under **Rule-050 (LOUD FAIL)**, **Rule-051 (CI gating)**, and **Rule-052 (tool-priority)**. The guards ensure this 050/051/052 triad is present in docs and mirrored in DB checks.

## Directory Purpose

The root `AGENTS.md` serves as the primary agent framework documentation for the Gemantria repository, defining mission, priorities, environment, workflows, and governance for all agentic operations across the codebase.

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1) Correctness: **Code gematria > bible_db > LLM (LLM = metadata only)**.
2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.
3) Safety: **bible_db is READ-ONLY**; parameterized SQL only; **fail-closed if <50 nouns** (ALLOW_PARTIAL=1 is explicit).

## pmagent Status

See `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` for current vs intended state of pmagent commands and capabilities.

See `docs/SSOT/PMAGENT_REALITY_CHECK_DESIGN.md` for reality.check implementation design and validation schema.

## PM DMS Integration (Rule-053) ⭐ NEW

**Phase 9.1**: PM must query **Postgres DMS (control plane)** BEFORE file searching.

**DMS-First Workflow**:
1. **Documentation**: `pmagent kb registry by-subsystem --owning-subsystem=<project>`
2. **Tool Catalog**: `SELECT * FROM control.mcp_tool_catalog WHERE tags @> '{<project>}'`
3. **Project Status**: `pmagent status kb` and `pmagent plan kb list`
4. **File Search** (LAST RESORT): Only if content not in DMS

**Feature Registration**:
- After building new tool/module: Create MCP envelope → `make mcp.ingest` → Update KB registry
- PM learns capabilities automatically through DMS registration
- **Goal**: PM and project develop together

See `.cursor/rules/053-pm-dms-integration.mdc` and `docs/SSOT/PM_CONTRACT.md` Section 2.6 for full workflow.

## Environment
- venv: `python -m venv .venv && source .venv/bin/activate`
- install: `make deps`
- Databases:
  - `BIBLE_DB_DSN` — read-only Bible database (RO adapter denies writes pre-connection)
  - `GEMATRIA_DSN` — read/write application database
- **DSN Access**: All DSN access must go through centralized loaders:
  - **Preferred**: `scripts.config.env` (`get_rw_dsn()`, `get_ro_dsn()`, `get_bible_db_dsn()`)
  - **Legacy**: `src.gemantria.dsn` (`dsn_rw()`, `dsn_ro()`, `dsn_atlas()`)
  - Never use `os.getenv("GEMATRIA_DSN")` directly - enforced by `guard.dsn.centralized`

### 3-Role DB Contract (OPS v6.2.3)
**Extraction DB**: `GEMATRIA_DSN` → database `gematria`  
**SSOT DB**: `BIBLE_DB_DSN` → database `bible_db` (read-only)  
**AI Tracking**: **lives in `gematria` DB**, `public` schema; `AI_AUTOMATION_DSN` **must equal** `GEMATRIA_DSN`.  
Guards: `guard.rules.alwaysapply.dbmirror` (triad), `guard.ai.tracking` (tables `public.ai_interactions`, `public.governance_artifacts`).  
CI posture: HINT on PRs; STRICT on tags behind `vars.STRICT_DB_MIRROR_CI == '1'`.
- Batch & overrides:
  - `BATCH_SIZE=50` (default noun batch size)
  - `ALLOW_PARTIAL=0|1` (if 1, manifest must capture reason)
  - `PARTIAL_REASON=<string>` (required when ALLOW_PARTIAL=1)
- Checkpointer: `CHECKPOINTER=postgres|memory` (default: memory for CI/dev)
- LLM: Local inference providers (LM Studio or Ollama) when enabled; confidence is metadata only.
  - **Inference Providers** (Phase-7E): Supports both LM Studio and Ollama via `INFERENCE_PROVIDER`:
    - `lmstudio`: OpenAI-compatible API (`OPENAI_BASE_URL`) - **Granite models available in LM Studio**
    - `ollama`: Native HTTP API (`OLLAMA_BASE_URL`) - **Granite models also available via Ollama**
  - **Setup**: See `docs/runbooks/LM_STUDIO_SETUP.md` for LM Studio setup or `docs/runbooks/OLLAMA_ALTERNATIVE.md` for Ollama
  - **Quick Start (LM Studio)**: Set `INFERENCE_PROVIDER=lmstudio`, `LM_STUDIO_ENABLED=1`, `OPENAI_BASE_URL=http://127.0.0.1:9994/v1`
  - **Quick Start (Ollama)**: Set `INFERENCE_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://127.0.0.1:11434`, then `ollama pull ibm/granite4.0-preview:tiny`
  - **Health Check**: `pmagent health lm` verifies inference provider availability
  - **Default Models (Phase-7F)**: 
    - **Default stack**: Granite embedding + Granite reranker + Granite local agent.
      - `LOCAL_AGENT_MODEL=granite4:tiny-h` (Ollama)
      - `EMBEDDING_MODEL=granite-embedding:278m` (Granite)
      - `RERANKER_MODEL=granite4:tiny-h` (Granite)
    - **Bible lane**: BGE embedding + theology model; BGE is not the general default.
      - `BIBLE_EMBEDDING_MODEL=bge-m3:latest` (Ollama: `qllama/bge-m3`) - for Bible/multilingual tasks only
    - **Qwen reranker**: fallback only, not the primary reranker.
    - `THEOLOGY_MODEL=Christian-Bible-Expert-v2.0-12B` (via theology adapter)
  - **Retrieval Profile (Phase-7C)**: `RETRIEVAL_PROFILE=DEFAULT` (default) uses Granite stack. Setting `RETRIEVAL_PROFILE=GRANITE` or `BIBLE` switches retrieval embeddings/rerankers accordingly. Granite IDs are resolved via `GRANITE_EMBEDDING_MODEL`, `GRANITE_RERANKER_MODEL`, and `GRANITE_LOCAL_AGENT_MODEL`. Misconfigured Granite profiles emit a `HINT` and fall back to DEFAULT for hermetic runs.
  - **Planning Lane (Gemini CLI + Codex)**: pmagent exposes a **planning slot** for backend planning, coding refactors, and math-heavy reasoning. This lane is intentionally **non-theology** and never substitutes for gematria/theology slots.
    - Configure via `PLANNING_PROVIDER` (`gemini`, `codex`, `lmstudio`, `ollama`) and `PLANNING_MODEL`. Optional toggles: `GEMINI_ENABLED`, `CODEX_ENABLED`, `GEMINI_CLI_PATH`, `CODEX_CLI_PATH`.
    - pmagent calls CLI adapters (`agentpm/adapters/gemini_cli.py`, `agentpm/adapters/codex_cli.py`) with structured prompts, logs runs through `agentpm.runtime.lm_logging`, and records outcomes in `control.agent_run`.
    - If the selected CLI is unavailable, pmagent fails closed with `mode="lm_off"` and optionally falls back to the Granite local_agent slot—never to theology.
    - Multi-agent planning is permitted: pmagent may spin up multiple planning calls (Gemini/Codex instances) for decomposition tasks, each tracked with its own agent_run row. Context windows are large, but prompts must still cite SSOT docs; no theology, scripture exegesis, or gematria scoring is delegated to these tools.
    - Planning lane usage is opt-in per operator; CI remains hermetic (planning CLIs disabled unless explicitly allowed).
    - **Runbooks**: See `docs/runbooks/GEMINI_CLI.md` and `docs/runbooks/CODEX_CLI.md` for setup and usage details.

### LM Status Command

- Command: `pmagent lm.status`
- Purpose: Show current LM configuration and local service health:
  - Per-slot provider and model (local_agent, embedding, reranker, theology)
  - Ollama health (local only)
  - LM Studio/theology_lmstudio health (local only)
- Notes:
  - No LangChain/LangGraph; this is a thin status/introspection layer.
  - All checks use localhost URLs (127.0.0.1); no internet calls.

### System Status UI & TVs

- JSON endpoint:
  - Path: `/api/status/system` (DB + LM health snapshot; reuses DB + LM health helpers)
- HTML status page:
  - Path: `/status`
  - Shows:
    - DB health mode (`ready`, `db_off`, or `partial`)
    - LM slots (local_agent, embedding, reranker, theology) with provider, model, and service status
- TVs:
  - `TV-LM-HEALTH-01`: LM stack local health snapshot (Ollama + LM Studio per-slot status)
  - `TV-DB-HEALTH-01`: DB health mode snapshot (ready/db_off/partial) based on db health guard
- Notes:
  - All checks are local-only (Postgres + LM providers on 127.0.0.1).
  - No LangChain/LangGraph in this path; thin status layer over existing adapters and guards.

### Status Explanation Skill

- Command: `pmagent status.explain`
- Purpose:
  - Read the combined DB + LM system status snapshot.
  - Produce a plain-language explanation of current health:
    - Database mode (ready/db_off/partial) and what it means.
    - LM slots (local_agent, embedding, reranker, theology) and their service states.
- Behavior:
  - Uses rule-based summaries by default.
  - May call the local LM provider stack (Granite/Ollama/LM Studio) to refine wording if available.
  - Never fails if LM is down; always returns a best-effort explanation.
- Options:
  - `--json-only`: Return JSON instead of formatted text.
  - `--no-lm`: Skip LM enhancement, use rule-based explanation only.
- Notes:
  - No external internet calls; only local DB and LM services (127.0.0.1).
  - Exit code 0 always (explanations are best-effort snapshots).

### Status Explanation in UI

- API endpoint:
  - Path: `/api/status/explain`
  - Returns:
    - `level`: "OK" | "WARN" | "ERROR"
    - `headline`: short summary
    - `details`: human-readable explanation
- HTML integration:
  - The `/status` page shows:
    - An "Explanation" card that surfaces the headline and details.
    - Explanation is refreshed alongside the raw DB/LM status snapshot.
- Notes:
  - Uses the same explain_system_status() helper as `pmagent status explain`.
  - Works even if LM is offline (falls back to rule-based summary).

### LM Insights Graph

- API endpoint:
  - Path: `/api/lm/indicator`
  - Purpose: Expose LM indicator snapshots (from existing exports) in a stable JSON shape for UI.
  - Returns:
    - `snapshot`: Current LM indicator data (status, rates, metrics) or `null` if unavailable
    - `note`: Message if data is missing
- HTML page:
  - Path: `/lm-insights`
  - Shows a simple chart of recent LM indicator snapshots:
    - Status indicator (color-coded: green/yellow/red)
    - Success/error rates bar chart
    - Metrics summary (total calls, success rate, error rate)
- Data source:
  - Read-only view over the LM indicator export JSON created in Phase-4C/4D.
  - Location: `share/atlas/control_plane/lm_indicator.json`
- Notes:
  - No DB queries; no new LM calls.
  - Uses Tailwind + Chart.js via CDN; no React/LangChain/LangGraph.

### System Dashboard

- HTML page:
  - Path: `/dashboard`
  - Purpose: Provide a friendly overview of:
    - System health (DB + LM) using /api/status/system and /api/status/explain.
    - LM indicator snapshot using /api/lm/indicator.
- Cards:
  - "System Health" card:
    - Shows overall level (OK/WARN/ERROR), headline, DB mode, LM slot summary.
    - Links to `/status` for detailed view.
  - "LM Insights" card:
    - Shows LM indicator status (healthy/degraded/offline) and key metrics.
    - Links to `/lm-insights` for detailed graph.
- Notes:
  - All data is read-only from existing JSON APIs/exports.
  - No additional DB queries or LM calls beyond current endpoints.
  - Auto-refreshes every 30 seconds.
  - Uses Tailwind CSS for styling (consistent with /status and /lm-insights).

### DB Health Graph

- API endpoint:
  - Path: `/api/db/health_timeline`
  - Purpose: Expose DB health snapshots from existing exports in a stable JSON shape for UI.
- HTML page:
  - Path: `/db-insights`
  - Shows a chart of DB health mode over time (ready/partial/db_off) and a summary of the latest state.
- Data source:
  - Read-only view over DB health export JSON (smokes/health indicators).
- Notes:
  - No DB queries or LM calls; purely export-driven.
  - Uses Tailwind + Chart.js via CDN; no React/LangChain/LangGraph.

### BibleScholar Passage UI

- API endpoint:
  - Path: `/api/bible/passage`
  - Purpose: Fetch a Bible passage from `bible_db` and generate an optional theology commentary using the theology LM slot.
  - Query parameters:
    - `reference`: Bible reference string (e.g., "John 3:16-18")
    - `use_lm`: Boolean (default: True) - Use AI commentary
  - Returns:
    - `reference`: The input reference
    - `verses`: Array of verse objects with book, chapter, verse, text
    - `commentary`: Object with `source` ("lm_theology" | "fallback") and `text`
    - `errors`: Array of error messages (empty if no errors)
- HTML page:
  - Path: `/bible`
  - Features:
    - Reference input field (e.g., "John 3:16-18")
    - Optional "Use AI commentary" toggle (default ON)
    - Renders passage text with verse numbers
    - Displays commentary in a separate section
    - Shows error messages if reference is invalid or DB unavailable
- Data sources:
  - `bible_db` read-only adapter (no writes)
  - LM theology slot (Christian-Bible-Expert model via existing LM adapter)
- Notes:
  - All calls are local-only (DB + LM)
  - Falls back gracefully if LM is offline; passage text is still shown
  - Uses Tailwind CSS for styling (consistent with other UI pages)


  - **Phase-7F Model Readiness**: All four slots configured, adapters implemented, tests created. See `docs/PHASE_7F_IMPLEMENTATION_SUMMARY.md` for details.
  - **Live Gate**: Pipeline fails-closed if `USE_QWEN_EMBEDDINGS=true` but models unavailable
  - **Phase-3C Integration**: Enrichment pipeline uses `lm_studio_chat_with_logging()` with control-plane observability (see RFC-080, ADR-066)
  - **LM Observability Exports**: Phase-4 exports provide LM status signals:
    - `lm_usage_7d.json` — Raw usage metrics (calls, latency)
    - `lm_health_7d.json` — Health metrics (success/error rates)
    - `lm_insights_7d.json` — Aggregated insights (usage ratio, top errors)
    - `lm_indicator.json` — **Canonical LM status signal for downstream apps** (offline/healthy/degraded)
  - **Phase-5 LM Integration**: ✅ **COMPLETE** — StoryMaker (LM status tile, PR #1) and BibleScholar (header badge, PR #2) now consume `lm_indicator.json` via the shared widget contract. Hermetic adapter implemented in `agentpm/lm_widgets/adapter.py` with full test coverage.
  - **Phase-6**: LM Studio live usage + DB-backed knowledge planning underway.
  - **Phase-7E**: ✅ **COMPLETE** — Ollama provider integration with Granite 4.0 support. Provider routing via `agentpm/adapters/lm_studio.py` (`chat()` and `embed()` functions).
  - **Phase-7F**: ✅ **COMPLETE** — Flexible local LM architecture with per-slot provider routing:
    - **Per-slot provider configuration**: Each model slot (local_agent, embedding, reranker, theology) can independently use `ollama` or `lmstudio` via `LOCAL_AGENT_PROVIDER`, `EMBEDDING_PROVIDER`, `RERANKER_PROVIDER`, `THEOLOGY_PROVIDER` env vars
    - **Provider enable/disable flags**: `OLLAMA_ENABLED` and `LM_STUDIO_ENABLED` control provider availability
    - **Default configuration**: Granite stack for general retrieval (embedding, reranker, local agent), LM Studio for theology (Christian-Bible-Expert-v2.0-12B)
    - **Models**: `granite4:tiny-h` (chat/rerank - default), `granite-embedding:278m` (embeddings - default), `Christian-Bible-Expert-v2.0-12B` (theology)
    - **Bible lane**: BGE models reserved for Bible/multilingual tasks; not the general default
    - **Test suite**: `tests/integration/test_phase7f_model_readiness.py` (availability-aware, skips when services unavailable)
    - **Architecture**: No LangChain/LangGraph in core LM pipeline; all calls go to local services (Ollama, LM Studio) on 127.0.0.1
  - **Phase-7C**: ✅ **COMPLETE** — LM Router (centralized task-to-model routing):
    - **Router module**: `agentpm/lm/router.py` - Rule-based task classification and model slot selection
    - **Router contract**: `docs/SSOT/LM_ROUTER_CONTRACT.md` - Full specification of router API and behavior
    - **Integration**: Math verifier (`src/nodes/math_verifier.py`) uses router when `ROUTER_ENABLED=1` (default enabled)
    - **CLI command**: `pmagent lm router-status` - Show router configuration and slot mappings (read-only, hermetic)
    - **Configuration**: `ROUTER_ENABLED` (default: `1`) controls router usage; set to `0` for legacy behavior
    - **Routing rules**: Embedding → `embedding` slot, rerank → `reranker` slot, math → `math` slot, theology/bible → `theology` slot, tool-calling → `local_agent` slot, default → `local_agent` slot
    - **Test suite**: `tests/unit/test_lm_router.py` - Unit tests for router decisions and fallback behavior (hermetic, no network calls)
    - **Design reference**: `Prompting Guide for Our Core LLM models.md` - Design-level spec for model stack and prompting
  - **LM Studio MCP Bridge**: Optional SSE server on port 8005 for LM Studio plugin integration
    - **Auto-start**: Set `AUTO_START_MCP_SSE=1` in `.env` to automatically start server when needed
    - **Integration points**:
      - `pmagent bringup full` - Automatically ensures MCP SSE server is running (if `AUTO_START_MCP_SSE=1`)
      - `make bringup.001` - Automatically ensures server is running before LM Studio checks
      - `pmagent mcp sse` - Manual ensure command (auto-starts if `AUTO_START_MCP_SSE=1`)
      - `make mcp.sse.ensure` - Makefile ensure command (auto-starts if `AUTO_START_MCP_SSE=1`)
    - **Manual start**: `make mcp.sse.start` or `~/mcp/gemantria-ops/run_server_sse.sh`
    - **Health check**: `make mcp.sse.health` or `pmagent mcp sse`
    - **Stop**: `make mcp.sse.stop`
    - **Guard**: `ENABLE_LMSTUDIO_MCP=1 make guard.mcp.sse` (optional, HINT mode by default)
    - **Server URL for LM Studio**: `http://127.0.0.1:8005/sse`
- GitHub: MCP server active for repository operations (issues, PRs, search, Copilot integration).
- CI: MyPy configured with `ignore_missing_imports=True` for external deps; DB ensure script runs before verify steps.
- **Branch Protection**: `pmagent repo guard-branch` enforces "No Direct Work on Main". Use in pre-commit hooks.

### Make Targets & DSN Precedence

**Core operational targets:**
- `make reality.green` — **Full system truth gate (110% signal)** - Validates DB health (Option C), control-plane health, AGENTS.md sync, share sync, and required exports. Only passes when system is up to date and consistent for the next agent. **Required before**: declaring features complete, opening PRs for main, generating share/ snapshots.
- `make bringup.001` — STRICT bring-up verification (env gate → inference provider → pipeline → guards → evidence)
- `make dsns.echo` — Print redacted DSNs for operator sanity (never prints secrets)
- `make pm.snapshot` — Generate PM-facing status snapshot with DSN posture proofs and 25-file manifest tracking
- `make share.manifest.verify` — Verify share directory contains exactly 25 files

**AI-in-the-loop docs helpers:**
- `pmagent docs reality-check-ai-notes` — Uses Granite (LM Studio) when available to propose orchestrator-facing notes about the reality-check system; safe when LM is off (writes placeholder file)

**MCP & Atlas targets:**
- `make mcp.dev.bench` — Run MCP endpoint benchmarks
- `make mcp.catalog.export` — Export MCP catalog JSON
- `make mcp.catalog.validate` — Validate MCP catalog structure
- `make atlas.viewer.validate` — Validate Atlas viewer HTML/JS/JSON presence
- `make atlas.webproof` — Browser-verified UI proof (Rule-067); `STRICT_WEBPROOF=1` for tags

**DSN precedence (via centralized loaders):**
- **RW DSN**: `GEMATRIA_DSN` → `RW_DSN` → `AI_AUTOMATION_DSN` → `ATLAS_DSN_RW` → `ATLAS_DSN`
- **RO DSN**: `GEMATRIA_RO_DSN` | `ATLAS_DSN_RO` (peers) → `ATLAS_DSN` → (fallback to RW)
- **Bible DB DSN**: `BIBLE_RO_DSN` → `RO_DSN` → `ATLAS_DSN_RO` → `ATLAS_DSN` (also checks `BIBLE_DB_DSN` directly)
- All DSN access must use centralized loaders (`scripts.config.env` or `src.gemantria.dsn`); never `os.getenv()` directly

## Workflow (small green PRs)

**CRITICAL: Local Gates Are Primary (Rule 050 §5.5)**

Before **any** push or PR creation, **mandatory local gates** must pass:

```bash
ruff format --check . && ruff check .
make book.smoke
make ci.exports.smoke
make reality.green STRICT
```

**If any local gate fails:**
- **DO NOT** push
- **DO NOT** open a PR
- Fix issues locally where error messages are readable
- Re-run gates until all pass

**Only after all local gates pass:**
- Push to remote
- Open/update PR
- Continue with other work (do not wait for CI)

**CI is a mirror, not the gate.** CI may flake, be slow, or fail due to infrastructure. It must **never** be treated as a blocking dependency. "Waiting for CI" is not a valid state.

### Standard Workflow Steps

- Branch `feature/<short>` → **write tests first** → code → run local gates → commit → push → PR.
- Coverage ≥98%.
- Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`
- PR: Goal, Files, Tests, Acceptance.
- **MANDATORY**: Update `AGENTS.md` files when code changes (Rule 006, Rule 027):
  - New functions/classes/components → update directory's `AGENTS.md`
  - API contracts change → update `AGENTS.md` with new contracts
  - Behavior changes → update `AGENTS.md` documentation
  - Run `make agents.md.sync` to check for stale documentation
  - Run `python scripts/create_agents_md.py --dry-run` to find missing files
- Always run `make housekeeping` after any docs, scripts, or rules change before requesting review (Rule 058).

## Code Quality Standards
- **Formatting**: Ruff format (single source of truth)
- **Linting**: Ruff check with zero tolerance for style issues
- **Type checking**: MyPy with `ignore_missing_imports=True` for external deps
- **Import organization**: All imports at module top (no mid-file imports)
- **Line length**: 120 characters maximum
- **String concatenation**: Use `["cmd", *args]` instead of `["cmd"] + args`

### Debugging Workflow State Issues

If a script behaves unexpectedly or seems to be running an old version:

1.  **Clean the environment:** Run `make clean` to remove all Python cache and temporary files.
2.  **Verify Git status:** Ensure your working directory is clean with `git status -sb`.
3.  **Re-run the command:** Execute your command again from a fresh terminal.

This process eliminates stale bytecode as a source of errors.

## UI / Frontend Generation (Standard)
**Primary model:** Gemini 2.5 Pro (terminal/CLI, long context)
**Fallback / refinement:** Claude Sonnet 4 (highest-fidelity styling, complex refactors)

### Usage rules
1) Start all UI codegen (React/Next, charts, search UI) with **Gemini 2.5 Pro**.
2) If spec unmet after ≤2 iterations, or multi-file refactor / high-fidelity styling is required → **escalate to Claude Sonnet 4**.
3) Minor tweaks (single-file CSS/prop changes) may use a cheaper model.
4) Log model + prompt + iteration count in the PR body (see template).

### Libraries & structure (defaults)
- React 18+ (Next.js when SSR/SSG needed)
- State: Zustand or React Context (keep light)
- Viz: Recharts, D3 wrapper, React Flow (graphs)
- Styling: Tailwind (or CSS Modules)
- Layout: `src/components/*`, `src/hooks/*`, `src/services/*`, `src/views/*`

### QA gates (always)
- Frontend: `npm run lint && npm run test` (if present)
- Backend: `ruff format --check . && ruff check .`
- Security: run static checks where configured
- **Browser verification (Rule-051 + Rule-067)**: When modifying Atlas HTML, CSS, or visual artifacts, use Cursor's browser tool to verify visual content. See `docs/runbooks/ATLAS_VISUAL_VERIFICATION.md` for workflow. Run `make atlas.webproof` or `make browser.verify` to generate screenshots and receipts. **MANDATORY: Cursor MUST perform browser verification proactively for ALL UI/visual work without waiting for user reminders.**
- PR must include "Model Usage" block (see template).

### Runbook: Postgres checkpointer
1. Apply migration:
   ```bash
   psql "$GEMATRIA_DSN" -f migrations/002_create_checkpointer.sql
   ```
2. Verify locally:
   ```bash
   export CHECKPOINTER=postgres
   export GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gemantria
   make lint type test.unit test.integration coverage.report
   ```
3. Expected: tests green, coverage ≥98%, checkpoint storage and retrieval works end-to-end.

### Runbook: Database Bootstrap (CI)
1. Bootstrap script ensures database exists before migrations:
   ```bash
   scripts/ci/ensure_db_then_migrate.sh
   ```
2. Handles missing database gracefully with admin connection fallback
3. Applies vector extension and all migrations in order
4. Migration 014 fixed to handle schema evolution from migration 007 (composite primary key preservation, view recreation)
5. Used in CI workflows for reliable database setup

## Operations

### CI Verification
- **Empty DB tolerance**: Verify scripts handle missing tables gracefully in CI (zero counts allowed when DB empty)
- **Stats validation**: Allows zero nodes/edges when DB tables don't exist (prevents CI failures on empty databases)
- **File tolerance**: Handles missing graph/stats files in CI by using empty defaults
- **File Verification (Rule-046)**: All file operations verify existence first (`test -f`, `os.path.exists`, `head`). Missing critical files emit LOUD FAIL (no auto-creation, fail-closed). Critical files include SSOT artifacts, schema files, and core pipeline scripts.
- **SSOT JSONSchema validation**: PR-diff scoped validation of JSON files against schemas (non-blocking nightly sweep)
- **Rules audit strictness**: No ALLOW_RULES_GAP toggle; RESERVED stubs (047/048) maintain contiguous numbering
- **Pre-commit ordering**: `share.sync` runs before `repo.audit` to ensure share/ directory is synchronized before validation
- **Ruff version pinning**: CI workflows hard-pin ruff==0.13.0 with version verification to defeat cache drift (enforce-ruff.yml, lint-nightly.yml, soft-checks.yml, ci.yml)
- **Share sync robustness**: Content-only validation (mtime checks removed) ensures sync works across different filesystem timestamps

### Evaluation
* **Phase-8 local eval**: `make eval.smoke` runs a non-CI smoke to validate the eval harness. Do not wire into CI or `make go` until stabilized. Governance gates (037/038, share no-drift, NEXT_STEPS) remain unchanged.
* **Phase-8 manifest eval**: `make eval.report` loads `eval/manifest.yml` and emits `share/eval/report.{json,md}`. Keep this **local-only** until stabilized; no CI wiring and no `make go` edits.
* **Ops verifier (local)**: `make ops.verify` prints deterministic checks confirming Phase-8 eval surfaces exist (Makefile targets, manifest version, docs header, share dir). Local-only; not wired into CI.
* **Pipeline stabilization**: `eval.package` runs to completion with soft integrity gates; `targets.check.dupes` prevents Makefile regressions; `build_release_manifest.py` skips bundles/ for performance.

## Data Extraction Lineage

Phase 11 unified pipeline flow:

1. **graph_latest.json** (Phase 9 output)
   - Nodes with gematria values, Hebrew text, book/chapter/verse refs
   - Edges with cosine similarity, rerank scores, edge_strength blend

2. **temporal_patterns.json** + **pattern_forecast.json** (Phase 8 output)
   - Time-series data for frequency trends
   - Prophet forecasts with confidence intervals

3. **correlation_weights.json** (Phase 10 output)
   - Cross-text pattern analytics
   - Edge classification (strong/weak thresholds)

4. **unified_envelope.json** (Phase 11 output)
   - Single integrated format with all attributes
   - Versioned schema (`unified-v1`)
   - Configurable size extraction (100, 1k, 10k, 100k+ nodes)

**Extraction Script:** `scripts/extract/extract_all.py`
**Makefile Target:** `make ui.extract.all SIZE=10000 OUTDIR=ui/out`
**Validation:** JSON schema enforcement + size/performance gates + COMPASS mathematical correctness (>80% score)

### COMPASS: Comprehensive Pipeline Assessment Scoring System

**Purpose**: Mathematical envelope validation for data integrity and correctness
**Requirements**: >80% correctness threshold for envelope acceptance

**Capabilities**:
- Correlation weight validation (>0.5 significance threshold)
- Edge strength blend verification (0.5*cos + 0.5*rerank calculation)
- Temporal pattern integrity checks (monotonic timestamps, data consistency)
- CLI scoring with detailed issue reporting

**Usage**:
```bash
make test.compass  # Score envelope for mathematical correctness
python scripts/compass/scorer.py share/exports/envelope.json --verbose
```

**Scoring Categories**:
- **correlation_weights**: Edge significance validation (40% weight)
- **edge_strength_blend**: Blend calculation accuracy (40% weight)
- **temporal_patterns**: Time series data integrity (20% weight)

**Output**: PASS/FAIL status with detailed issue breakdown

## Cursor Execution Profile (Default-Apply)

This repo expects Cursor to **show its work** in a fixed shape so that GPT-5 and human orchestrators can continue from any point.

**Always output in 4 blocks:**

1. **Goal** — what this step is doing (e.g. "rebase PR #70 onto clean main and re-run hermetic bundle")
2. **Commands** — exact shell commands, top to bottom, no prose in between
3. **Evidence to return** — which command outputs we expect to see pasted back
4. **Next gate** — what happens once the evidence is pasted

### PM ↔ Cursor Auto Cadence (PM lane)

- In the **PM lane**, the Project Manager agent (governed by `docs/SSOT/PM_CONTRACT.md`) is responsible for:
  - Choosing the next work item from `MASTER_PLAN.md` / `share/MASTER_PLAN.md` / `NEXT_STEPS.md`.
  - Emitting the 4‑block (Goal, Commands, Evidence to return, Next gate) **for Cursor Auto**, not the human orchestrator.
- **Cursor Auto** must:
  - Treat the Commands block as the only source of actions for that step.
  - Execute those commands, then report back evidence in the agreed shape.
  - Avoid asking the orchestrator for infra/env decisions; those belong to PM/OPS.
- The **orchestrator** only provides high‑level direction and accepts plain‑English summaries; they never run commands by hand in this workflow.

- For any work that touches **DB or LM**, each 4‑block **Commands** section MUST:
  - Re‑establish baseline posture (venv check, repo root + branch, `git status -sb`).
  - Run the hermetic bundle and posture checks:
    - `ruff format --check . && ruff check .`
    - `make book.smoke`
    - `make eval.graph.calibrate.adv`
    - `make ci.exports.smoke`
    - `make reality.green`
  - Include at least one **live DB+LM execution** of the specific feature path (for example: a Knowledge MCP round‑trip, a BibleScholar reference slice export + guard, a control‑plane metrics/widgets export + guard, an LM insights slice around `/api/lm/indicator` + `/lm-insights`, or a router + `math_verifier` run).
  - **MANDATORY: Add browser verification (`make browser.verify` / `make atlas.webproof`) whenever Atlas or WebUI pages are involved. Cursor MUST perform browser verification proactively without waiting for user reminders. Use `browser_snapshot` and `browser_take_screenshot` to verify all UI components before completing the task.**

- **Phase advancement discipline**:
  - Phase/PLAN status is driven **only** by `MASTER_PLAN.md` / `share/MASTER_PLAN.md` / `NEXT_STEPS.md`.
  - “Next Milestone” banners (for example, *Phase 12 advanced pattern mining capabilities*) are **future guidance**, not instructions to start work.
  - PM must not advance to Phase 12 (or any future phase) solely because it is labeled as “Next Milestone” without the preceding Phases’ hermetic + live gates being explicitly marked complete.

**Minimum evidence per PR session:**

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

### Live vs Hermetic Runs (DB + LM Posture)

Once the project has been brought up at least once with **real DB and LM services running** (Postgres + LM Studio/Ollama), Cursor Auto must assume that:

- **Hermetic/HINT-only runs are not enough to call a feature “done”** if that feature touches DB or LM.
- For any PLAN/Phase item that exercises DB or LM (pipelines, BibleScholar, Knowledge MCP, control-plane exports, LM router, etc.):
  - First run the hermetic/HINT-mode checks (smokes, guards, unit tests) to keep CI/dev safe.
  - Then run at least one **live DB‑on + LM‑on** execution of the relevant flow (for example:
    - `make reality.green` / `make bringup.live`,
    - A small `make book.go` run,
    - A real BibleScholar interaction,
    - A Knowledge MCP query against `mcp.v_catalog`).
  - Treat `db_off` / `lm_off` in that live step as a **failure to be investigated**, not “correct hermetic behavior”.
- Cursor Auto must not mark a PLAN/Phase item as ✅ COMPLETE or update `MASTER_PLAN.md` / `share/MASTER_PLAN.md` / `NEXT_STEPS.md` to “Complete” on the basis of hermetic evidence alone when live DB/LM usage is part of the design.
- If live tests cannot be executed (DB/LM genuinely unavailable), Cursor Auto must:
  - Surface that explicitly in the Evidence / Next gate blocks,
  - Leave the item as blocked/partial rather than complete,
  - Propose a clear follow-up gate (“Run live DB+LM flow once services are up”).

**GitHub PR policy for automated tools:**

* If `gh pr checks <N> --required` is **all SUCCESS** → non-required automated reviews are **advisory only**.
* Cursor must **say that** in the output:

  > "Required checks are green; automated review is advisory per AGENTS.md and RULE 051."

* Cursor must prefer **standard merge**:

  ```bash
  gh pr merge <N> --squash
  ```

  when checks are green.

**Fumbling prevention:**

* Do **not** re-ask for repo location if `git rev-parse --show-toplevel` already succeeded in this session.
* Do **not** re-run discovery (`gh pr list …`) more than once per handoff unless the previous output showed conflicts.
* Do **not** propose alternative tooling (Black, isort, flake8) — SSOT is `ruff`.
* **File Verification (Rule-046)**: All file operations MUST verify existence first using explicit checks (`test -f`, `os.path.exists`, `head`) before reading/writing. Missing critical files emit LOUD FAIL per Rule-039 (no auto-creation, fail-closed). Treat missing critical files as infra/contract breach.
* **Browser Verification (Rule-051 + Rule-067)**: When modifying `docs/atlas/*` HTML, CSS, or visual artifacts, browser verification is **mandatory**. Use `make browser.verify` or follow `docs/runbooks/ATLAS_VISUAL_VERIFICATION.md`. Screenshots must be saved to `evidence/webproof/` and included in PR evidence. **CRITICAL: Cursor MUST perform browser verification proactively for ANY UI/visual work without waiting for user reminders. This is a mandatory workflow step, not optional.**

## External PM / Planning Agents (Provider-Agnostic)

External planning agents (Gemini CLI, Codex, Granite local agents, or any other model) are allowed to act as the PM implementation engine **only** when they follow the same governance and SSOT rules as pmagent:

- **Required view of the repo**:
  - The agent must be started with its working directory at the **repo root** and must be able to read:
    - `AGENTS.md` (this file),
    - `RULES_INDEX.md`,
    - `.cursor/rules/*.mdc` (especially 050, 051, 052, 062),
    - `docs/SSOT/PM_CONTRACT.md`,
    - `docs/SSOT/MASTER_PLAN.md`,
    - `NEXT_STEPS.md`,
    - And the relevant directory‑level `AGENTS.md` files for the areas it is modifying.
  - If any of these are missing or unreadable, the agent must **fail‑closed** and ask the operator to fix the environment instead of proceeding with partial context.

- **Planning truth sources (read‑only):**
  1. `docs/SSOT/PM_CONTRACT.md`,
  2. `docs/SSOT/MASTER_PLAN.md` (Active Development Workstreams + PLAN checklists),
  3. `NEXT_STEPS.md` (latest Next Gate / Next Steps),
  4. `.cursor/rules/` governance files (at minimum 050, 051, 052, 062),
  5. Directory‑level `AGENTS.md` files and relevant SSOT/runbooks (for example, `agentpm/plan/AGENTS.md`, `agentpm/reality/AGENTS.md`, `docs/SSOT/CAPABILITY_SESSION_AI_TRACKING_MAPPING.md`).

- **Output shape for PM decisions:**
  - All external PM agents must speak in the same 4‑block OPS format:
    - **Goal**, **Commands**, **Evidence to return**, **Next gate**.
  - The **Commands** block must target **pmagent and Make** (for example, `pmagent plan next --with-status`, `pmagent plan reality-loop --track-session --dry-run-command "make book.go"`, `pmagent plan history`, `pmagent reality validate-capability-envelope ...`) and the standard OPS bundle (ruff, smokes, `make reality.green`), not ad‑hoc shell one‑offs.

- **No direct DB / network access:**
  - External planning agents must treat the file system (SSOT docs, `evidence/pmagent/` envelopes, share/ exports) as primary.
  - Any DB or LM usage is mediated by existing commands (`pmagent reality-check check`, `make reality.green`, etc.) and must respect `db_off` / `lm_off` modes.

## Rules (summary)
- Normalize Hebrew: **NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC**
- Mispar Hechrachi; finals=regular. Surface-form gematria with calc strings.
- Ketiv primary; variants recorded with `variant_type`; store span_start/end for instances.
- Batches default to 50; abort + `review.ndjson` on failure; `ALLOW_PARTIAL=1` override logs manifest.
- Default edges: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags.
- Layouts persisted with (algorithm, params_json, seed, version). New params → new layout id.
- Checkpointer: `CHECKPOINTER=postgres|memory` (memory default); Postgres requires `GEMATRIA_DSN`.
- GitHub operations: Use MCP server for issues/PRs/search; confirm ownership; search before creating; use Copilot for AI tasks.

### Edge reranking & classification (Phase-10)
All exported edges now carry a `rerank` score and an `edge_strength = 0.5*cos + 0.5*rerank`.
Edges are classified as **strong** (≥0.90), **weak** (≥0.75), or **other**.
Counts are emitted to `share/eval/edges/edge_class_counts.json` for telemetry.
- **Make Target**: `make eval.reclassify` — Runs `scripts/eval/reclassify_edges.py` to generate edge class counts from `exports/graph_latest.json` (or `share/eval/edges/edge_inputs.json` if present). Thresholds configurable via `EDGE_STRONG` (default 0.90) and `EDGE_WEAK` (default 0.75). Hermetic: emits HINT if `graph_latest.json` is missing (empty-DB/CI runs).
- **Ollama Rerank Failure Handling**: Ollama rerank adapter (`agentpm/adapters/ollama.py`) implements robust failure handling:
  - **HTTP errors (404, 500, etc.)**: Raises `OllamaAPIError` with `error_type="http_error"`; rerank functions catch and fall back to `embedding_only`, then equal scores (0.5) if that also fails
  - **Connection errors & timeouts**: Raises `OllamaAPIError` with `error_type="connection_error"` or `"timeout"`; same fallback chain
  - **JSON parse errors**: Falls back to `embedding_only` (existing behavior)
  - **Pipeline resilience**: Rerank failures never crash the pipeline; HINT-level warnings logged; `make eval.reclassify` remains valid even when rerank fails (uses available edge_strength values)
  - **Test coverage**: `tests/unit/test_ollama_rerank_failures.py` (8 tests) validates all failure modes

### SSOT Blend Validation (Phase-10)
Hermetic validation enforces `edge_strength = α*cosine + (1-α)*rerank_score` contract (Rule-045).
- **Validator**: `scripts/eval/validate_blend_ssot.py` (non-fatal HINTs only)
- **Field aliases**: Accepts SSOT names first, then legacy (`similarity`→`cosine`, `rerank`→`rerank_score`, `strength`→`edge_strength`)
- **Exporter**: `scripts/export_graph.py` emits SSOT field names with proper blend computation
- **Reclassifier**: `scripts/eval/reclassify_edges.py` prefers SSOT edge_strength for classification
- **Defaults**: `EDGE_ALPHA=0.5`, `BLEND_TOL=0.005`
- **Artifacts**: `share/eval/edges/blend_ssot_report.json` and `.md` (deterministic)
- **Integration**: Wired into `ops.verify` as non-fatal validation step

### Rerank & Blend (SSOT)
- Blend thresholds are enforced via HINT on main and STRICT on tags.
- Config: `configs/rerank_blend.json` (env overrides `RERANK_THRESHOLD_HINT/STRICT`)
- Guard: `guard.rerank.thresholds` (HINT on main; STRICT when `STRICT_RERANK_THRESH=1`)
- Artifacts: `share/eval/rerank_blend_report.json`, `evidence/guard_rerank_thresholds.json`
- CI: STRICT step gated by `vars.STRICT_DB_MIRROR_CI` (same switch as dbmirror/AI-tracking).

### Hints Envelope (Enforcement Bridge - Rule-026)
Runtime hints are collected and wrapped in structured envelopes for persistence and auditability.
- **Collection**: Hints collected in `PipelineState.hints` during pipeline execution
- **Wrapping**: `wrap_hints_node` wraps hints into envelope structure: `{type: "hints_envelope", version: "1.0", items: [...], count: N}`
- **Persistence**: Hints envelope included in `graph_latest.json` metadata for export validation
- **Validation**: `rules_guard.py` validates hints envelope structure in exports (non-fatal, encouraged for PRs)
- **Purpose**: Enables determinism and auditability without breaking resumable pipeline design

## Integrated Pipeline Architecture

The Gemantria system now features a fully integrated pipeline that coordinates all components from data extraction through analysis and visualization.

### Pipeline Flow

```
Noun Extraction → Enrichment → Math Verification → Network Building → Schema Validation → Analysis → Export
     ↓              ↓              ↓                    ↓                    ↓             ↓         ↓
collect_nouns → enrichment → math_verifier → network_aggregator → schema_validator → analysis → export_graph
```

### Core Components

#### Main Pipeline (`src/graph/graph.py`)
- **LangGraph orchestration** with 8 integrated nodes (includes math_verifier)
- **Qwen health gate** enforcement (fail-closed)
- **State persistence** via Postgres/memory checkpointer
- **Comprehensive logging** and error handling
- **Math verification** runs automatically after enrichment to verify gematria calculations

#### Pipeline Nodes
1. **collect_nouns**: Extract nouns from Bible database
2. **validate_batch**: Apply size and quality gates
3. **enrichment**: AI-powered theological analysis
4. **math_verifier**: Numeric verification of gematria calculations using MATH_MODEL (NEW)
5. **confidence_validator**: Quality threshold enforcement
6. **network_aggregator**: Semantic embeddings and relationships
7. **schema_validator**: JSON schema validation
8. **analysis_runner**: Graph analysis and export

#### Book Processing (`scripts/run_book.py`)
- **Chapter orchestration** with stop-loss and resume
- **Deterministic seeding** for reproducible runs
- **Service validation** before inference
- **Integrated with main pipeline** via orchestrator

#### Unified Orchestrator (`scripts/pipeline_orchestrator.py`)
- **Single entry point** for all pipeline operations
- **Coordinated workflows** (pipeline → analysis → export)
- **JSON output** for automation and monitoring
- **Error aggregation** and status reporting

### Usage Patterns

#### Quick Start
```bash
# Run complete integrated pipeline
make orchestrator.full BOOK=Genesis

# Run main pipeline only
make orchestrator.pipeline BOOK=Genesis

# Run analysis suite
make orchestrator.analysis OPERATION=all
```

#### Book Processing
```bash
# Plan book processing
make book.plan

# Dry run (validate services)
make book.dry

# Execute full book
make book.go

# Stop after N chapters
make book.stop N=5

# Resume from interruption
make book.resume
```

#### Schema Validation
```bash
# Validate all schemas
make schema.validate

# Validate specific exports
python scripts/eval/jsonschema_validate.py exports/graph_latest.json schemas/graph_output.schema.json
```

### Integration Benefits

- **End-to-end automation** from raw data to visualization
- **Consistent error handling** across all components
- **Unified logging** and monitoring
- **Schema enforcement** prevents data corruption
- **Modular architecture** allows component testing
- **Orchestrator abstraction** simplifies complex workflows

### Quality Gates

- **Schema validation** ensures data integrity
- **Integration tests** verify component interactions
- **Makefile targets** provide consistent interfaces
- **Hermetic CI** with conditional validation
- **Comprehensive logging** enables debugging

## How agents should use rules

* Always-Apply triad lives in `.cursor/rules/050-ops-contract.mdc`, `.cursor/rules/051-cursor-insight.mdc`, and `.cursor/rules/052-tool-priority.mdc`.
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
* See .cursor/rules/049-gpt5-contract-v5.2.mdc (alwaysApply).
* Path-scoped rules auto-attach via `globs`.
* One-off procedures live as agent-requested rules (invoke by referencing their `description` in the prompt).
* Any change to rules affecting workflows must update this AGENTS.md and ADRs in the same PR.


<!-- RULES_INVENTORY_START -->
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
<!-- RULES_INVENTORY_END -->

---

## Agentic Pipeline Framework (Orchestrator-Only)

**Canonical path:** `python3 scripts/pipeline_orchestrator.py pipeline --book "$BOOK" [--nouns-json ...]`

- Granular `make graph.build` / `graph.score` targets remain as compatibility shims and call the orchestrator.
- Resuming from enriched nouns is supported; the network aggregator now prefers `enriched_nouns` and preserves pipeline `ts`.
- Use `CHECKPOINTER=memory` for local deterministic runs; Postgres checkpointer requires `GEMATRIA_DSN`.
- **Note:** The orchestrator does **not** accept this flag.
  - Forbidden flag: `--limit`; use book-scoped runs for smaller workloads.

**Fallback mode**  
Set `NETWORK_AGGREGATOR_MODE=fallback` to build a graph without LM/pgvector.  
The orchestrator persists `exports/graph_latest.json` and `exports/graph_stats.json` directly from memory.  
`make analytics.export` prefers this fast-lane file when present; otherwise it falls back to the DB export.

### Timestamp Standard (RFC3339 / ISO-8601)
- All exported artifacts MUST stamp `generated_at` as RFC3339 timestamps.
- Applies to: `exports/graph_latest.json` and `exports/graph_stats.json`.
- Fast-lane metadata: `metadata.source="fallback_fast_lane"` is required when the orchestrator persists graph without DB round-trip.
- Guard: stats timestamp is verified RFC3339; graph export is covered by schema guard and will emit a HINT if missing.
- `guards.all` includes `guard.graph.generated_at` (HINT by default; set `STRICT_RFC3339=1` for strict).
- CI policy: **HINT-only** (`STRICT_RFC3339=0`) on main/PRs; **STRICT** (`STRICT_RFC3339=1`) on release tags/branches.

### TS Sandbox PoC (ADR-063)
- Gated by `CODE_EXEC_TS=0` (default = OFF). Python/LangGraph remains the operative path.
- `make sandbox.smoke` is gate-aware and runs hermetically when enabled; otherwise clearly SKIPs.

**Goal:** Take raw biblical text → discover nouns (AI-first) → enrich theology → build/score graph → verify against SSOT → export analytics/report → ship to UI, with self-healing guards and governance.

### Core Agents (Production Path)

#### 1. Ingestion Agent (Text→Shards)
- **Purpose:** Pulls raw Hebrew text, splits into stable shards/chunks, dedups, stamps source refs
- **Reads:** Corpus store or DB
- **Writes:** `share/corpus/{book}/shards.jsonl`
- **Requirements:** Deterministic chunking; include `ref`, `offset`, `text`
- **System Prompt:**
  > You split source text into semantically coherent shards with stable offsets. Never interpret. Output JSONL with fields: {ref, offset, text}. No omissions. Max shard ~1k chars.
- **Task Prompt:**
  > Split the attached {BOOK} raw text into shards. Keep verse boundaries.
- **Make Target:** `make ai.ingest`

#### 2. AI-Noun Discovery Agent (Organic Nouns)
- **Purpose:** Discovers significant nouns from shards; outputs SSOT **ai-nouns** envelope
- **Reads:** `shards.jsonl`
- **Writes:** `exports/ai_nouns.json` (schema `gemantria/ai-nouns.v1`)
- **Requirements:** Populate `noun_id (uuid)`, `surface`, `letters[]`, `gematria`, `class`, `sources[]`, `analysis`
- **System Prompt:**
  > Discover Hebrew nouns directly from shards. Produce only nouns with clear lexical evidence. Return interim reasoning in `analysis`, but keep `surface/letters/gematria/class/sources` factual. Conform to JSON Schema gemantria/ai-nouns.v1 exactly; never add extra fields.
- **Task Prompt:**
  > From these shards for {BOOK}, find significant nouns; compute letters & gematria; classify person/place/thing; attach `{ref,offset}` sources. Emit one JSON object: {schema:"gemantria/ai-nouns.v1",book,generated_at,nodes:[...]}.
- **Make Target:** `make ai.nouns`

#### 3. Enrichment Agent (Theology & Context)
- **Purpose:** Expands each noun with theological context, cross-refs, motifs
- **Reads:** `exports/ai_nouns.json`
- **Writes:** `exports/ai_nouns.enriched.json` (same schema + `analysis.theology` block)
- **Requirements:** Never mutate identifiers; add only under `analysis`
- **System Prompt:**
  > Enrich each noun with concise, citable theological notes. Do not invent sources; describe patterns and canonical motifs. Add to `analysis.theology` with fields {themes[], cross_refs[], notes}.
- **Task Prompt:**
  > For each noun in {BOOK}, add `analysis.theology` with 1–3 themes and short notes. Keep JSON valid and schema-conformant.
- **Make Target:** `make ai.enrich`

#### 4. Graph Builder Agent (Edges from Nouns)
- **Purpose:** Turns nouns/enrichment into a typed relation set; writes a single **graph** envelope
- **Reads:** `ai_nouns.enriched.json`
- **Writes:** `exports/graph_latest.json` (nodes/edges schema `gemantria/graph.v1`)
- **Requirements:** Node keys = `noun_id`; edge types = `semantic|cooccur|theology|other`; weight ∈ [0,1]
- **System Prompt:**
  > Build a concept graph from nouns and enrichment. Node id is noun_id. Create typed edges with rationale in `analysis.edge_reason` (kept internal if not exported). Normalize weights to [0,1].
- **Task Prompt:**
  > For {BOOK}, output {schema:"gemantria/graph.v1",nodes:[{id,lemma?,surface,book}],edges:[{src,dst,type,weight}]} using only noun_ids present.
- **Make Target:** `make graph.build`

#### 5. Rerank/Edge-Strength Agent
- **Purpose:** Computes cosine/rrf/rerank score and blends to edge strength
- **Reads:** `graph_latest.json`
- **Writes:** `exports/graph_latest.scored.json`
- **Requirements:** `edge_strength = α*cosine + (1-α)*rerank_score`, thresholds: strong ≥0.90, weak ≥0.75
- **System Prompt:**
  > Score edges using embeddings+reranker. Output same graph with added {cosine, rerank_score, class}.
- **Task Prompt:**
  > Score edges for {BOOK} with α={ALPHA}. Classify into strong/weak/very_weak.
- **Make Target:** `make graph.score`

#### 6. Analytics & Report Agent
- **Purpose:** Stats, patterns, temporal, forecast + Markdown report
- **Reads:** `graph_latest.scored.json`
- **Writes:** `exports/graph_stats.json`, `graph_patterns.json`, `temporal_patterns.json`, `pattern_forecast.json`, `report.md`
- **System Prompt:**
  > Produce concise analytics JSONs per SSOT schemas; generate a short Markdown report for humans. Never change upstream data.
- **Task Prompt:**
  > Compute degree/betweenness histograms, top-k concepts, motif patterns, and a naive forecast. Emit JSON files + a 1-page report.
- **Make Target:** `make analytics.export`

#### 7. Guard/Compliance Agent (Fail-Closed)
- **Purpose:** Validates schema conformance, Hebrew fields, orphan checks, ADR mention
- **Reads:** All exports + PR body context
- **Writes:** Status only; blocks on failure
- **System Prompt:**
  > You are the policy gate. If any JSON violates its schema, any edge orphaned, Hebrew missing, or PR lacks ADR note when touching infra/data, return a single FAILURE line with details. Otherwise return GUARD_OK.
- **Task Prompt:**
  > Validate {list of files} against schemas and invariants. Print GUARD_OK or specific FAIL_* lines.
- **Make Target:** `make guards.all`

#### 8. Release/Operator Agent
- **Purpose:** Assembles artifacts, updates CHANGELOG, tags release, posts summary
- **Reads:** All export JSONs + report
- **Writes:** Git tag/release notes with artifact manifest
- **System Prompt:**
  > Prepare release notes with artifacts and checksums. Summarize notable graph changes and known limitations. No speculation.
- **Task Prompt:**
  > Create notes for {BOOK} including artifact list and acceptance checklist.
- **Make Target:** `make release.prepare`
- **Before tagging, run the Atlas DSN-on proof:**
  - `make atlas.proof.dsn` (read-only; stays grey/HINT if DB is unreachable)
  - Tag only after diagrams populate from real telemetry and tests pass.
- **Dev-only demo data for Atlas visual proof:**
  - Seed+proof: `DEMO_DB=1 make atlas.demo.proof` (requires `GEMATRIA_DSN`, writes demo rows)
  - Cleanup: `DEMO_DB=1 make atlas.demo.reset`
  - Safety: DEMO seed is **dev-only**; CI/release must **not** invoke these targets.

#### 13. Reality Check Agent (System Validation)
- **Purpose:** Unified environment validation across env/DSN, DB/control plane, LM/models, exports, and eval smokes with HINT/STRICT modes
- **Reads:** Environment variables, DSN configs, DB health, LM status, control plane exports, eval smoke targets
- **Writes:** JSON verdict to stdout, human summary to stderr
- **Requirements:** Hermetic behavior (works without DB/LM), HINT/STRICT mode support, comprehensive but single-command validation
- **System Prompt:**
  > You are the Reality Check Agent. Validate the entire system environment and report a structured verdict. Use HINT mode for development (tolerates missing non-critical components) and STRICT mode for production (all components must be OK).
- **Task Prompt:**
  > Run comprehensive system validation in {MODE} mode. Check env/DSN, DB/control plane, LM/models, exports, and eval smokes. Return JSON verdict with overall_ok flag and detailed component status.
- **pmagent Command:** `pmagent reality-check check --mode hint|strict [--json-only] [--no-dashboards]`
  - **HINT mode (hermetic / PR):** DB/env must be correct; LM/exports/eval may be offline and produce hints without failing the run.
  - **STRICT mode (live-ready):** DB, control-plane, and LM providers must be reachable; failures are treated as errors and reflected in `overall_ok=false`.
  - **Unified bringup:** `make bringup.live` composes `pmagent reality-check check --mode strict --no-dashboards` with `make bringup.001` to provide a single live bringup gate for humans.

#### 14. Autopilot Agent (Backend Stub)
- **Purpose:** Handles Orchestrator Shell intents via HTTP API
- **Reads:** Intent payloads from Shell
- **Writes:** Structured plan responses (stubbed in Phase B)
- **System Prompt:** (Future) Map user intent to guarded pmagent commands.
- **pmagent Command:** `pmagent autopilot serve --port 8006`
  - **Phase B:** Stubbed response (accepted=False, status="planned")
  - **Logging:** Logs intents to stdout/logs for analysis

### Support Agents (Resilience & Governance)

#### 9. Incident Triage Agent
- **Purpose:** Watches logs/guards; files issues with minimal repro
- **System Prompt:** Detect root cause; propose 1-shot fix or open issue with repro, scope, impact.

#### 10. Data Steward Agent
- **Purpose:** Curates source catalogs/refs; manages alignment table to bible_db (optional)
- **System Prompt:** Ensure `sources[]` are consistent, resolvable, and deduped; maintain mapping tables with confidence.

#### 11. Performance/Batching Agent
- **Purpose:** Tunes batch sizes, caching, and provider selection under constraints
- **System Prompt:** Maximize throughput while keeping deterministic outputs; never change output shape.

#### 12. ADR Scribe Agent
- **Purpose:** Writes/updates ADRs when architecture or contracts change
- **System Prompt:** Produce succinct ADRs with Context/Decision/Consequences/Verification; link PRs; update index.

### Agentic Workflow Architecture

#### Observe → Decide → Act Loops
- **Immutable Handoff Artifacts:**
  - `shards.jsonl` → `ai_nouns.json` → `ai_nouns.enriched.json` → `graph_latest.json` → `graph_latest.scored.json` → analytics JSONs + `report.md`
- **Single SSOT per Stage:** `gemantria/ai-nouns.v1`, `gemantria/graph.v1`, analytics schemas in `docs/SSOT/`
- **Fail-Closed Guards:** Schema validation + invariants + orphan checks between every stage

#### Governance & Quality Gates
- **ADR Required:** On contract changes; guards run in CI and locally via `make`
- **Idempotence:** Reruns on same inputs produce identical outputs (timestamps excluded)
- **Explicit Handoffs:** Each agent writes complete envelope; next agent only reads that envelope
- **Observability:** Each agent logs machine-readable summary to `share/evidence/`
- **Recovery:** Triage agent opens issue and suggests exact `make` target to rerun failed stage

### Make Targets (Agent Entry Points)

```makefile
ai.ingest:                 # Ingestion Agent (shards)
ai.nouns:                  # Discovery Agent → ai_nouns.json
ai.enrich:                 # Enrichment Agent → ai_nouns.enriched.json
graph.build:               # Graph Builder → graph_latest.json
graph.score:               # Reranker → graph_latest.scored.json
analytics.export:          # Stats/Patterns/Temporal/Forecast + report.md
guards.all:                # Schema + invariants + Hebrew + orphans + ADR
release.prepare:           # Pack artifacts + release notes
bringup.001:               # STRICT bring-up verification (env gate → LM Studio → pipeline → guards → evidence)
dsns.echo:                 # Print redacted DSNs for operator sanity (never prints secrets)
```

**Bring-up 001 (`make bringup.001`):**
- **Purpose:** STRICT verification of complete pipeline from environment setup through evidence capture
- **DSN Precedence:** `.env.local` > `.env` > centralized loader (`scripts.config.env`) > defaults
- **Requirements:** `BIBLE_DB_DSN` (RO) and `GEMATRIA_DSN` (RW) must be available
- **Posture:** Enforces `CHECKPOINTER=postgres` and `ENFORCE_STRICT=1` for durable checkpoints
- **Steps:** (1) Environment hard-gate, (2) Always-Apply triad verification, (3) Inference provider readiness (LM Studio or Ollama), (4) Minimal pipeline run, (5) Guards (fail-closed), (6) Evidence capture
- **Output:** `evidence/bringup_001/run.log` with full execution trace and timing

**DSN Helper (`make dsns.echo`):**
- **Purpose:** Operator sanity check - prints redacted DSNs without exposing secrets
- **Behavior:** Checks `.env.local` first, then `.env`, then centralized loader; prints redacted connection strings
- **Security:** Never prints actual credentials - uses `REDACTED@` pattern for user/password portions
- **Output:** Shows effective `CHECKPOINTER` and `ENFORCE_STRICT` values

### Handoff Contracts

- **Discovery → Enrichment:** `exports/ai_nouns.json` (ai-nouns.v1)
- **Enrichment → Graph:** `exports/ai_nouns.enriched.json` (same schema + theology block)
- **Graph → Rerank:** `exports/graph_latest.json` (graph.v1)
- **Rerank → Analytics:** `exports/graph_latest.scored.json`
- **Analytics → Release/UI:** `exports/{graph_stats,graph_patterns,temporal_patterns,pattern_forecast}.json` + `report.md`

### Universal Agent Contract

**System Prelude (attach to every agent):**
> You are the {AGENT_NAME}. You must produce outputs that exactly match the declared SSOT schema. Never change field names or shapes. If a requirement cannot be met, stop and state a single clear reason. Do not proceed with partial/invalid outputs.

### Acceptance Checklist

- [ ] Each agent has a **system** and **task** prompt (above), plus a single `make` target
- [ ] SSOT schemas exist for ai-nouns and graph; analytics schemas pinned
- [ ] Guards pass locally and in CI (`guards.all`)
- [ ] Handoffs are **only** the SSOT envelopes; no hidden side-channels
- [ ] ADR updated if any schema/contract changes

### Now / Next / Later

- **Now:** Wire the `make` targets to current scripts; add `guards.all` chaining all validations
- **Next:** Flip enrichment + graph stages to consume strictly from `ai_nouns(.enriched).json`
- **Later:** Work ADR-032 roadmap (bible_db SSOT) with compat views + dual-export, without touching AI path

---

## Model Routing & Configuration

For detailed prompt templates, routing roles, and MoE-of-MoEs design for the Granite 4.0 + BGE-M3 + Granite Reranker stack, see `Prompting Guide for Our Core LLM models.md`. That guide is a **design-level spec**; this section remains the SSOT for what is currently wired in code.

### 🔧 **Model Routing Map (Who Handles What)**

| Agent                       | Primary model                                            | Why / Purpose                               | Fallback                                  | Non-LLM deps      |
| --------------------------- | -------------------------------------------------------- | ------------------------------------------- | ----------------------------------------- | ----------------- |
| **Ingestion (Text→Shards)** | **none** (code)                                          | deterministic parsing/splitting             | —                                         | —                 |
| **AI-Noun Discovery**       | **christian-bible-expert-v2.0-12b**                      | excels at theological Hebrew noun reasoning | `Qwen2.5-14B-Instruct-GGUF` (general alt) | —                 |
| **Enrichment (Theology)**   | **christian-bible-expert-v2.0-12b**                      | deep doctrinal and contextual enrichment    | `Qwen2.5-14B-Instruct-GGUF`               | —                 |
| **Graph Builder**           | **none** (code)                                          | deterministic edge creation                 | —                                         | —                 |
| **Rerank / Edge Strength**  | **text-embedding-bge-m3** + **qwen.qwen3-reranker-0.6b** | numeric, deterministic rerank blend         | —                                         | cosine + reranker |
| **Analytics & Report**      | **none** (code)                                          | programmatic stats & forecasts              | —                                         | —                 |
| **Guard / Compliance**      | **none** (code)                                          | schema + invariants                         | —                                         | —                 |
| **Release / Operator**      | **none** (code)                                          | changelog + checksum generation             | —                                         | —                 |
| **Incident Triage**         | **Qwen2.5-14B-Instruct-GGUF**                            | broader context understanding for fixes     | `christian-bible-expert-v2.0-12b`         | —                 |
| **Math / Verification**     | **self-certainty-qwen3-1.7b-base-math**                  | numerical & gematria verification           | —                                         | —                 |
| **ADR / Scribe**            | **Qwen2.5-14B-Instruct-GGUF**                            | structured ADR drafting                     | —                                         | —                 |

### 🧩 **Concrete Model Bindings (LM Studio / Ollama)**

**Phase-7E**: Supports both LM Studio and Ollama providers.

```yaml
# LM Studio Profile (Legacy)
models:
  provider: lmstudio
  theology: christian-bible-expert-v2.0-12b
  general: Qwen2.5-14B-Instruct-GGUF
  math: self-certainty-qwen3-1.7b-base-math
  embedding: text-embedding-bge-m3
  reranker: qwen.qwen3-reranker-0.6b

# Ollama Profile (Phase-7F - All Four Slots Ready)
models:
  provider: ollama
  theology: Christian-Bible-Expert-v2.0-12B  # via theology adapter
  local_agent: granite4:tiny-h
  math: self-certainty-qwen3-1.7b-base-math
  embedding: bge-m3:latest  # Ollama: qllama/bge-m3
  reranker: bge-reranker-v2-m3:latest  # Ollama: bona/bge-reranker-v2-m3

routing:
  ingestion: none
  discovery: theology
  enrichment: theology
  graph_build: none
  rerank: [embedding, reranker]
  analytics: none
  guard: none
  release: none
  triage: general
  math: math
  adr: general
```

### ⚙️ **Agent Settings**

```yaml
agent_settings:
  defaults:
    max_tokens: 1024
    temperature: 0.2
    stop: ["```json", "</json>", "\n\n###"]
    seed: 42

  discovery:
    model: ${models.theology}
    temperature: 0.15
    system: >
      Discover Hebrew nouns organically from canonical text shards.
      Emit ai-nouns.v1 JSON only; preserve Hebrew; compute letters + gematria deterministically.
    task: >
      From shards for {BOOK}, output {"schema":"gemantria/ai-nouns.v1","book":...,"nodes":[...]}.
      Each node: {noun_id, surface, letters[], gematria, class, ai_discovered:true, sources[], analysis:{notes}}.

  enrichment:
    model: ${models.theology}
    temperature: 0.35
    system: >
      Add concise, citable Christian-theology context. Do not alter identifiers or base fields.
      Write only to analysis.theology: {themes[], cross_refs[], notes}.
    task: >
      Enrich each noun in ai_nouns.json for {BOOK}. Keep JSON valid; never add top-level keys.

  rerank:
    embed_model: ${models.embedding}
    reranker_model: ${models.reranker}
    formula: "edge_strength = EDGE_ALPHA*cosine + (1-EDGE_ALPHA)*rerank_score"
    classes: {"strong": ">=0.90", "weak": ">=0.75", "very_weak": "else"}

  math:
    model: ${models.math}
    temperature: 0.0
    system: >
      Verify gematria and numeric relationships deterministically.
      Return verified values or corrections only.
    integration: >
      Math verifier runs automatically in the pipeline after enrichment.
      Standalone: `make ai.verify.math` (reads exports/ai_nouns.enriched.json).
      Adds math_check to each noun: {ok, local_sum, claimed, model, confidence}.

  guard:
    impl: code
    checks:
      - "jsonschema: ai-nouns.v1, graph.v1, analytics schemas"
      - "no orphan edges"
      - "hebrew fields non-empty"
      - "assert_qwen_live passes when ENFORCE_QWEN_LIVE=1"

  release:
    impl: code
    notes:
      include: ["artifacts list", "sha256", "models used", "ADRs touched"]

  adr:
    model: ${models.general}
    temperature: 0.2
    system: >
      Write ADRs with Context, Decision, Consequences, Verification. Link PRs and schemas.
```

### 🧾 **Minimal .env Keys**

**Phase-7E**: Choose provider (lmstudio or ollama) and configure accordingly.

```dotenv
# Provider Selection (Phase-7E)
INFERENCE_PROVIDER=lmstudio  # or "ollama" for Granite 4.0

# LM Studio Configuration
OPENAI_BASE_URL=http://127.0.0.1:9994/v1
LM_STUDIO_ENABLED=1

# Ollama Configuration (when INFERENCE_PROVIDER=ollama)
OLLAMA_BASE_URL=http://127.0.0.1:11434

# Model Configuration (provider-agnostic)
ENFORCE_QWEN_LIVE=1
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
LOCAL_AGENT_MODEL=qwen/qwen3-8b  # or granite4:tiny-h for Ollama
MATH_MODEL=self-certainty-qwen3-1.7b-base-math
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
ANSWERER_MODEL_PRIMARY=christian-bible-expert-v2.0-12b
ANSWERER_MODEL_ALT=Qwen2.5-14B-Instruct-GGUF
EDGE_ALPHA=0.5
```

### 🔍 **Command-to-Function Mapping**

| Command                 | Function                    | Model                            |
| ----------------------- | --------------------------- | -------------------------------- |
| `make ai.nouns`         | `discover_nouns_for_book()` | THEOLOGY_MODEL                   |
| `make ai.enrich`        | enrichment loop             | THEOLOGY_MODEL                   |
| `make ai.verify.math`   | gematria verification       | MATH_MODEL                       |
| `make graph.build`      | edge creation               | code                             |
| `make graph.score`      | rerank blend                | EMBEDDING_MODEL + RERANKER_MODEL |
| `make analytics.export` | reports                     | code                             |
| `make guards.all`       | schema checks               | code                             |
| `make release.build`    | artifact summary            | code                             |

### ✅ **Acceptance Checklist**

- [ ] `.env` keys match live models above
- [ ] `assert_qwen_live()` passes for all four models
- [ ] AI-noun + Enrichment schemas validate (guards green)
- [ ] Rerank outputs `edge_strength` + `class`
- [ ] Release notes list model versions used

---

## Editor Baseline (Cursor 2.0)

**Purpose:** speed up surgical PR work while preserving SSOT governance.

### Settings (per developer)

- **Multi-Agents:** **Enabled**; set parallel agents to **4–8** as hardware allows. Cursor isolates agents via **git worktrees / remote machines** to avoid file conflicts. :contentReference[oaicite:1]{index=1}

- **Models:** **Plan with your top reasoner**; **Build with *Composer*** (Cursor's agentic coding model, ~**4× faster**, most turns **<30s**). :contentReference[oaicite:2]{index=2}

- **Browser for Agent:** Allowed **in-editor** for research/design only (CI remains hermetic). Browser is **GA** in 2.0 and can forward DOM to the agent. :contentReference[oaicite:3]{index=3}

- **Sandboxed Terminals:** Prefer sandboxed agent shells (no network) where supported; keep our CI "no network" invariant regardless. :contentReference[oaicite:4]{index=4}

### Team Rules / Commands

- SSOT remains in-repo (`.cursor/rules/*.mdc`). Optional dashboard **Team Rules/Commands** may drift or fail to sync; if used, generate them **from** the repo and treat dashboard as a mirror only. :contentReference[oaicite:5]{index=5}

### Guardrails we keep

- **No outbound network in CI.** Use hermetic validators and artifacts-first routing.

- **No `share/**` writes in CI.** Route CI outputs to `_artifacts/**`.

- **Ruff-format is the single formatter.** Workflows should run `ruff format --check .` and `ruff check .`.

### Codex CLI Integration

- Optional, local-only tool for running terminal agents with fresh context.
- CI-gated: Exits early unless `ALLOW_CODEX=1`.
- No share writes, respects ruff formatting.
- See `docs/runbooks/CODEX_CLI.md` for installation, usage, and examples.
- Quick start: `make codex.task TASK="your instruction"`

### Runbook: PR Gating (required checks only)

**Note:** Ruff formatting applied during rebase conflict resolution in PR #70.

- **Script:** `scripts/pr_gate.sh <pr-number>`

- **Purpose:** Gate PR merges by required checks only (connector-less strategy)

- **Required checks:** `ruff` (formatting + linting), `build` (CI pipeline)

- **Usage:**
  ```bash
  # Check if PR #123 is ready to merge
  ./scripts/pr_gate.sh 123

  # In CI: exits 0 if mergeable, 1 if not ready
  ```

- **Branch protection:** Main branch requires reviews from CODEOWNERS + required checks

### Runbook: Codex CLI (optional, local-only)

- **Docs:** `docs/runbooks/CODEX_CLI.md`

- **Enable locally:** `npm i -g @openai/codex && codex login`

- **Config:** copy `.codex/config.example.toml` to `~/.codex/config.toml`

- **Use:** `make codex.task TASK="List last 5 commits; propose 2-line release note."`

- **Gating:** **Off in CI** by default; to allow in CI, set `ALLOW_CODEX=1` (not recommended).

---

# 🧭 Gemantria — OPS Contract v6.2.3

**Mode:** OPS MODE only (no small talk, no speculation without evidence)
**Scope:** Gemantria repository and its subprojects (pipeline, exports, viz)
**Authority chain:** Rules 039 → 041 → 046 → 050 → 051 → **052 (Tool Priority & Context Guidance)**

## 1 · Activation Rule

I operate *only if all three* are true:

1. **Repo present** → `git rev-parse --show-toplevel` succeeds.
2. **Governance docs present** → `AGENTS.md` and `RULES_INDEX.md` exist.
3. **Quality SSOT available** → `ruff format --check . && ruff check .` runs.

If any is missing → **FAIL-CLOSED (LOUD FAIL)**.

## 2 · LOUD FAIL Pattern

Emit **exactly** if a required tool/context is missing:

```
LOUD FAIL
governance: Gemantria OPS v6.2
tool: <name>              # e.g., codex, gemini, gh, local-make
action: <what you tried>
args: <key args>
error: <short reason>
fallback:

* git pull --ff-only
* make share.sync
* ruff format --check . && ruff check .
```

## 3 · Tool Priority & File References

Cursor **must** declare the tool and files used.

### Tool Order

1. **Local + GH tools** (`git`, `make`, `gh pr …`)
2. **Codex** — edits/patches/re-writes
   *If unavailable → print `Codex disabled (401)` and fallback*
3. **Gemini / MCP** — long-context reasoning or large docs

### Files Referenced

* `AGENTS.md`
* `RULES_INDEX.md`
* `.cursor/rules/050-ops-contract.mdc`
* `.cursor/rules/051-cursor-insight.mdc`
* `src/**/AGENTS.md` (scoped to relevant module)

### Example Cursor Header

```
governance: Gemantria OPS v6.2.3
tool-priority:
  1. local+gh
  2. codex (if available)
  3. gemini/mcp (for long files)
   files-referenced:
* AGENTS.md
* RULES_INDEX.md
* .cursor/rules/050-ops-contract.mdc
* .cursor/rules/051-cursor-insight.mdc
* .cursor/rules/053-idempotence.mdc
  output-shape: 4 blocks (Goal, Commands, Evidence, Next gate)
  ssot: ruff format --check . && ruff check .
```

## 4 · Context-Thinning Rule

If overflow, **reduce** to:

1. `AGENTS.md`
2. `RULES_INDEX.md`
3. `.cursor/rules/050-ops-contract.mdc`
4. `.cursor/rules/051-cursor-insight.mdc`
5. The single relevant submodule `AGENTS.md`

Do **not** reload the entire repo once this subset is set.

## 5 · Evidence-First Protocol

Before proposing changes:

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

For PR work:

```bash
gh pr view <N> --json number,title,headRefName,baseRefName,state,author,reviews,reviewDecision,mergeable,mergeStateStatus,checks
gh pr checks <N> --required --json name,state
```

## 6 · Output Shape (4-Block Standard)

1. **Goal** — one sentence defining the action.
2. **Commands** — runnable shell/gh/make lines only.
3. **Evidence to return** — numbered list of expected outputs.
4. **Next gate** — what to do after I see the evidence.

   Each command block begins with:

```
# source: AGENTS.md + RULES_INDEX.md + .cursor/rules/050 + .cursor/rules/051
```

## 7 · SSOT for Quality

```bash
ruff format --check . && ruff check .
```

If ruff fails → stop and request the last 60–200 lines.

## 8 · Hermetic Test Bundle

```bash
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

If DB/services down → "correct hermetic behavior."

## 9 · Non-Required Automated Reviews

If required checks are green:

> "Required checks are green; non-required automated reviews are **advisory only** per AGENTS.md and Rule 051."

## 10 · CI Naming-Conflict Clause

If duplicate `build` jobs (one pass / one fail):

> "Treat as infra fault. With ruff + smokes green, **admin merge allowed** per Governance v6.2 §10."

## 11 · Handoff / New Chat Rule

On "prepare handoff" or "new chat", output **only** the 4 blocks and include baseline evidence (§5).

## 12 · Dirty-Branch Rule

If `git status -sb` shows dirty on `main`, open hygiene PR first:

```bash
git switch -c ci/hygiene-ruff-$(date +%Y%m%d-%H%M)
ruff format --check . && ruff check .
make ops.verify
make share.sync
git add .
git commit -m "ci: apply ruff/py.fullwave hygiene"
git push -u origin HEAD
gh pr create --title "ci: hygiene (ruff)" --body "Automated hygiene per OPS v6.2"
```

## 13 · Required-Checks Gate

Always emit:

```bash
gh pr checks <N> --required --json name,state \
  --jq 'if length==0 then "NO_REQUIRED_CHECKS" else all(.state=="SUCCESS") end'
```

If `NO_REQUIRED_CHECKS`, say: *"Automated checks present → advisory only (051)."*

## 14 · Fail-Closed on Share

If CI writes to `share/`:

1. Identify script. 2) Explain why it breaks hermetic CI.
2. `make share.sync`. 4) Re-run CI.

## 15 · No Async Promises

Never say "I'll check later" or give time estimates.

Always output commands runnable **now**.

## 16 · Header Banner for OPS Responses

Every OPS reply begins:

> **Governance: Gemantria OPS v6.2.3 (tool-aware, 050 + 051 + 052 active)**

> Then the 4-block format follows.

## 17 · Rule-053 — Idempotent Baseline

Cache baseline evidence by `(branch, HEAD)` for **60 minutes**.

If unchanged, **do not** re-ask for baseline; acknowledge cached evidence.

Emit `HINT[baseline.sha]: <sha>` when using cache.

## 18 · CI Single-Context Requirement

PRs expose **one** required status context: **`build-pr`**.

Use concurrency with `cancel-in-progress: true`.

Duplicate/legacy contexts = **infra fault** (see §10).

## 19 · Internal Guardrails (Branch Protection OFF allowed)

Merges are permitted only when **all** are true:

* **policy-gate** passed (Conventional Commits + signed-commit verification).
* **build-pr** passed.
* ≥ **1 human approval** present.
* Prefer **bot-mediated merge** (queue/automation) over manual "Merge".

## 20 · Security & Supply Chain

* Pin third-party actions to **full commit SHAs** (avoid `@v*` tags).
* Enable **Dependabot** for `github-actions` (weekly).
* Nightly **OpenSSF Scorecard** with SARIF upload to Security tab.

### Summary

* **SSOT:** Ruff
* **Hermetic:** book + eval + exports smokes
* **Reviews:** non-required = advisory
* **Tool Priority:** local+gh → codex → gemini/mcp
* **Files:** AGENTS.md, RULES_INDEX.md, 050, 051 (+ Rule-053)
* **Output:** 4 blocks
* **Failure:** LOUD FAIL v6.2
* **Chain:** 039→041→046→050→051→052→**053**

## Cursor-Specific Guidelines

- Respond in plain English; no structured OPS formats or Governance headers.
- Use tool calls for verification (e.g., read_file for existence checks).
- Paste file contents/head/tail when requested for state confirmation.
- Do not assume—verify first, fail-closed on missing critical files.
- For edits, provide patches/diffs only; no auto-apply without user confirmation.

- **Note:** The orchestrator does **not** accept this flag.
  - Forbidden flag: `--limit`; use book-scoped runs.

- CI policy: **HINT-only** (`STRICT_RFC3339=0`) on main/PRs; **STRICT** (`STRICT_RFC3339=1`) on release tags/branches.

> **Always-Apply:** 050 (OPS/SSOT LOUD-FAIL), 051 (Required-checks advisory), 052 (Tool-priority & evidence-first)
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
- Rule-050
- Rule-051
- Rule-052
<!-- RULES_INVENTORY:BEGIN -->
| ID | File | Title | Status |
|---:|:-----|:------|:-------|
| 000 | `000-ssot-index.mdc` | 000-ssot-index (AlwaysApply) | **Default-Apply** |
| 001 | `001-db-safety.mdc` | Related ADR: ADR-001 (Two-DB Safety) | **Default-Apply** |
| 002 | `002-gematria-validation.mdc` | gematria validation | **Default-Apply** |
| 003 | `003-graph-and-batch.mdc` | graph and batch | **Default-Apply** |
| 004 | `004-pr-workflow.mdc` | References | **Default-Apply** |
| 005 | `005-github-operations.mdc` | References | **Default-Apply** |
| 006 | `006-agents-md-governance.mdc` | AGENTS.md Governance — How agents must use and maintain AGENTS.md | **Default-Apply** |
| 007 | `007-infrastructure.mdc` | infrastructure | **Default-Apply** |
| 008 | `008-cursor-rule-authoring.mdc` | Cursor Rule Authoring Guide | **Default-Apply** |
| 009 | `009-documentation-sync.mdc` | documentation sync | **Default-Apply** |
| 010 | `010-task-brief.mdc` | SHORT BRIEF Format (Always Required) | **Default-Apply** |
| 011 | `011-production-safety.mdc` | Rule 011 — DEPRECATED | **Default-Apply** |
| 012 | `012-connectivity-troubleshooting.mdc` | connectivity troubleshooting | **Default-Apply** |
| 013 | `013-report-generation-verification.mdc` | report generation verification | **Default-Apply** |
| 014 | `014-governance-index.mdc` | Rule 014 — Governance Index (Reserved) | **Default-Apply** |
| 015 | `015-semantic-export-compliance.mdc` | Related ADRs: ADR-015 (JSON-LD & RDF Graph Exports + Visualization Interface) | **Default-Apply** |
| 016 | `016-visualization-contract-sync.mdc` | Rule 016 — DEPRECATED | **Default-Apply** |
| 017 | `017-agent-docs-presence.mdc` | Related ADRs: ADR-013 (Comprehensive documentation synchronization enhancement) | **Default-Apply** |
| 018 | `018-ssot-linkage.mdc` | Related ADRs: ADR-013 (Comprehensive documentation synchronization enhancement) | **Default-Apply** |
| 019 | `019-metrics-contract-sync.mdc` | Metrics Contract Synchronization Rule | **Default-Apply** |
| 020 | `020-ontology-forward-compat.mdc` | Ontology Forward Compatibility Rule | **Default-Apply** |
| 021 | `021-stats-proof.mdc` | Rule 021 — Stats Proof (PR-016/017) | **Default-Apply** |
| 022 | `022-visualization-contract-sync.mdc` | Rule 022 — Visualization Contract Sync | **Default-Apply** |
| 023 | `023-visualization-api-spec.mdc` | Rule 023 — Visualization API Spec | **Default-Apply** |
| 024 | `024-dashboard-ui-spec.mdc` | Rule 024 — Dashboard UI Spec | **Default-Apply** |
| 025 | `025-phase-gate.mdc` | Rule 025 — Multi-Temporal Analytics Enforcement | **Default-Apply** |
| 026 | `026-system-enforcement-bridge.mdc` | Rule 026 — System Enforcement Bridge | **Default-Apply** |
| 027 | `027-docs-sync-gate.mdc` | Rule 027 — Docs Sync Gate | **Default-Apply** |
| 028 | `028-phase-freshness.mdc` | Rule 028 — Phase Freshness | **Default-Apply** |
| 029 | `029-adr-coverage.mdc` | Rule 029 — ADR Coverage | **Default-Apply** |
| 030 | `030-share-sync.mdc` | Share Directory Synchronization (Always Required) | **Default-Apply** |
| 031 | `031-correlation-visualization-validation.mdc` | Rule 031 — Correlation Visualization Validation | **Default-Apply** |
| 032 | `032-pattern-integrity-validation.mdc` | Rule 032 — Pattern Integrity Validation | **Default-Apply** |
| 033 | `033-visualization-api-validation.mdc` | Rule 033 — Visualization API Validation | **Default-Apply** |
| 034 | `034-temporal-suite.mdc` | Rule 034 — Temporal Analytics Suite (Phase 8) | **Default-Apply** |
| 035 | `035-forecasting-spec.mdc` | Rule 035 — Forecasting Spec (DEPRECATED) | **Default-Apply** |
| 036 | `036-temporal-visualization-spec.mdc` | Rule 036 — Temporal Visualization Spec (DEPRECATED) | **Default-Apply** |
| 037 | `037-data-persistence-completeness.mdc` | Rule 037 — Data Persistence Completeness | **Default-Apply** |
| 038 | `038-exports-smoke-gate.mdc` | Rule 038 — Exports Smoke Gate | **Default-Apply** |
| 039 | `039-execution-contract.mdc` | execution contract | **Default-Apply** |
| 040 | `040-ci-triage-playbook.mdc` | ci triage playbook | **Default-Apply** |
| 041 | `041-pr-merge-policy.mdc` | pr merge policy | **Default-Apply** |
| 042 | `042-formatter-single-source-of-truth.mdc` | 042 — Formatter Single Source of Truth (AlwaysApply) | **Default-Apply** |
| 043 | `043-ci-db-bootstrap.mdc` | 043 — CI DB Bootstrap & Empty-Data Handling (AlwaysApply) | **Default-Apply** |
| 044 | `044-share-manifest-contract.mdc` | 044 — Share Manifest Contract (AlwaysApply) | **Default-Apply** |
| 045 | `045-rerank-blend-SSOT.mdc` | 045 — Rerank Blend is SSOT (AlwaysApply) | **Default-Apply** |
| 046 | `046-ci-hermetic-fallbacks.mdc` | 046 — Hermetic CI Fallbacks (AlwaysApply) | **Default-Apply** |
| 047 | `047-reserved.mdc` | reserved | **Default-Apply** |
| 048 | `048-reserved.mdc` | reserved | **Default-Apply** |
| 049 | `049-gpt5-contract-v5.2.mdc` | gpt5 contract v5.2 | **Default-Apply** |
| 050 | `050-ops-contract.mdc` | 🧭 Gemantria — OPS Contract v6.2.3 | **Always-Apply** |
| 051 | `051-cursor-insight.mdc` | 051 — Cursor Insight & Handoff (AlwaysApply) | **Always-Apply** |
| 052 | `052-tool-priority.mdc` | 052 — Tool Priority & Context Guidance (AlwaysApply) | **Always-Apply** |
| 053 | `053-idempotence.mdc` | 053 — Idempotent Baseline (OPS v6.2.1) | **Default-Apply** |
| 054 | `054-reuse-first.mdc` | Rule-054 — Reuse-First, No-Scaffold-When-Exists (AlwaysApply: true) | **Default-Apply** |
| 055 | `055-auto-docs-sync.mdc` | 055 — Auto-Docs Sync Pass (AlwaysApply) | **Default-Apply** |
| 056 | `056-ui-generation.mdc` | ui generation | **Default-Apply** |
| 057 | `057-embedding-consistency.mdc` | Rule 057 — EMBEDDING CONSISTENCY CI CHECKS (AlwaysApply) | **Default-Apply** |
| 058 | `058-auto-housekeeping.mdc` | Rule 058 — Auto-Housekeeping Post-Change (AlwaysApply) | **Default-Apply** |
| 059 | `059-context-persistence.mdc` | 059 — Context Persistence (AlwaysApply) | **Default-Apply** |
| 060 | `060-response-style.mdc` | Rule-060: Response Style | **Default-Apply** |
| 061 | `061-ai-learning-tracking.mdc` | Rule 061 — AI Learning Tracking (AlwaysApply: false, but recommended) | **Default-Apply** |
| 062 | `062-environment-validation.mdc` | Environment Validation (Always Required) | **Default-Apply** |
| 063 | `063-git-safety.mdc` | Git Safety (No Destructive Operations) | **Default-Apply** |
| 064 | `064-ai-tracking-contract.mdc` | ai tracking contract | **Default-Apply** |
| 065 | `065-auto-normalize.mdc` | Rule 065 — Auto-Normalize on Branch Switch & PR Events | **Default-Apply** |
| 066 | `066-lm-studio-appimage-update.mdc` | 066 — LM Studio AppImage Update & Dock Integration | **Default-Apply** |
| 067 | `067-atlas-webproof.mdc` | Rule 067 — Atlas Webproof (Browser-Verified UI) | **Default-Apply** |
| 068 | `068-gpt-docs-sync.mdc` | 068 — GPT Documentation Sync (AlwaysApply) | **Default-Apply** |
<!-- RULES_INVENTORY:END -->


> **RO DSN (tag builds)** — Either `GEMATRIA_RO_DSN` **or** `ATLAS_DSN_RO` satisfies the RO requirement.
> Exporters/runners must check **both** (peers) before falling back to `get_ro_dsn()`; fail-closed on tags.

> **Postgres Knowledge MCP (RFC-078):** Catalog-as-a-service lives in Postgres. Tag builds use RO DSN and must prove `mcp.v_catalog`. See `docs/runbooks/MCP_KNOWLEDGE_DB.md`.

> **Postgres Knowledge MCP (STRICT tags: RO proof):** tagproof runs `make guard.mcp.db.ro STRICT_DB_PROBE=1` to verify `mcp.v_catalog` via RO DSN; PR CI remains hermetic (no probes).

## pmagent repo — Repository Introspection Subsystem (NEW)

The `pmagent repo` command group provides read-only, DMS-aware introspection of the repository.
It implements three commands:

* **semantic-inventory**
  Produces a JSON inventory of all repo files, correlated with DMS-tracked paths.

* **reunion-plan**
  Labels repository directories as integration, quarantine, or investigate.
  Auto-runs semantic-inventory if needed.

* **quarantine-candidates**
  Identifies quarantine-eligible files under `archive/` and `logs/`.
  Auto-runs reunion-plan (and thus semantic-inventory) if needed.

All repo commands:

* Are **read-only**
* Only write JSON evidence to `evidence/repo/` (and optionally `share/exports/repo/`)
* Never modify repo files or DMS records
