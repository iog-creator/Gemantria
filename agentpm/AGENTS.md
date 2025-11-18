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
- **AI tracking tables (Rule-064 / AGENTS root contract)**
  - AI interaction and governance artifacts live in the `gematria` database:
    - `public.ai_interactions`
    - `public.governance_artifacts`
  - Writers are implemented via `agentpm.runtime.lm_logging` (and related runtime helpers).
  - All writes are routed through the Postgres checkpointer / loaders; DB-off mode must fail closed or no-op hermetically.
- **Control-plane exports**
  - Control-plane helpers in `agentpm.control_plane` read/write Postgres-backed views and exports (e.g. LM indicator, control status, tool catalog).
  - These exports are consumed by Atlas dashboards, pmagent CLI commands, and reality-check flows.

## Key Components (High-Level)

- **`agentpm/db/`**: DSN loaders, SQLAlchemy engines, and Postgres-specific helpers.
- **`agentpm/control_plane/`**: Control schema helpers (tables, sessions, exports, pipeline status).
- **`agentpm/runtime/`**: LM routing, budgeting, and logging into `public.ai_interactions` / `public.governance_artifacts`.
- **`agentpm/lm/` + `agentpm/adapters/`**: Provider routing for Ollama + LM Studio (chat, embeddings, rerankers, theology).
- **`agentpm/status/`**: System and LM status aggregation used by `/api/status/*` and pmagent status CLI.
- **`agentpm/reality/`**: Reality-check orchestrator helpers (`reality.check` verdicts).
- **`agentpm/atlas/` + `agentpm/exports/`**: Atlas/HTML/UI exports and graph/metrics helpers.
- **`agentpm/mcp/`**: Postgres-backed MCP catalog/knowledge integration.
- **`agentpm/tests/`**: Test suites for the above components.

See each subdirectory’s `AGENTS.md` for more detailed contracts and test entry points.

## API Contracts (Top-Level)

- pmagent CLI subcommands (e.g. `pmagent health *`, `pmagent status *`, `pmagent reality-check check`) are thin wrappers over `agentpm.*` modules.
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
- **AI tracking**
  - All LM calls should be logged through `agentpm.runtime` helpers when DB is available.
  - Logging must **no-op cleanly** when DB is unavailable (CI/hermetic mode).
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


