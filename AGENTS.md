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
- Checkpointer: `CHECKPOINTER=postgres|memory` (default: memory for CI/dev)
- LLM: LM Studio only when enabled; confidence is metadata only.
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

## Operations

### Evaluation
* **Phase-8 local eval**: `make eval.smoke` runs a non-CI smoke to validate the eval harness. Do not wire into CI or `make go` until stabilized. Governance gates (037/038, share no-drift, NEXT_STEPS) remain unchanged.

## Rules (summary)
- Normalize Hebrew: **NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC**
- Mispar Hechrachi; finals=regular. Surface-form gematria with calc strings.
- Ketiv primary; variants recorded with `variant_type`; store span_start/end for instances.
- Batches default to 50; abort + `review.ndjson` on failure; `ALLOW_PARTIAL=1` override logs manifest.
- Default edges: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags.
- Layouts persisted with (algorithm, params_json, seed, version). New params → new layout id.
- Checkpointer: `CHECKPOINTER=postgres|memory` (memory default); Postgres requires `GEMATRIA_DSN`.
- GitHub operations: Use MCP server for issues/PRs/search; confirm ownership; search before creating; use Copilot for AI tasks.

## How agents should use rules

* Global constraints live in `.cursor/rules/000-always-apply.mdc`.
* Path-scoped rules auto-attach via `globs`.
* One-off procedures live as agent-requested rules (invoke by referencing their `description` in the prompt).
* Any change to rules affecting workflows must update this AGENTS.md and ADRs in the same PR.
