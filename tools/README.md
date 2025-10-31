# Tools — Headless Orchestration & Smoke Tests

## Overview

This directory contains automation for running LM Studio in headless mode, validating endpoints, and orchestrating the pipeline shard run.

## Files

- lm_bootstrap_strict.py — Strictly resolves lms CLI, no UI fallback.
- genesis_autopilot.py — Start servers, audit models/quants, smoke embeddings, run shard.
- smoke_lms_embeddings.py — Calls /v1/embeddings and validates dimension.
- smoke_lms_models.py — Audits /v1/models and GGUF quant hints.

## Usage

```bash
python tools/genesis_autopilot.py Genesis --batch 10
```

Env (examples):

```bash
export USE_MOCKS=0 USE_QWEN_EMBEDDINGS=true
export EMBED_URL=http://127.0.0.1:9994/v1
export LM_STUDIO_HOST=http://127.0.0.1:9991
```

Expected:
- Embeddings smoke prints OK with dim.
- Qwen Live Gate passes if chat is available at LM_STUDIO_HOST.
