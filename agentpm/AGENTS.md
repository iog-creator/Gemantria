# AGENTS.md - agentpm Package

## Directory Purpose

The `agentpm/` package contains the **Postgres-backed control plane and runtime services** that pmagent uses for:

- Database access and control-plane schemas (control + gematria)
- LM provider routing (Ollama + LM Studio) and AI interaction logging
- Graph exports, Atlas/HTML/dashboard helpers, and MCP knowledge integrations
- Guarded pipelines, metrics, and reality-check style verification

Subdirectories (e.g. `agentpm/db/`, `agentpm/control_plane/`, `agentpm/runtime/`, `agentpm/mcp/`) each have their own `AGENTS.md` for more detailed contracts.

## Postgres & AI Tracking Integration

- **DSNs & loaders**
  - All database access must go through centralized loaders:
    - `scripts.config.env.get_rw_dsn()` / `get_ro_dsn()` / `get_bible_db_dsn()`
    - `agentpm.db.loader.get_control_engine()` / `get_bible_engine()`
  - DSNs are resolved from environment (`GEMATRIA_DSN`, `ATLAS_DSN_RW`, `BIBLE_DB_DSN`, etc.); **no direct `os.getenv()` for DSNs**.
- **AI tracking tables (Rule-061/064 / AGENTS root contract)**
  - AI interaction and governance artifacts live in the `gematria` database:
    - `control.agent_run` - Runtime LM calls and tool executions (written by `agentpm.runtime.lm_logging._write_agent_run()`)
    - `control.agent_run_cli` - CLI command executions (written by `agentpm.control_plane.create_agent_run()` / `mark_agent_run_success()` / `mark_agent_run_error()`)
    - `public.ai_interactions` - Legacy/alternative AI tracking (if used)
    - `public.governance_artifacts` - Governance artifact tracking
  - **Writers:**
    - Runtime LM calls: `agentpm.runtime.lm_logging._write_agent_run()` writes to `control.agent_run` for all `lm_studio_chat_with_logging()` and `guarded_lm_call()` invocations
    - CLI commands: `agentpm.control_plane.create_agent_run()` creates `control.agent_run_cli` records; `mark_agent_run_success()` / `mark_agent_run_error()` update them
  - **DB-on vs DB-off semantics:**
    - **DB-on**: When `get_rw_dsn()` returns a valid DSN and `psycopg` is available, all tracking functions write to the database and return run IDs
    - **DB-off**: When DSN is unavailable, `psycopg` is missing, or DB write fails, all tracking functions return `None` gracefully (no exceptions raised)
    - This ensures CI and hermetic tests can run without database access
  - All writes are routed through centralized DSN loaders (`scripts.config.env.get_rw_dsn()`); never use `os.getenv()` directly
- **Control-plane exports**
  - Control-plane helpers in `agentpm.control_plane` read/write Postgres-backed views and exports (e.g. LM indicator, control status, tool catalog).
  - These exports are consumed by Atlas dashboards, pmagent CLI commands, and reality-check flows.

## Key Components (High-Level)

- **`agentpm/db/`**: DSN loaders, SQLAlchemy engines, and Postgres-specific helpers.
- **`agentpm/control_plane/`**: Control schema helpers (tables, sessions, exports, pipeline status).
- **`agentpm/runtime/`**: LM routing, budgeting, and logging into `public.ai_interactions` / `public.governance_artifacts`.
- **`agentpm/lm/` + `agentpm/adapters/`**: Provider routing for Ollama + LM Studio (chat, embeddings, rerankers, theology).
- **`agentpm/status/`**: System and LM status aggregation used by `/api/status/*` and pmagent status CLI.
  - **`agentpm/status/snapshot.py`**: Unified system snapshot helper (M3 + M4)
  - **`agentpm/status/eval_exports.py`**: Eval exports helpers for Phase-8/10 analytics (M4)
- **`agentpm/kb/`**: Knowledge-base document registry (KB-Reg:M1 + M2 + M6).
  - **`agentpm/kb/registry.py`**: KB document registry model (Pydantic), persistence helpers, `query_registry()` planning helper, and `analyze_freshness()` drift detector
  - **Purpose**: Track KB documents (AGENTS.md, SSOT docs, rules, etc.) with metadata (id, title, path, type, tags, owning subsystem, provenance, freshness)
  - **SSOT**: Registry entries live in `share/kb_registry.json` (read-only in CI per Rule-044)
  - **CLI**: `pmagent kb registry list/show/validate` commands for registry operations
  - **Snapshot integration (KB-Reg:M2)**: Registry summary included in `pm.snapshot` via `agentpm.status.snapshot.get_system_snapshot()` (advisory-only, non-gating)
  - **Planning helper (KB-Reg:M2)**: `query_registry()` provides read-only filter interface for future AgentPM planning flows
  - **Freshness tracking (KB-Reg:M6)**: Registry tracks document freshness (`last_seen_mtime`, `last_refreshed_at`, `min_refresh_interval_days`); `analyze_freshness()` detects stale/missing/out-of-sync docs; freshness summary included in `pmagent status kb` and `pmagent status.explain`; KB hints include `KB_DOC_STALE` and `KB_DOC_OUT_OF_SYNC` warnings (advisory-only); default refresh intervals: SSOT (30d), ADR (90d), AGENTS.md (14d), runbook (60d), rule (90d), changelog (7d), other (60d)
- **`agentpm/plan/`**: Planning workflows powered by KB registry (AgentPM-Next:M1).
  - **`agentpm/plan/kb.py`**: KB document worklist builder (`build_kb_doc_worklist()`) that produces prioritized documentation tasks from KB registry status and hints
  - **Purpose**: Provide deterministic, read-only planning surfaces for PM/AgentPM workflows
  - **CLI**: `pmagent plan kb` command returns prioritized worklist of documentation tasks (missing > stale > out_of_sync > low_coverage > info)
  - **Worklist structure**: Items grouped by subsystem, ordered by severity, with suggested actions for each task
  - **Hermetic**: No writes, no LM calls; purely interprets existing KB signals
- **`agentpm/reality/`**: Reality-check orchestrator helpers (`reality.check` verdicts).
- **`agentpm/atlas/` + `agentpm/exports/`**: Atlas/HTML/UI exports and graph/metrics helpers.
- **`agentpm/mcp/`**: Postgres-backed MCP catalog/knowledge integration.
- **`agentpm/tests/`**: Test suites for the above components.

See each subdirectory's `AGENTS.md` for more detailed contracts and test entry points.

## pm.snapshot Integration (AgentPM-First:M3 + M4)

**Purpose:** `pm.snapshot` (`make pm.snapshot` / `scripts/pm_snapshot.py`) generates a comprehensive PM-facing status snapshot that composes health, status explanation, reality-check, AI tracking, share manifest, and eval exports posture into a single operator-facing view.

**Implementation:**
- **Unified helper**: `agentpm.status.snapshot.get_system_snapshot()` — Single source of truth for system snapshot composition
- **Shared by**: `pm.snapshot` script and WebUI APIs (`/api/status/system`) for consistency
- **Components**: DB health, system health (DB + LM + Graph), status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10 exports), kb_registry (KB-Reg:M2)
- **Eval exports helpers**: `agentpm.status.eval_exports` — Shared helpers for reading Phase-8/10 eval export files (hermetic, tolerant of missing files)

**Inputs:**
- Environment variables: `BIBLE_DB_DSN`, `GEMATRIA_DSN`, `CHECKPOINTER`, `ENFORCE_STRICT` (via centralized loaders)
- Required guards: DB health guard, system health (DB + LM + Graph), status explanation, reality-check

**Outputs:**
- **Markdown snapshot**: `share/pm.snapshot.md` — Human-readable PM snapshot with all component statuses
- **JSON snapshot**: `evidence/pm_snapshot/snapshot.json` — Machine-readable comprehensive snapshot with:
  - `overall_ok`: Boolean indicating overall system health
  - `db_mode`: Database health mode (`ready`/`db_off`/`partial`)
  - `lm_mode`: LM health mode (`lm_ready`/`lm_off`/`unknown`)
  - `posture`: DSN posture and STRICT flags
  - `db_health`: DB health guard results
  - `system_health`: System health (DB + LM + Graph) aggregation
  - `status_explain`: Status explanation (plain-language summary)
  - `reality_check`: Reality-check verdict (HINT mode)
  - `ai_tracking`: AI tracking summary (control.agent_run and control.agent_run_cli counts)
  - `share_manifest`: Share manifest summary (file count and status)
  - `eval_insights`: Eval exports summary (Phase-8/10) — **advisory only, export-driven analytics**:
    - `lm_indicator`: LM indicator export summary (from `share/atlas/control_plane/lm_indicator.json`)
    - `db_health`: DB health snapshot (from `evidence/pm_snapshot/db_health.json`)
    - `edge_class_counts`: Edge class counts (from `share/eval/edges/edge_class_counts.json`)
    - Each export includes `available` flag and `note` if missing/invalid
  - `kb_registry`: KB registry summary (KB-Reg:M2) — **advisory only, read-only in CI**:
    - `available`: Whether registry file exists
    - `total`: Total number of registered documents
    - `valid`: Whether registry validation passed
    - `errors_count`: Number of validation errors
    - `warnings_count`: Number of validation warnings
    - Does NOT affect `overall_ok` (advisory-only, non-gating)
- **DB health JSON** (backward compatibility): `evidence/pm_snapshot/db_health.json`

**Usage:**
- **Local operator command**: `make pm.snapshot` — Run after bring-up or DSN changes to generate current system posture snapshot
- **CI usage**: CI may run `pm.snapshot` but should not fail if DB/LM are offline (hermetic behavior)
- **WebUI APIs**: `/api/status/system` uses the same unified snapshot helper (with optional components for backward compatibility)

**Relation to other commands:**
- **Composes**: `pmagent health system` (DB + LM + Graph), `pmagent status explain` (plain-language explanation), `pmagent status kb` (KB registry status view, KB-Reg:M3b), `pmagent reality-check check --mode hint` (comprehensive validation)
- **Surfaces**: AI tracking posture (control.agent_run and control.agent_run_cli table counts), share manifest posture (SHARE_MANIFEST.json file count and status), eval exports posture (Phase-8/10 analytics), KB registry posture (KB-Reg:M2 + M3b, advisory-only)
- **Behavior**: DB-off/LM-off modes degrade gracefully to clear HINTs and explicit mode indicators; snapshot is still produced with all available information (hermetic behavior for CI/testing)
- **Eval insights**: Eval exports are **advisory only** and do NOT affect `overall_ok`; they provide analytics context but system health is determined by the core health components (DB, LM, Graph, reality-check)
- **KB registry**: KB registry summary is **advisory only** and does NOT affect `overall_ok`; it provides document registry context but system health is determined by the core health components (DB, LM, Graph, reality-check); registry is read-only in CI per Rule-044
- **KB hints (KB-Reg:M4 + M6)**: KB registry health is surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`; hints include missing docs, low coverage subsystems, validation issues, stale docs (`KB_DOC_STALE`), and out-of-sync docs (`KB_DOC_OUT_OF_SYNC`); all hints are advisory-only and never affect `overall_ok`
- **WebUI alignment**: WebUI status pages (`/status`, `/dashboard`, `/lm-insights`, `/db-insights`) consume the same snapshot data via `/api/status/system` and related endpoints; eval data is clearly labeled as "advisory analytics" and does not override health gates

## API Contracts (Top-Level)

- pmagent CLI subcommands (e.g. `pmagent health *`, `pmagent status *` including `pmagent status kb` for KB registry status view, `pmagent reality-check check`) are thin wrappers over `agentpm.*` modules.
- All top-level behaviors must:
  - Use centralized env/DSN loaders.
  - Treat DB-off / LM-off as **first-class modes** (never crash; emit structured `mode` + `ok` flags instead).
  - Persist AI tracking records (when DB is available) via the runtime/logging layer.

## Testing Strategy

- Primary tests live under `agentpm/tests/` and are invoked via:

  ```bash
  pytest -q agentpm/tests
  ```

- Additional end-to-end coverage comes from:
  - `pmagent` CLI tests (e.g. `agentpm/tests/cli/`)
  - Atlas/UI tests (e.g. `agentpm/tests/atlas/`, `tests/ui/*`)
  - Guard, MCP, and system status tests.

## Development Guidelines

- **DSN & Postgres**
  - Never hard-code DSNs; always use `scripts.config.env` or `agentpm.db.loader`.
  - Respect DB-off modes; raise `DbUnavailableError` or return structured `mode="db_off"` instead of crashing.
- **LM & providers**
  - Use the centralized LM model config (`scripts.config.env.get_lm_model_config()`).
  - Theology slot is served by LM Studio (`THEOLOGY_MODEL=Christian-Bible-Expert-v2.0-12B`) when enabled; other slots may use Ollama Granite per env.
  - For detailed prompt templates and MoE-of-MoEs routing roles (Granite 4.0 + BGE-M3 + Granite Reranker), refer to `Prompting Guide for Our Core LLM models.md` (design-level; not all models are wired yet).
- **AI tracking**
  - All LM calls should be logged through `agentpm.runtime.lm_logging` helpers when DB is available:
    - `lm_studio_chat_with_logging()` automatically logs to `control.agent_run` via `_write_agent_run()`
    - `guarded_lm_call()` logs budget violations and successful LM calls to `control.agent_run`
  - All pmagent CLI commands should use `agentpm.control_plane.create_agent_run()` and `mark_agent_run_success()` / `mark_agent_run_error()` to track command executions in `control.agent_run_cli`
  - Logging must **no-op cleanly** when DB is unavailable (CI/hermetic mode): all tracking functions return `None` without raising exceptions
- **Docs & governance**
  - Keep this file and subdirectory `AGENTS.md` files in sync with behavior changes.
  - Run `make housekeeping` (or at least `make share.sync governance.housekeeping`) after changes to ensure docs and share/ are updated.

## Related ADRs / Rules

| Component/Function                   | Related ADRs / Rules                         |
|-------------------------------------|----------------------------------------------|
| DB loaders, control-plane schemas   | ADR-065 (Postgres SSOT), Rule-001, Rule-043  |
| AI tracking tables & runtime logging| Rule-061, Rule-064, ADR-066                 |
| LM routing (Ollama + LM Studio)     | ADR-066, LM Studio + Ollama runbooks        |
| Reality-check & system status       | ADR-058 (GPT System Prompt), Rule-050/051   |


