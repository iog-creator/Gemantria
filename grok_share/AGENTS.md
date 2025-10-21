# AGENTS.md — Gemantria Agent Framework

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1) Correctness: **Code gematria > bible_db > LLM (LLM = metadata only)**.
2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.
3) Safety: **bible_db is READ-ONLY**; parameterized SQL only; **fail-closed if <50 nouns** (ALLOW_PARTIAL=1 is explicit).

## Environment
- venv: `python -m venv .venv && source .venv/bin/activate`
- install: `make deps`
- Databases:
  - `BIBLE_DB_DSN` — read-only Bible database (RO adapter denies writes pre-connection)
  - `GEMATRIA_DSN` — read/write application database
- Batch & overrides:
  - `BATCH_SIZE=50` (default noun batch size)
  - `ALLOW_PARTIAL=0|1` (if 1, manifest must capture reason)
  - `PARTIAL_REASON=<string>` (required when ALLOW_PARTIAL=1)
### Checkpointer / Orchestration
- `CHECKPOINTER=memory|postgres` (default: memory)
- `GEMATRIA_DSN` — required when `CHECKPOINTER=postgres`
- `WORKFLOW_ID` — defaults to `gemantria.v1`
- `METRICS_ENABLED=1` — enables Postgres metrics sink; `0` disables DB writes (stdout remains)
- `LOG_LEVEL=INFO` — controls JSON logger verbosity

- LLM: LM Studio with Qwen3 models for semantic intelligence. Requires `THEOLOGY_MODEL`, `MATH_MODEL`, `QWEN_EMBEDDING_MODEL`, `QWEN_RERANKER_MODEL` for inference. `USE_QWEN_EMBEDDINGS=true` enables real semantic vectors.
- Metrics: stdout JSON + Postgres sink (metrics_log). Fail-open (never block pipeline).
- Observability (Phase 2 baseline):
  - Postgres views: `v_node_latency_7d`, `v_node_throughput_24h`, `v_recent_errors_7d`, `v_pipeline_runs`.
  - Materialized view: `mv_node_latency_7d`; refresh via `SELECT refresh_metrics_materialized();`.
  - Optional OpenMetrics exporter: set `PROM_EXPORTER_ENABLED=1` to serve `/metrics` (port `PROM_EXPORTER_PORT`).
  - Dashboards must use SQL views (no ad-hoc heavy queries in UI).
- GitHub: MCP server active for repository operations (issues, PRs, search, Copilot integration).

## Workflow (small green PRs)
- Branch `feature/<short>` → **write tests first** → code → `make lint type test.unit test.int coverage.report` → commit → push → PR.
- Coverage ≥98%.
- Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`
- PR: Goal, Files, Tests, Acceptance.

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

### Runbook: Metrics & Logging
1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/003_metrics_logging.sql
   ```
2. Verify locally:
   ```bash
   export METRICS_ENABLED=1
   export LOG_LEVEL=INFO
   export WORKFLOW_ID=gemantria.v1
   make lint type test.unit test.integration coverage.report
   ```
3. Expected: JSON logs to stdout, metrics rows in DB when enabled, pipeline unaffected by metrics failures.

### Runbook: Observability Dashboards
1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/004_metrics_views.sql
   ```
2. Verify locally:
   ```bash
   export PROM_EXPORTER_ENABLED=0  # Optional exporter disabled by default
   export PROM_EXPORTER_PORT=9108
   make lint type test.unit test.integration coverage.report
   ```
3. Expected: SQL views created, queries return data when metrics exist, exporter optional.

### Runbook: LLM Integration
1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/005_ai_metadata.sql
   ```
2. Configure LM Studio:
   ```bash
   export LM_STUDIO_HOST=http://127.0.0.1:1234
   export THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
   export MATH_MODEL=self-certainty-qwen3-1.7b-base-math
   export LM_STUDIO_MOCK=false  # Set to true for testing without LM Studio
   ```
3. Verify locally:
   ```bash
   make lint type test.unit test.integration coverage.report
   ```
4. Expected: AI enrichment node integrates with pipeline, confidence scores stored in `ai_enrichment_log`, fallback to mock mode when LM Studio unavailable.

### Runbook: Semantic Network & Qwen Integration
1. Apply migrations:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/007_concept_network.sql
   psql "${GEMATRIA_DSN}" -f migrations/008_add_concept_network_constraints.sql
   ```
2. Configure Qwen models:
   ```bash
   export USE_QWEN_EMBEDDINGS=true
   export QWEN_EMBEDDING_MODEL=qwen-embed
   export QWEN_RERANKER_MODEL=qwen-reranker
   export LM_STUDIO_HOST=http://127.0.0.1:1234
   ```
3. Verify locally:
   ```bash
   make lint type test.unit test.integration coverage.report
   ```
4. Expected: Network aggregator generates 1024-dim embeddings, stores in `concept_network`, computes similarity relationships, and updates reports with network metrics.

## Rules (summary)
- Normalize Hebrew: **NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC**
- Mispar Hechrachi; finals=regular. Surface-form gematria with calc strings.
- Ketiv primary; variants recorded with `variant_type`; store span_start/end for instances.
- Batches default to 50; abort + `review.ndjson` on failure; `ALLOW_PARTIAL=1` override logs manifest.
- Default edges: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags.
- Layouts persisted with (algorithm, params_json, seed, version). New params → new layout id.
- Checkpointer: `CHECKPOINTER=postgres|memory` (memory default); Postgres requires `GEMATRIA_DSN`.
- LLM Integration: LM Studio with Qwen3 models; confidence scores are metadata only (never affect core gematria); `USE_QWEN_EMBEDDINGS=true` enables real semantic vectors; mock mode available for testing.
- Semantic Network: pgvector embeddings (1024-dim, L2 normalized) with cosine similarity; strong edges ≥0.90, weak edges ≥0.75; Qwen3 inference for relationship discovery.
- GitHub operations: Use MCP server for issues/PRs/search; confirm ownership; search before creating; use Copilot for AI tasks.

## How agents should use rules

* Global constraints live in `.cursor/rules/000-always-apply.mdc`.
* Path-scoped rules auto-attach via `globs`.
* One-off procedures live as agent-requested rules (invoke by referencing their `description` in the prompt).
* Any change to rules affecting workflows must update this AGENTS.md and ADRs in the same PR.
