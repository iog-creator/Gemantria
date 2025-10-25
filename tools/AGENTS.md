# AGENTS.md — Tools (Headless Orchestration & Smoke Tests)

## Purpose

Define the tooling used to orchestrate LM Studio in headless mode, enforce fail-fast gates, and verify readiness via smoke tests before running the pipeline.

## Components

- tools/lm_bootstrap_strict.py — Resolve LM Studio CLI (lms) strictly (no UI fallback). Fails if not found.
- tools/genesis_autopilot.py — Headless orchestrator. Starts servers, audits models, smokes embeddings, runs shard, asserts no UI server.
- tools/smoke_lms_embeddings.py — Verifies /v1/embeddings liveness and dimensionality.
- tools/smoke_lms_models.py — Audits active model IDs and GGUF quants.

## Contracts & Env

- LM_CLI: Absolute path to lms; resolved by lm_bootstrap_strict.py.
- EMBED_URL: http://127.0.0.1:9994/v1 (default) — used by embeddings proxy.
- LM_STUDIO_HOST: Base URL for lmstudio_client chat/emb health (Rule 011).
- USE_MOCKS=0, USE_QWEN_EMBEDDINGS=true — enforced for production runs.

## Behavior (Rule References)

- Rule 000/011 Production Safety: Qwen Live Gate must pass; fail-closed if chat or embedding checks fail.
- Rule 003 Graph & Batch: Autopilot runs shard with batch-size and gates; aborts on violations.
- Rule 006 Agents Governance: Tools must be documented; changes require docs sync.
- Rule 027 Docs Sync Gate: Any tooling changes update this AGENTS.md and related docs.

## Usage

```bash
python tools/genesis_autopilot.py Genesis --batch 10
```

Autopilot will:

- Start headless servers on 9994/9991/9993
- Audit /v1/models and GGUF quants
- Smoke /v1/embeddings (dim check)
- Run graph shard; assert SQL sanity

### LM Studio Port Split (Env-only)

- Embeddings: `EMBED_URL=http://127.0.0.1:9994/v1`
- Chat/Live Gate: `LM_STUDIO_HOST=http://127.0.0.1:9994` (or `:9991` when chat lives there)
- Critic (optional): `:9993`

Make targets:

```bash
make models.verify   # Verify endpoints and models
make models.swap     # Test alt answerer model
make models.params   # Show recommended runtime knobs
```
